# src/improved_price_predictor.py - Enhanced version with advanced ML techniques

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
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
            except Exception as e:
                print(f"Error calculating TA indicators: {e}")
                # Fill with default values
                df["rsi"] = 50
                df["macd"] = 0
                df["macd_signal"] = 0
                df["macd_diff"] = 0
                df["bb_upper"] = df["close"] * 1.1
                df["bb_lower"] = df["close"] * 0.9
                df["bb_width"] = df["close"] * 0.2
        else:
            # Simple alternatives without ta library
            df["rsi"] = 50  # Neutral RSI
            df["macd"] = 0
            df["macd_signal"] = 0
            df["macd_diff"] = 0
            df["bb_upper"] = df["close"] * 1.1
            df["bb_lower"] = df["close"] * 0.9
            df["bb_width"] = df["close"] * 0.2

        df["volatility"] = df["close"].rolling(window=20, min_periods=1).std()

        # Volume indicators
        if "volume" in df.columns:
            df["volume_sma"] = df["volume"].rolling(window=20, min_periods=1).mean()
            df["volume_ratio"] = df["volume"] / df["volume_sma"]
            df["price_volume_corr"] = df["close"].rolling(window=20, min_periods=1).corr(df["volume"])
        else:
            df["volume_sma"] = 0
            df["volume_ratio"] = 1
            df["price_volume_corr"] = 0

        # Price position
        df["high_20"] = df["high"].rolling(window=20, min_periods=1).max() if "high" in df.columns else df["close"]
        df["low_20"] = df["low"].rolling(window=20, min_periods=1).min() if "low" in df.columns else df["close"]
        df["price_position"] = (df["close"] - df["low_20"]) / (df["high_20"] - df["low_20"] + 0.0001)

        # Rate of change
        df["roc_7"] = ((df["close"] - df["close"].shift(7)) / (df["close"].shift(7) + 0.0001)) * 100
        df["roc_14"] = ((df["close"] - df["close"].shift(14)) / (df["close"].shift(14) + 0.0001)) * 100

        # Target: future price change (next period)
        df["target"] = ((df["close"].shift(-1) - df["close"]) / (df["close"] + 0.0001)) * 100

        # Drop NaN values
        df = df.dropna()

        return df

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
        ]

        # Ensure all feature columns exist
        existing_features = [col for col in feature_cols if col in df.columns]

        X = df[existing_features].values
        y = df["target"].values if "target" in df.columns else None

        return X, y

    def train_ensemble_model(self, coin_id: str, days: int = 90):
        """Train ensemble model for a specific coin"""
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

            # Train ensemble of models
            models = {
                "rf": RandomForestRegressor(
                    n_estimators=100, random_state=42, n_jobs=-1
                ),
                "gb": GradientBoostingRegressor(n_estimators=100, random_state=42),
            }

            predictions = []
            model_predictions = {}

            for name, model in models.items():
                model.fit(X_train_scaled, y_train)

                # Predict on test set
                y_pred = model.predict(X_test_scaled)

                # Calculate metrics
                mae = mean_absolute_error(y_test, y_pred)
                rmse = np.sqrt(mean_squared_error(y_test, y_pred))

                model_predictions[name] = {
                    "model": model,
                    "mae": mae,
                    "rmse": rmse,
                    "predictions": y_pred,
                }
                predictions.append(y_pred)

            # Ensemble prediction (average)
            ensemble_pred = np.mean(predictions, axis=0)
            ensemble_mae = mean_absolute_error(y_test, ensemble_pred)
            ensemble_rmse = np.sqrt(mean_squared_error(y_test, ensemble_pred))

            # Save models and scaler
            model_path = os.path.join(self.model_dir, f"{coin_id}_model.joblib")
            scaler_path = os.path.join(self.model_dir, f"{coin_id}_scaler.joblib")

            simple_models = {
                "rf": model_predictions["rf"]["model"],
                "gb": model_predictions["gb"]["model"],
            }

            joblib.dump(simple_models, model_path)
            joblib.dump(scaler, scaler_path)

            # Update cache
            self.models[coin_id] = {
                "ensemble_mae": ensemble_mae,
                "ensemble_rmse": ensemble_rmse,
                "models": simple_models,
                "last_trained": datetime.now(),
                "days_trained": days,
                "scaler": scaler,
            }

            return (
                True,
                f"Model trained. MAE: {ensemble_mae:.4f}, RMSE: {ensemble_rmse:.4f}",
            )

        except Exception as e:
            print(f"Training error: {e}")
            return False, f"Training error: {str(e)}"

    def predict_price(
        self, coin_id: str, current_price: float, time_frame: int = 1
    ) -> Dict:
        """Predict price change for the selected time frame"""
        try:
            # Load model if not in memory
            if coin_id not in self.models:
                model_path = os.path.join(self.model_dir, f"{coin_id}_model.joblib")
                scaler_path = os.path.join(self.model_dir, f"{coin_id}_scaler.joblib")

                if not os.path.exists(model_path):
                    # Train model if it doesn't exist
                    success, message = self.train_ensemble_model(
                        coin_id, days=max(time_frame * 30, 90)
                    )
                    if not success:
                        return self._fallback_prediction(current_price, time_frame)

                # Load trained models
                try:
                    models_dict = joblib.load(model_path)
                    scaler = joblib.load(scaler_path)

                    self.models[coin_id] = {"models": models_dict, "scaler": scaler}
                except Exception as e:
                    print(f"Error loading model: {e}")
                    return self._fallback_prediction(current_price, time_frame)

            # Get latest data for prediction based on time frame
            days = max(time_frame * 30, 90)  # At least 90 days of history
            df = self.api.get_coin_history(coin_id, days=days)
            if df is None or len(df) < 10:
                return self._fallback_prediction(current_price, time_frame)

            # Prepare features from latest data
            X, _ = self.prepare_features(df)
            if len(X) == 0:
                return self._fallback_prediction(current_price, time_frame)

            # Get latest feature vector
            latest_features = X[-1].reshape(1, -1)

            # Scale features
            scaler = self.models[coin_id]["scaler"]
            latest_scaled = scaler.transform(latest_features)

            # Make ensemble prediction
            predictions = []
            model_weights = {"rf": 0.6, "gb": 0.4}  # Weighted ensemble

            for model_name, weight in model_weights.items():
                if model_name in self.models[coin_id]["models"]:
                    model = self.models[coin_id]["models"][model_name]
                    pred = model.predict(latest_scaled)[0]
                    predictions.append(pred * weight)

            # Calculate predicted price change percentage
            if predictions:
                predicted_change = sum(predictions)
            else:
                predicted_change = 0

            # Adjust prediction based on time frame
            time_frame_adjustment = 1.0
            if time_frame == 3:  # 3 days (72h)
                time_frame_adjustment = 1.2
            elif time_frame == 7:  # 7 days
                time_frame_adjustment = 1.5
            elif time_frame == 30:  # 30 days
                time_frame_adjustment = 2.0

            predicted_change *= time_frame_adjustment

            # Calculate prediction details
            predicted_price = current_price * (1 + predicted_change / 100)

            # Calculate confidence based on recent volatility and time frame
            recent_volatility = df["close"].pct_change().std() * 100
            confidence = max(0, 100 - recent_volatility * 2 - time_frame * 2)
            confidence = min(confidence, 95)  # Cap at 95%

            # Generate insights
            insights = self._generate_insights(df, predicted_change, time_frame)

            # Determine direction and strength
            direction = "bullish" if predicted_change > 0 else "bearish"
            strength = (
                "strong"
                if abs(predicted_change) > 5
                else "moderate" if abs(predicted_change) > 2 else "weak"
            )

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
            print(f"Prediction error for {coin_id}: {e}")
            import traceback
            traceback.print_exc()
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
                "Limited data available for ML prediction"
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
            return {
                "last_trained": self.models[coin_id].get("last_trained"),
                "ensemble_mae": self.models[coin_id].get("ensemble_mae"),
                "ensemble_rmse": self.models[coin_id].get("ensemble_rmse"),
                "models_trained": list(self.models[coin_id].get("models", {}).keys()),
                "days_trained": self.models[coin_id].get("days_trained", 90),
            }
        return None
