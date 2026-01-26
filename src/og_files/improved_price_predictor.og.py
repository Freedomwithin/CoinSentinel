import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import warnings
warnings.filterwarnings('ignore')

class ImprovedPricePredictor:
    def __init__(self, look_back=30):
        """
        Enhanced price predictor with technical indicators and ensemble methods.
        
        Args:
            look_back: Number of days to use for feature creation (increased to 30)
        """
        self.look_back = look_back
        self.scaler = StandardScaler()
        
        # Ensemble of models for better predictions
        self.models = {
            'rf': RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42),
            'gb': GradientBoostingRegressor(n_estimators=100, learning_rate=0.1, random_state=42)
        }
        
        self.is_trained = False
        self.feature_names = []
        
    def calculate_technical_indicators(self, prices, volumes=None):
        """
        Calculate technical indicators for feature engineering.
        
        Args:
            prices: Array of historical prices
            volumes: Array of trading volumes (optional)
            
        Returns:
            DataFrame with technical indicators
        """
        df = pd.DataFrame({'price': prices})
        
        # Moving averages
        df['sma_7'] = df['price'].rolling(window=7, min_periods=1).mean()
        df['sma_14'] = df['price'].rolling(window=14, min_periods=1).mean()
        df['sma_30'] = df['price'].rolling(window=30, min_periods=1).mean()
        
        # Exponential moving averages
        df['ema_7'] = df['price'].ewm(span=7, adjust=False).mean()
        df['ema_14'] = df['price'].ewm(span=14, adjust=False).mean()
        
        # RSI (Relative Strength Index)
        delta = df['price'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14, min_periods=1).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14, min_periods=1).mean()
        rs = gain / (loss + 1e-10)  # Avoid division by zero
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # MACD (Moving Average Convergence Divergence)
        ema_12 = df['price'].ewm(span=12, adjust=False).mean()
        ema_26 = df['price'].ewm(span=26, adjust=False).mean()
        df['macd'] = ema_12 - ema_26
        df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
        df['macd_diff'] = df['macd'] - df['macd_signal']
        
        # Bollinger Bands
        df['bb_middle'] = df['price'].rolling(window=20, min_periods=1).mean()
        bb_std = df['price'].rolling(window=20, min_periods=1).std()
        df['bb_upper'] = df['bb_middle'] + (bb_std * 2)
        df['bb_lower'] = df['bb_middle'] - (bb_std * 2)
        df['bb_width'] = df['bb_upper'] - df['bb_lower']
        
        # Price momentum
        df['momentum_1'] = df['price'].pct_change(1)
        df['momentum_3'] = df['price'].pct_change(3)
        df['momentum_7'] = df['price'].pct_change(7)
        
        # Volatility (standard deviation)
        df['volatility_7'] = df['price'].rolling(window=7, min_periods=1).std()
        df['volatility_14'] = df['price'].rolling(window=14, min_periods=1).std()
        
        # Volume-based features (if available)
        if volumes is not None and len(volumes) == len(prices):
            df['volume'] = volumes
            df['volume_sma_7'] = df['volume'].rolling(window=7, min_periods=1).mean()
            df['volume_ratio'] = df['volume'] / (df['volume_sma_7'] + 1e-10)
            df['price_volume'] = df['price'] * df['volume']
        
        # Price position relative to high/low
        df['price_range_7'] = df['price'].rolling(window=7, min_periods=1).max() - df['price'].rolling(window=7, min_periods=1).min()
        df['price_position'] = (df['price'] - df['price'].rolling(window=7, min_periods=1).min()) / (df['price_range_7'] + 1e-10)
        
        # Fill any NaN values with forward fill then backward fill
        df = df.fillna(method='ffill').fillna(method='bfill')
        
        return df
    
    def create_features(self, df, target_col='price'):
        """
        Create feature matrix for training/prediction.
        
        Args:
            df: DataFrame with technical indicators
            target_col: Name of target column
            
        Returns:
            X (features), y (targets)
        """
        # Remove the target column and non-feature columns
        feature_cols = [col for col in df.columns if col != target_col]
        
        X, y = [], []
        
        # Create sequences for time series prediction
        for i in range(len(df) - self.look_back - 1):
            # Use last look_back days of features
            feature_sequence = df[feature_cols].iloc[i:i + self.look_back].values.flatten()
            target = df[target_col].iloc[i + self.look_back]
            
            X.append(feature_sequence)
            y.append(target)
        
        return np.array(X), np.array(y)
    
    def train(self, historical_prices, volumes=None, test_size=0.2):
        """
        Train the prediction models.
        
        Args:
            historical_prices: Array of historical prices
            volumes: Array of trading volumes (optional)
            test_size: Fraction of data to use for testing
            
        Returns:
            Dictionary with training metrics
        """
        if len(historical_prices) < self.look_back + 10:
            return {
                'error': f'Need at least {self.look_back + 10} data points. Got {len(historical_prices)}'
            }
        
        # Calculate technical indicators
        df = self.calculate_technical_indicators(historical_prices, volumes)
        
        # Create features
        X, y = self.create_features(df)
        
        if len(X) == 0:
            return {'error': 'Failed to create features'}
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, shuffle=False, random_state=42
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train each model
        results = {}
        for name, model in self.models.items():
            model.fit(X_train_scaled, y_train)
            train_score = model.score(X_train_scaled, y_train)
            test_score = model.score(X_test_scaled, y_test)
            
            results[name] = {
                'train_r2': train_score,
                'test_r2': test_score
            }
        
        self.is_trained = True
        self.feature_names = df.columns.tolist()
        
        return results
    
    def predict_next_price(self, historical_prices, volumes=None, horizon=1):
        """
        Predict future prices.
        
        Args:
            historical_prices: Array of historical prices
            volumes: Array of trading volumes (optional)
            horizon: Number of days ahead to predict (1, 2, or 3)
            
        Returns:
            Tuple of (predicted_price, percentage_change, confidence_interval)
        """
        try:
            if len(historical_prices) < self.look_back + 1:
                return None, None, None
            
            # Calculate technical indicators
            df = self.calculate_technical_indicators(historical_prices, volumes)
            
            # Get the last sequence for prediction
            feature_cols = [col for col in df.columns if col != 'price']
            last_sequence = df[feature_cols].iloc[-self.look_back:].values.flatten().reshape(1, -1)
            
            # If not trained, train on this data
            if not self.is_trained:
                print("Training model on provided data...")
                self.train(historical_prices, volumes)
            
            # Scale the features
            last_sequence_scaled = self.scaler.transform(last_sequence)
            
            # Get predictions from all models
            predictions = []
            for model in self.models.values():
                pred = model.predict(last_sequence_scaled)[0]
                predictions.append(pred)
            
            # Ensemble prediction (average)
            predicted_price = np.mean(predictions)
            
            # Calculate confidence interval (std of model predictions)
            confidence_interval = np.std(predictions) * 1.96  # 95% CI
            
            # Calculate percentage change
            last_actual_price = historical_prices[-1]
            percentage_change = ((predicted_price - last_actual_price) / last_actual_price) * 100
            
            # Multi-step prediction (simple iterative approach)
            if horizon > 1:
                future_predictions = [predicted_price]
                for _ in range(horizon - 1):
                    # Use last prediction to predict next
                    # This is simplified - in production you'd update all features
                    future_pred = np.mean([
                        model.predict(last_sequence_scaled)[0] 
                        for model in self.models.values()
                    ])
                    future_predictions.append(future_pred)
                
                predicted_price = future_predictions[-1]
                percentage_change = ((predicted_price - last_actual_price) / last_actual_price) * 100
            
            return predicted_price, percentage_change, confidence_interval
            
        except Exception as e:
            print(f"Prediction error: {e}")
            return None, None, None
    
    def get_feature_importance(self, top_n=10):
        """
        Get feature importance from Random Forest model.
        
        Returns:
            Dictionary of top features and their importance scores
        """
        if not self.is_trained or 'rf' not in self.models:
            return {}
        
        rf_model = self.models['rf']
        importances = rf_model.feature_importances_
        
        # Note: feature names are flattened sequences, so this is approximate
        feature_importance = dict(zip(
            [f'feature_{i}' for i in range(len(importances))],
            importances
        ))
        
        # Get top N features
        sorted_features = sorted(
            feature_importance.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:top_n]
        
        return dict(sorted_features)


