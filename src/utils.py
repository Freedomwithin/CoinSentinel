"""
Utility functions for CoinSentinel crypto tracking application.
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
import json
from datetime import datetime, timedelta


def create_price_predictor_model():
    """
    Create a basic price prediction model and scaler.
    
    Returns:
        Tuple of (model, scaler)
    """
    model = LinearRegression()
    scaler = StandardScaler()
    return model, scaler


def create_advanced_predictor_model():
    """
    Create an ensemble of advanced models for price prediction.
    
    Returns:
        Dictionary of models and scaler
    """
    models = {
        'rf': RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            random_state=42,
            n_jobs=-1
        ),
        'gb': GradientBoostingRegressor(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=5,
            random_state=42
        )
    }
    scaler = StandardScaler()
    return models, scaler


def calculate_rsi(prices, period=14):
    """
    Calculate Relative Strength Index (RSI).
    
    Args:
        prices: Array or list of prices
        period: RSI period (default 14)
        
    Returns:
        Array of RSI values
    """
    prices = np.array(prices)
    deltas = np.diff(prices)
    
    gains = np.where(deltas > 0, deltas, 0)
    losses = np.where(deltas < 0, -deltas, 0)
    
    avg_gains = np.convolve(gains, np.ones(period), 'valid') / period
    avg_losses = np.convolve(losses, np.ones(period), 'valid') / period
    
    # Avoid division by zero
    avg_losses = np.where(avg_losses == 0, 1e-10, avg_losses)
    
    rs = avg_gains / avg_losses
    rsi = 100 - (100 / (1 + rs))
    
    # Pad the beginning with NaN
    rsi = np.concatenate([np.full(len(prices) - len(rsi), np.nan), rsi])
    
    return rsi


def calculate_macd(prices, fast=12, slow=26, signal=9):
    """
    Calculate MACD (Moving Average Convergence Divergence).
    
    Args:
        prices: Array or list of prices
        fast: Fast EMA period
        slow: Slow EMA period
        signal: Signal line period
        
    Returns:
        Tuple of (macd, signal_line, histogram)
    """
    prices = pd.Series(prices)
    
    ema_fast = prices.ewm(span=fast, adjust=False).mean()
    ema_slow = prices.ewm(span=slow, adjust=False).mean()
    
    macd = ema_fast - ema_slow
    signal_line = macd.ewm(span=signal, adjust=False).mean()
    histogram = macd - signal_line
    
    return macd.values, signal_line.values, histogram.values


def calculate_bollinger_bands(prices, period=20, num_std=2):
    """
    Calculate Bollinger Bands.
    
    Args:
        prices: Array or list of prices
        period: Moving average period
        num_std: Number of standard deviations
        
    Returns:
        Tuple of (upper_band, middle_band, lower_band)
    """
    prices = pd.Series(prices)
    
    middle_band = prices.rolling(window=period, min_periods=1).mean()
    std = prices.rolling(window=period, min_periods=1).std()
    
    upper_band = middle_band + (std * num_std)
    lower_band = middle_band - (std * num_std)
    
    return upper_band.values, middle_band.values, lower_band.values


def calculate_moving_averages(prices, windows=[7, 14, 30, 50, 200]):
    """
    Calculate multiple simple moving averages.
    
    Args:
        prices: Array or list of prices
        windows: List of window sizes
        
    Returns:
        Dictionary of moving averages
    """
    prices = pd.Series(prices)
    mas = {}
    
    for window in windows:
        mas[f'sma_{window}'] = prices.rolling(
            window=window, 
            min_periods=1
        ).mean().values
    
    return mas


def calculate_ema(prices, span=12):
    """
    Calculate Exponential Moving Average.
    
    Args:
        prices: Array or list of prices
        span: EMA span
        
    Returns:
        Array of EMA values
    """
    prices = pd.Series(prices)
    return prices.ewm(span=span, adjust=False).mean().values


def calculate_volatility(prices, window=14):
    """
    Calculate price volatility (standard deviation).
    
    Args:
        prices: Array or list of prices
        window: Window size for calculation
        
    Returns:
        Array of volatility values
    """
    prices = pd.Series(prices)
    return prices.rolling(window=window, min_periods=1).std().values


def calculate_returns(prices):
    """
    Calculate percentage returns.
    
    Args:
        prices: Array or list of prices
        
    Returns:
        Array of percentage returns
    """
    prices = np.array(prices)
    returns = np.zeros_like(prices)
    returns[1:] = (prices[1:] - prices[:-1]) / prices[:-1] * 100
    return returns


def detect_support_resistance(prices, window=20, threshold=0.02):
    """
    Detect support and resistance levels.
    
    Args:
        prices: Array or list of prices
        window: Window size for local extrema
        threshold: Threshold for level clustering
        
    Returns:
        Tuple of (support_levels, resistance_levels)
    """
    prices = np.array(prices)
    
    # Find local minima (support) and maxima (resistance)
    support_candidates = []
    resistance_candidates = []
    
    for i in range(window, len(prices) - window):
        # Check if local minimum
        if prices[i] == min(prices[i-window:i+window+1]):
            support_candidates.append(prices[i])
        
        # Check if local maximum
        if prices[i] == max(prices[i-window:i+window+1]):
            resistance_candidates.append(prices[i])
    
    # Cluster nearby levels
    def cluster_levels(levels, threshold):
        if not levels:
            return []
        
        levels = sorted(levels)
        clustered = []
        current_cluster = [levels[0]]
        
        for level in levels[1:]:
            if abs(level - current_cluster[-1]) / current_cluster[-1] <= threshold:
                current_cluster.append(level)
            else:
                clustered.append(np.mean(current_cluster))
                current_cluster = [level]
        
        clustered.append(np.mean(current_cluster))
        return clustered
    
    support_levels = cluster_levels(support_candidates, threshold)
    resistance_levels = cluster_levels(resistance_candidates, threshold)
    
    return support_levels, resistance_levels


def calculate_sharpe_ratio(returns, risk_free_rate=0.0):
    """
    Calculate Sharpe ratio for a series of returns.
    
    Args:
        returns: Array of returns
        risk_free_rate: Risk-free rate (annualized)
        
    Returns:
        Sharpe ratio
    """
    returns = np.array(returns)
    excess_returns = returns - (risk_free_rate / 252)  # Daily risk-free rate
    
    if len(excess_returns) == 0 or np.std(excess_returns) == 0:
        return 0.0
    
    sharpe = np.mean(excess_returns) / np.std(excess_returns) * np.sqrt(252)
    return sharpe


def format_large_number(number):
    """
    Format large numbers with K, M, B suffixes.
    
    Args:
        number: Number to format
        
    Returns:
        Formatted string
    """
    if number >= 1e9:
        return f"${number/1e9:.2f}B"
    elif number >= 1e6:
        return f"${number/1e6:.2f}M"
    elif number >= 1e3:
        return f"${number/1e3:.2f}K"
    else:
        return f"${number:.2f}"


def calculate_profit_loss(entry_price, current_price, quantity):
    """
    Calculate profit/loss for a position.
    
    Args:
        entry_price: Entry price
        current_price: Current price
        quantity: Position quantity
        
    Returns:
        Tuple of (profit_loss_amount, profit_loss_percentage)
    """
    pl_amount = (current_price - entry_price) * quantity
    pl_percentage = ((current_price - entry_price) / entry_price) * 100
    
    return pl_amount, pl_percentage


def validate_price_data(prices, min_length=10):
    """
    Validate price data for analysis.
    
    Args:
        prices: Array or list of prices
        min_length: Minimum required length
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if prices is None:
        return False, "Price data is None"
    
    if len(prices) < min_length:
        return False, f"Insufficient data: need at least {min_length} points, got {len(prices)}"
    
    if any(p <= 0 for p in prices):
        return False, "Invalid prices: all prices must be positive"
    
    if any(np.isnan(p) for p in prices):
        return False, "Invalid prices: contains NaN values"
    
    return True, ""


