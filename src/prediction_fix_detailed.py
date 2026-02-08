# PREDICTION FIX - Stop Always Using Fallback
# This file fixes the ML predictor to actually work

"""
DIAGNOSIS: Why predictions always use fallback
1. get_coin_history() might not be returning proper data
2. Technical indicator calculations might be failing
3. Model might not be saving/loading properly

SOLUTION: Add detailed logging and fix data pipeline
"""

# ==================== FIX 1: Enhanced get_coin_history ====================
def get_coin_history_FIXED(self, coin_id: str, days: int = 90):
    """
    FIXED version with detailed logging
    Add this to your EnhancedCryptoAPIHandler class
    """
    try:
        print(f"\n{'='*60}")
        print(f"FETCHING HISTORY FOR: {coin_id}")
        print(f"Days requested: {days}")
        print(f"{'='*60}")
        
        import pandas as pd
        from datetime import datetime
        
        if hasattr(self, '_rate_limit'):
            self._rate_limit()
        else:
            time.sleep(1)
        
        # Get market chart data
        market_chart = self.cg.get_coin_market_chart_by_id(
            id=coin_id,
            vs_currency='usd',
            days=days
        )
        
        if not market_chart or 'prices' not in market_chart:
            print("❌ No market chart data received")
            return None
        
        print(f"✓ Received {len(market_chart['prices'])} price points")
        
        # Create DataFrame
        prices_df = pd.DataFrame(
            market_chart['prices'],
            columns=['timestamp', 'close']
        )
        prices_df['timestamp'] = pd.to_datetime(prices_df['timestamp'], unit='ms')
        
        # Add volume
        if 'total_volumes' in market_chart:
            volumes_df = pd.DataFrame(
                market_chart['total_volumes'],
                columns=['timestamp', 'volume']
            )
            volumes_df['timestamp'] = pd.to_datetime(volumes_df['timestamp'], unit='ms')
            
            df = pd.merge_asof(
                prices_df.sort_values('timestamp'),
                volumes_df.sort_values('timestamp'),
                on='timestamp',
                direction='nearest'
            )
        else:
            df = prices_df
            df['volume'] = 0
        
        print(f"✓ Created base DataFrame with {len(df)} rows")
        
        # Create OHLC from close prices
        # Group by hour for more data points
        df['hour'] = df['timestamp'].dt.floor('H')
        
        hourly = df.groupby('hour').agg({
            'close': ['first', 'max', 'min', 'last'],
            'volume': 'sum',
            'timestamp': 'first'
        }).reset_index()
        
        hourly.columns = ['hour', 'open', 'high', 'low', 'close', 'volume', 'timestamp']
        result = hourly[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
        
        print(f"✓ Created OHLC data with {len(result)} rows")
        print(f"✓ Columns: {list(result.columns)}")
        print(f"✓ Date range: {result['timestamp'].min()} to {result['timestamp'].max()}")
        print(f"✓ Sample close prices: {result['close'].head(3).tolist()}")
        print(f"{'='*60}\n")
        
        return result
        
    except Exception as e:
        print(f"❌ ERROR in get_coin_history: {e}")
        import traceback
        traceback.print_exc()
        return None


# ==================== FIX 2: Enhanced Predictor with Logging ====================
def predict_price_FIXED(self, coin_id: str, current_price: float, time_frame: int = 1):
    """
    FIXED prediction method with detailed logging
    Replace the predict_price method in AdvancedPricePredictor
    """
    try:
        print(f"\n{'='*60}")
        print(f"PREDICTION REQUEST")
        print(f"Coin: {coin_id}")
        print(f"Current Price: ${current_price:,.2f}")
        print(f"Time Frame: {time_frame} days")
        print(f"{'='*60}")
        
        # Get historical data
        days = max(time_frame * 30, 90)
        print(f"→ Fetching {days} days of historical data...")
        
        df = self.api.get_coin_history(coin_id, days=days)
        
        if df is None:
            print("❌ get_coin_history returned None")
            return self._fallback_prediction(current_price, time_frame)
        
        print(f"✓ Received DataFrame with {len(df)} rows")
        
        if len(df) < 30:
            print(f"❌ Insufficient data: {len(df)} rows (need 30+)")
            return self._fallback_prediction(current_price, time_frame)
        
        # Prepare features
        print(f"→ Calculating technical indicators...")
        X, y = self.prepare_features(df)
        
        if len(X) == 0:
            print("❌ prepare_features returned empty array")
            return self._fallback_prediction(current_price, time_frame)
        
        print(f"✓ Features prepared: {X.shape[0]} samples, {X.shape[1]} features")
        
        # Check if we need to train
        model_path = os.path.join(self.model_dir, f"{coin_id}_model.joblib")
        scaler_path = os.path.join(self.model_dir, f"{coin_id}_scaler.joblib")
        
        if coin_id not in self.models and not os.path.exists(model_path):
            print(f"→ No existing model found, training new model...")
            success, message = self.train_ensemble_model(coin_id, days=days)
            
            if not success:
                print(f"❌ Training failed: {message}")
                return self._fallback_prediction(current_price, time_frame)
            
            print(f"✓ Model trained successfully")
        
        # Load model if needed
        if coin_id not in self.models:
            print(f"→ Loading model from disk...")
            try:
                import joblib
                models_dict = joblib.load(model_path)
                scaler = joblib.load(scaler_path)
                self.models[coin_id] = {"models": models_dict, "scaler": scaler}
                print(f"✓ Model loaded successfully")
            except Exception as e:
                print(f"❌ Model loading failed: {e}")
                return self._fallback_prediction(current_price, time_frame)
        
        # Make prediction
        print(f"→ Making prediction...")
        
        latest_features = X[-1].reshape(1, -1)
        scaler = self.models[coin_id]["scaler"]
        latest_scaled = scaler.transform(latest_features)
        
        # Ensemble prediction
        predictions = []
        model_weights = {"rf": 0.6, "gb": 0.4}
        
        for model_name, weight in model_weights.items():
            if model_name in self.models[coin_id]["models"]:
                model = self.models[coin_id]["models"][model_name]
                pred = model.predict(latest_scaled)[0]
                predictions.append(pred * weight)
                print(f"  {model_name.upper()}: {pred:.2f}% (weight: {weight})")
        
        if not predictions:
            print("❌ No models available for prediction")
            return self._fallback_prediction(current_price, time_frame)
        
        predicted_change = sum(predictions)
        
        # Adjust for time frame
        time_frame_adjustment = 1.0
        if time_frame == 7:
            time_frame_adjustment = 1.5
        elif time_frame == 30:
            time_frame_adjustment = 2.0
        
        predicted_change *= time_frame_adjustment
        
        print(f"  Raw prediction: {sum(predictions):.2f}%")
        print(f"  Time adjustment: {time_frame_adjustment}x")
        print(f"  Final prediction: {predicted_change:.2f}%")
        
        # Calculate results
        predicted_price = current_price * (1 + predicted_change / 100)
        
        recent_volatility = df["close"].pct_change().std() * 100
        confidence = max(0, 100 - recent_volatility * 2 - time_frame * 2)
        confidence = min(confidence, 95)
        
        direction = "bullish" if predicted_change > 0 else "bearish"
        strength = (
            "strong" if abs(predicted_change) > 5
            else "moderate" if abs(predicted_change) > 2
            else "weak"
        )
        
        insights = self._generate_insights(df, predicted_change, time_frame)
        
        print(f"✓ PREDICTION COMPLETE")
        print(f"  Predicted Price: ${predicted_price:,.2f}")
        print(f"  Change: {predicted_change:+.2f}%")
        print(f"  Direction: {direction} ({strength})")
        print(f"  Confidence: {confidence:.1f}%")
        print(f"{'='*60}\n")
        
        return {
            "current_price": current_price,
            "predicted_price": predicted_price,
            "predicted_change_percent": predicted_change,
            "confidence_score": confidence,
            "direction": direction,
            "strength": strength,
            "time_frame": time_frame,
            "timestamp": datetime.now(),
            "insights": insights,
            "is_fallback": False,
        }
        
    except Exception as e:
        print(f"❌ PREDICTION ERROR: {e}")
        import traceback
        traceback.print_exc()
        print(f"{'='*60}\n")
        return self._fallback_prediction(current_price, time_frame)


# ==================== FIX 3: Import statement ====================
import os
import joblib


print("""
====================================================================
PREDICTOR FIX GUIDE
====================================================================

STEP 1: Fix API Handler
------------------------
In api_handler.py, REPLACE the get_coin_history method with:
  get_coin_history_FIXED (from above)

STEP 2: Fix Predictor
----------------------
In improved_price_predictor.py, REPLACE the predict_price method with:
  predict_price_FIXED (from above)

STEP 3: Ensure Imports
-----------------------
At the top of improved_price_predictor.py, make sure you have:
  import os
  import joblib
  from datetime import datetime

STEP 4: Test
------------
Run a prediction and watch the console output. You should see:
  - Detailed logging of each step
  - Number of data points fetched
  - Feature calculation results
  - Model training/loading status
  - Actual prediction values (NOT fallback message)

TROUBLESHOOTING:
----------------
If you still see fallback:
1. Check console output - it will tell you EXACTLY where it fails
2. Verify pycoingecko is installed: pip install pycoingecko
3. Verify sklearn is installed: pip install scikit-learn
4. Verify pandas is installed: pip install pandas

If technical indicators fail:
  pip install ta

The detailed logging will show you the exact problem!
====================================================================
""")
