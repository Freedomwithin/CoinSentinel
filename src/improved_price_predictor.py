# src/improved_price_predictor.py - Enhanced version with advanced ML techniques

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from sklearn.ensemble import (
    RandomForestRegressor,
    GradientBoostingRegressor,
    StackingRegressor,
    HistGradientBoostingRegressor,
)
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error
import warnings

warnings.filterwarnings("ignore")

# Try to import technical analysis library
try:
    import ta

    HAS_TA = True
except ImportError:
    HAS_TA = False
    print("Warning: 'ta' library not installed. Technical indicators will be limited.")

import joblib
import os
from typing import Dict, Tuple, Optional


class AdvancedPricePredictor:
    def __init__(self, api_handler):
        self.api = api_handler
        self.models = {}
        self.scalers = {}
        self.model_dir = "models"
        os.makedirs(self.model_dir, exist_ok=True)

    def calculate_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate technical indicators"""
        df = df.copy()

        # Price features
        df["returns"] = df["close"].pct_change()
        df["log_returns"] = np.log(df["close"] / df["close"].shift(1))

        # Moving averages
        df["sma_7"] = df["close"].rolling(window=7, min_periods=1).mean()
        df["sma_14"] = df["close"].rolling(window=14, min_periods=1).mean()
        df["sma_30"] = df["close"].rolling(window=30, min_periods=1).mean()
        df["ema_7"] = df["close"].ewm(span=7, adjust=False).mean()
        df["ema_14"] = df["close"].ewm(span=14, adjust=False).mean()

        if HAS_TA:
            # Momentum indicators (only if ta library is available)
            try:
                df["rsi"] = ta.momentum.RSIIndicator(df["close"], window=14).rsi()
                macd = ta.trend.MACD(df["close"])
                df["macd"] = macd.macd()
                df["macd_signal"] = macd.macd_signal()
                df["macd_diff"] = macd.macd_diff()

                # Volatility
                bb = ta.volatility.BollingerBands(df["close"], window=20, window_dev=2)
                df["bb_upper"] = bb.bollinger_hband()
                df["bb_lower"] = bb.bollinger_lband()
                df["bb_width"] = bb.bollinger_wband()

                # Stochastic Oscillator
                stoch = ta.momentum.StochasticOscillator(
                    df["high"], df["low"], df["close"], window=14, smooth_window=3
                )
                df["stoch_k"] = stoch.stoch()
                df["stoch_d"] = stoch.stoch_signal()

                # CCI
                df["cci"] = ta.trend.CCIIndicator(
                    df["high"], df["low"], df["close"], window=20
                ).cci()

            except Exception as e:
                print(f"Error calculating TA indicators: {e}")
                # Fill with default values
                self._fill_default_ta_values(df)
        else:
            # Simple alternatives without ta library
            self._fill_default_ta_values(df)

        df["volatility"] = df["close"].rolling(window=20, min_periods=1).std()

        # Volume indicators
        if "volume" in df.columns:
            df["volume_sma"] = df["volume"].rolling(window=20, min_periods=1).mean()
            df["volume_ratio"] = df["volume"] / df["volume_sma"]
            df["price_volume_corr"] = (
                df["close"].rolling(window=20, min_periods=1).corr(df["volume"])
            )
        else:
            df["volume_sma"] = 0
            df["volume_ratio"] = 1
            df["price_volume_corr"] = 0

        # Price position
        df["high_20"] = (
            df["high"].rolling(window=20, min_periods=1).max()
            if "high" in df.columns
            else df["close"]
        )
        df["low_20"] = (
            df["low"].rolling(window=20, min_periods=1).min()
            if "low" in df.columns
            else df["close"]
        )
        df["price_position"] = (df["close"] - df["low_20"]) / (
            df["high_20"] - df["low_20"] + 0.0001
        )

        # Rate of change
        df["roc_7"] = (
            (df["close"] - df["close"].shift(7)) / (df["close"].shift(7) + 0.0001)
        ) * 100
        df["roc_14"] = (
            (df["close"] - df["close"].shift(14)) / (df["close"].shift(14) + 0.0001)
        ) * 100

        # Target: future price change (next period)
        df["target"] = (
            (df["close"].shift(-1) - df["close"]) / (df["close"] + 0.0001)
        ) * 100

        # Drop NaN values
        df = df.dropna()

        return df

    def _fill_default_ta_values(self, df):
        """Fill default values for TA indicators if calculation fails or lib missing"""
        df["rsi"] = 50  # Neutral RSI
        df["macd"] = 0
        df["macd_signal"] = 0
        df["macd_diff"] = 0
        df["bb_upper"] = df["close"] * 1.1
        df["bb_lower"] = df["close"] * 0.9
        df["bb_width"] = df["close"] * 0.2
        df["stoch_k"] = 50
        df["stoch_d"] = 50
        df["cci"] = 0

    def prepare_features(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare features and target for training"""
        df = self.calculate_technical_indicators(df)

        # Feature columns (all technical indicators)
        feature_cols = [
            "returns",
            "log_returns",
            "sma_7",
            "sma_14",
            "sma_30",
            "ema_7",
            "ema_14",
            "rsi",
            "macd",
            "macd_signal",
            "macd_diff",
            "bb_upper",
            "bb_lower",
            "bb_width",
            "volatility",
            "volume_ratio",
            "price_volume_corr",
            "price_position",
            "roc_7",
            "roc_14",
            "stoch_k",
            "stoch_d",
            "cci",
        ]

        # Ensure all feature columns exist
        existing_features = [col for col in feature_cols if col in df.columns]

        X = df[existing_features].values
        y = df["target"].values if "target" in df.columns else None

        return X, y

    def train_ensemble_model(self, coin_id: str, days: int = 90):
        """Train ensemble model for a specific coin using Stacking"""
        try:
            # Fetch historical data
            df = self.api.get_coin_history(coin_id, days=days)
            if df is None or len(df) < 30:
                return False, "Insufficient data"

            # Prepare features
            X, y = self.prepare_features(df)

            if len(X) < 20 or y is None:
                return False, "Not enough data for training"

            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )

            # Scale features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)

            # Base estimators
            estimators = [
                (
                    "rf",
                    RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1),
                ),
                (
                    "gb",
                    GradientBoostingRegressor(n_estimators=100, random_state=42),
                ),
                (
                    "hgb",
                    HistGradientBoostingRegressor(random_state=42),
                ),
            ]

            # Stacking Regressor
            stacking_regressor = StackingRegressor(
                estimators=estimators, final_estimator=Ridge()
            )

            stacking_regressor.fit(X_train_scaled, y_train)

            # Predict on test set
            y_pred = stacking_regressor.predict(X_test_scaled)

            # Calculate metrics
            mae = mean_absolute_error(y_test, y_pred)
            rmse = np.sqrt(mean_squared_error(y_test, y_pred))

            # Save models and scaler
            model_path = os.path.join(self.model_dir, f"{coin_id}_model.joblib")
            scaler_path = os.path.join(self.model_dir, f"{coin_id}_scaler.joblib")

            joblib.dump(stacking_regressor, model_path)
            joblib.dump(scaler, scaler_path)

            # Update cache
            self.models[coin_id] = {
                "ensemble_mae": mae,
                "ensemble_rmse": rmse,
                "model": stacking_regressor,
                "last_trained": datetime.now(),
                "days_trained": days,
                "scaler": scaler,
            }

            return (
                True,
                f"Model trained. MAE: {mae:.4f}, RMSE: {rmse:.4f}",
            )

        except Exception as e:
            print(f"Training error: {e}")
            return False, f"Training error: {str(e)}"

    def predict_price(self, coin_id: str, current_price: float, time_frame: int = 1):
        """
        FIXED prediction method with detailed logging
        """
        try:
            print(f"\\n{'='*60}")
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

                    model = joblib.load(model_path)
                    scaler = joblib.load(scaler_path)
                    self.models[coin_id] = {"model": model, "scaler": scaler}
                    print(f"✓ Model loaded successfully")
                except Exception as e:
                    print(f"❌ Model loading failed: {e}")
                    return self._fallback_prediction(current_price, time_frame)

            # Make prediction
            print(f"→ Making prediction...")

            latest_features = X[-1].reshape(1, -1)
            scaler = self.models[coin_id]["scaler"]
            latest_scaled = scaler.transform(latest_features)

            # Prediction
            model_obj = self.models[coin_id].get("model")

            # Check if it's the old dict format or new StackingRegressor
            if isinstance(model_obj, dict):
                print("⚠️ Legacy model detected. Using simple average.")
                # Use simple average as before
                preds = []
                for m in model_obj.values():
                    preds.append(m.predict(latest_scaled)[0])
                predicted_change = np.mean(preds)
            else:
                predicted_change = model_obj.predict(latest_scaled)[0]

            # Adjust for time frame
            time_frame_adjustment = 1.0
            if time_frame == 7:
                time_frame_adjustment = 1.5
            elif time_frame == 30:
                time_frame_adjustment = 2.0

            predicted_change *= time_frame_adjustment

            print(f"  Final prediction: {predicted_change:.2f}%")

            # Calculate results
            predicted_price = current_price * (1 + predicted_change / 100)

            recent_volatility = df["close"].pct_change().std() * 100
            confidence = max(0, 100 - recent_volatility * 2 - time_frame * 2)
            confidence = min(confidence, 95)

            direction = "bullish" if predicted_change > 0 else "bearish"
            strength = (
                "strong"
                if abs(predicted_change) > 5
                else "moderate" if abs(predicted_change) > 2 else "weak"
            )

            insights = self._generate_insights(df, predicted_change, time_frame)

            print(f"✓ PREDICTION COMPLETE")
            print(f"  Predicted Price: ${predicted_price:,.2f}")
            print(f"  Change: {predicted_change:+.2f}%")
            print(f"  Direction: {direction} ({strength})")
            print(f"  Confidence: {confidence:.1f}%")
            print(f"{'='*60}\\n")

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
            print(f"{'='*60}\\n")
            return self._fallback_prediction(current_price, time_frame)

    def _fallback_prediction(self, current_price: float, time_frame: int = 1) -> Dict:
        """Fallback prediction when ML model fails"""
        # Simple momentum-based fallback
        change = 1.0 * time_frame * 0.5  # Modest prediction

        return {
            "current_price": current_price,
            "predicted_price": current_price * (1 + change / 100),
            "predicted_change_percent": change,
            "confidence_score": 50.0,
            "direction": "neutral",
            "strength": "weak",
            "time_frame": time_frame,
            "timestamp": datetime.now(),
            "insights": [
                "Using fallback prediction model",
                f"Prediction for {time_frame} {'day' if time_frame == 1 else 'days'}",
                "Limited data available for ML prediction",
            ],
            "is_fallback": True,
        }

    def _generate_insights(
        self, df: pd.DataFrame, predicted_change: float, time_frame: int
    ) -> list:
        """Generate trading insights based on technical analysis and time frame"""
        insights = []

        # Time frame specific insights
        if time_frame == 1:
            insights.append("Short-term prediction (24 hours)")
        elif time_frame == 3:
            insights.append("Short-term prediction (72 hours)")
        elif time_frame == 7:
            insights.append("Medium-term prediction (7 days)")
        else:
            insights.append("Long-term prediction (30 days)")

        # RSI analysis
        if "rsi" in df.columns:
            latest_rsi = df["rsi"].iloc[-1]
            if not np.isnan(latest_rsi):
                if latest_rsi > 70:
                    insights.append("RSI indicates overbought conditions")
                elif latest_rsi < 30:
                    insights.append("RSI indicates oversold conditions")
                else:
                    insights.append("RSI in neutral territory")

        # MACD analysis
        if "macd" in df.columns and "macd_signal" in df.columns:
            if df["macd"].iloc[-1] > df["macd_signal"].iloc[-1]:
                insights.append("MACD bullish crossover detected")
            else:
                insights.append("MACD bearish signal")

        # Volatility analysis
        volatility = df["close"].pct_change().std() * 100
        if not np.isnan(volatility):
            if volatility > 5:
                insights.append(f"High volatility detected ({volatility:.1f}%)")
            elif volatility < 2:
                insights.append(f"Low volatility detected ({volatility:.1f}%)")

        # Price trend
        if len(df) >= 5:
            recent_trend = (df["close"].iloc[-1] / df["close"].iloc[-5] - 1) * 100
            if abs(recent_trend) > 3:
                trend_direction = "up" if recent_trend > 0 else "down"
                insights.append(
                    f"Strong {trend_direction} trend ({abs(recent_trend):.1f}% in 5 periods)"
                )

        # Volume analysis
        if "volume_ratio" in df.columns:
            volume_ratio = df["volume_ratio"].iloc[-1]
            if not np.isnan(volume_ratio) and volume_ratio > 1.5:
                insights.append("High volume activity detected")

        # Add prediction-based insight
        if abs(predicted_change) > 3:
            direction = "increase" if predicted_change > 0 else "decrease"
            insights.append(
                f"Model predicts {direction} of {abs(predicted_change):.1f}% over the selected time frame"
            )

        # Time frame specific volatility analysis
        if time_frame > 1 and len(df) >= 30:
            long_term_volatility = (
                df["close"].pct_change().rolling(window=30).std().iloc[-1] * 100
            )
            if not np.isnan(long_term_volatility):
                insights.append(f"Long-term volatility: {long_term_volatility:.1f}%")

        return insights[:6]  # Return top 6 insights

    def get_model_performance(self, coin_id: str) -> Optional[Dict]:
        """Get model performance metrics"""
        if coin_id in self.models:
            model_info = self.models[coin_id]
            # Handle legacy
            if "models" in model_info:
                models_list = list(model_info.get("models", {}).keys())
            else:
                models_list = ["StackingRegressor"]

            return {
                "last_trained": model_info.get("last_trained"),
                "ensemble_mae": model_info.get("ensemble_mae"),
                "ensemble_rmse": model_info.get("ensemble_rmse"),
                "models_trained": models_list,
                "days_trained": model_info.get("days_trained", 90),
            }
        return None