# Example usage
if __name__ == "__main__":
    # Generate sample data (replace with real data)
    np.random.seed(42)
    days = 100
    base_price = 45000
    trend = np.linspace(0, 5000, days)
    noise = np.random.normal(0, 2000, days)
    sample_prices = base_price + trend + noise
    sample_volumes = np.random.uniform(1e9, 5e9, days)
    
    # Create and train predictor
    predictor = ImprovedPricePredictor(look_back=30)
    
    print("Training models...")
    results = predictor.train(sample_prices, sample_volumes)
    print("\nTraining Results:")
    for model_name, metrics in results.items():
        print(f"{model_name.upper()}: Train R² = {metrics['train_r2']:.4f}, Test R² = {metrics['test_r2']:.4f}")
    
    # Make prediction
    print("\nMaking prediction...")
    pred_price, pct_change, conf_interval = predictor.predict_next_price(
        sample_prices, sample_volumes, horizon=1
    )
    
    if pred_price is not None:
        print(f"\nPredicted Price: ${pred_price:,.2f}")
        print(f"Percentage Change: {pct_change:+.2f}%")
        print(f"95% Confidence Interval: ±${conf_interval:,.2f}")
        print(f"Price Range: ${pred_price - conf_interval:,.2f} - ${pred_price + conf_interval:,.2f}")
    
    # Show feature importance
    print("\nTop Feature Importances:")
    importance = predictor.get_feature_importance(top_n=5)
    for feat, score in importance.items():
        print(f"{feat}: {score:.4f}")