def save_portfolio_data(portfolio, filename='portfolio.json'):
    """
    Save portfolio data to JSON file.
    
    Args:
        portfolio: Portfolio dictionary
        filename: Output filename
    """
    with open(filename, 'w') as f:
        json.dump(portfolio, f, indent=2)


def load_portfolio_data(filename='portfolio.json'):
    """
    Load portfolio data from JSON file.
    
    Args:
        filename: Input filename
        
    Returns:
        Portfolio dictionary or empty dict if file doesn't exist
    """
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def calculate_correlation(prices1, prices2):
    """
    Calculate correlation between two price series.
    
    Args:
        prices1: First price series
        prices2: Second price series
        
    Returns:
        Correlation coefficient
    """
    if len(prices1) != len(prices2):
        min_len = min(len(prices1), len(prices2))
        prices1 = prices1[-min_len:]
        prices2 = prices2[-min_len:]
    
    return np.corrcoef(prices1, prices2)[0, 1]


def generate_price_alerts(current_price, alert_levels):
    """
    Generate alerts based on price levels.
    
    Args:
        current_price: Current price
        alert_levels: Dictionary of alert levels and types
        
    Returns:
        List of triggered alerts
    """
    alerts = []
    
    for level, alert_type in alert_levels.items():
        if alert_type == 'above' and current_price >= level:
            alerts.append({
                'type': 'above',
                'level': level,
                'current_price': current_price
            })
        elif alert_type == 'below' and current_price <= level:
            alerts.append({
                'type': 'below',
                'level': level,
                'current_price': current_price
            })
    
    return alerts


def calculate_drawdown(prices):
    """
    Calculate maximum drawdown.
    
    Args:
        prices: Array or list of prices
        
    Returns:
        Tuple of (max_drawdown, drawdown_series)
    """
    prices = np.array(prices)
    running_max = np.maximum.accumulate(prices)
    drawdown = (prices - running_max) / running_max * 100
    max_drawdown = np.min(drawdown)
    
    return max_drawdown, drawdown


# Example usage
if __name__ == "__main__":
    # Generate sample data
    np.random.seed(42)
    sample_prices = 45000 + np.cumsum(np.random.randn(100) * 500)
    
    print("Technical Indicators Example:")
    print(f"Latest Price: ${sample_prices[-1]:,.2f}")
    
    # RSI
    rsi = calculate_rsi(sample_prices)
    print(f"RSI (14): {rsi[-1]:.2f}")
    
    # MACD
    macd, signal, hist = calculate_macd(sample_prices)
    print(f"MACD: {macd[-1]:.2f}, Signal: {signal[-1]:.2f}")
    
    # Bollinger Bands
    upper, middle, lower = calculate_bollinger_bands(sample_prices)
    print(f"Bollinger Bands: Upper ${upper[-1]:,.2f}, Middle ${middle[-1]:,.2f}, Lower ${lower[-1]:,.2f}")
    
    # Support/Resistance
    support, resistance = detect_support_resistance(sample_prices)
    print(f"Support Levels: {[f'${s:,.2f}' for s in support[-3:]]}")
    print(f"Resistance Levels: {[f'${r:,.2f}' for r in resistance[-3:]]}")
    
    # Drawdown
    max_dd, dd_series = calculate_drawdown(sample_prices)
    print(f"Maximum Drawdown: {max_dd:.2f}%")