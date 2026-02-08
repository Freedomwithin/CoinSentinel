# src/api_handler.py

import time
from typing import Dict, List, Optional
from pycoingecko import CoinGeckoAPI
import pandas as pd
from datetime import datetime, timedelta


class EnhancedCryptoAPIHandler:
    def __init__(self):
        self.cg = CoinGeckoAPI()
        self.coin_cache = {}
        self.last_request_time = 0
        self.rate_limit_delay = 1.5  # seconds between requests

    def _rate_limit(self):
        """Implement rate limiting to avoid API throttling"""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        if time_since_last_request < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - time_since_last_request)
        self.last_request_time = time.time()

    def get_top_coins(self, limit=100, vs_currency="usd"):
        """Get top cryptocurrencies by market cap"""
        try:
            self._rate_limit()
            # Get coin list with market data
            coins = self.cg.get_coins_markets(
                vs_currency=vs_currency,
                order="market_cap_desc",
                per_page=limit,
                page=1,
                sparkline=False,
                price_change_percentage="1h,24h,7d",
            )
            return coins
        except Exception as e:
            print(f"API Error in get_top_coins: {e}")
            return []

    def get_coin_history(self, coin_id: str, days: int = 90) -> Optional[pd.DataFrame]:
        """
        Get historical OHLCV data for a coin
        
        Args:
            coin_id: CoinGecko coin ID
            days: Number of days of historical data
            
        Returns:
            DataFrame with columns: timestamp, open, high, low, close, volume
        """
        try:
            self._rate_limit()
            
            print(f"Fetching {days} days of history for {coin_id}")
            
            # Get market chart data (works for any time period)
            market_chart = self.cg.get_coin_market_chart_by_id(
                id=coin_id,
                vs_currency='usd',
                days=days
            )
            
            if not market_chart or 'prices' not in market_chart:
                print("No market chart data available")
                return None
            
            # Create DataFrame from prices
            prices_df = pd.DataFrame(
                market_chart['prices'],
                columns=['timestamp', 'close']
            )
            prices_df['timestamp'] = pd.to_datetime(prices_df['timestamp'], unit='ms')
            
            # Add volume if available
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
            
            # Create OHLC approximation from close prices
            # Use hourly grouping for more granular data
            df['hour'] = df['timestamp'].dt.floor('H')
            
            hourly = df.groupby('hour').agg({
                'close': ['first', 'max', 'min', 'last'],
                'volume': 'sum',
                'timestamp': 'first'
            }).reset_index()
            
            hourly.columns = ['hour', 'open', 'high', 'low', 'close', 'volume', 'timestamp']
            hourly = hourly[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
            
            # Ensure we have enough data
            if len(hourly) < 30:
                # If hourly data is insufficient, use the raw close prices
                df['open'] = df['close'].shift(1).fillna(df['close'])
                df['high'] = df['close']
                df['low'] = df['close']
                result = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
            else:
                result = hourly
            
            print(f"Successfully fetched {len(result)} data points")
            return result
            
        except Exception as e:
            print(f"Error fetching coin history for {coin_id}: {e}")
            import traceback
            traceback.print_exc()
            return None

    def get_price(self, coin_ids: List[str], vs_currency: str = "usd") -> Dict:
        """
        Get current prices for multiple coins
        
        Args:
            coin_ids: List of coin IDs
            vs_currency: Currency to get prices in
            
        Returns:
            Dictionary mapping coin_id to price data
        """
        try:
            self._rate_limit()
            
            # Convert list to comma-separated string
            ids_str = ",".join(coin_ids)
            
            result = self.cg.get_price(
                ids=ids_str,
                vs_currencies=vs_currency,
                include_market_cap=True,
                include_24hr_vol=True,
                include_24hr_change=True
            )
            
            return result
            
        except Exception as e:
            print(f"Error fetching prices: {e}")
            return {}

    def get_coin_info(self, coin_id: str) -> Dict:
        """
        Get detailed information about a specific coin
        
        Args:
            coin_id: CoinGecko coin ID
            
        Returns:
            Dictionary with coin information
        """
        try:
            # Check cache first
            if coin_id in self.coin_cache:
                cache_time, data = self.coin_cache[coin_id]
                # Cache for 5 minutes
                if time.time() - cache_time < 300:
                    return data
            
            self._rate_limit()
            
            # Get basic coin data
            coin_data = self.cg.get_coin_by_id(
                id=coin_id,
                localization=False,
                tickers=False,
                market_data=True,
                community_data=False,
                developer_data=False
            )
            
            result = {
                'id': coin_id,
                'name': coin_data.get('name', coin_id),
                'symbol': coin_data.get('symbol', '').upper(),
                'market_cap_rank': coin_data.get('market_cap_rank'),
            }
            
            # Cache the result
            self.coin_cache[coin_id] = (time.time(), result)
            
            return result
            
        except Exception as e:
            print(f"Error fetching coin info for {coin_id}: {e}")
            # Return minimal info
            return {
                'id': coin_id,
                'name': coin_id.capitalize(),
                'symbol': coin_id.upper(),
                'market_cap_rank': None
            }

    def get_coin_sentiment(self, coin_id: str) -> Dict:
        """
        Get sentiment data for a specific coin (mock implementation)
        
        Args:
            coin_id: CoinGecko coin ID
            
        Returns:
            Dictionary with sentiment percentages
        """
        try:
            # This is a simplified version - real implementation would use
            # social media data, news sentiment, etc.
            
            # Get recent price action as a proxy for sentiment
            df = self.get_coin_history(coin_id, days=7)
            
            if df is not None and len(df) > 0:
                # Calculate price change
                price_change = ((df['close'].iloc[-1] / df['close'].iloc[0]) - 1) * 100
                
                # Simple sentiment based on price action
                if price_change > 5:
                    return {"positive": 70, "negative": 10, "neutral": 20}
                elif price_change > 0:
                    return {"positive": 55, "negative": 20, "neutral": 25}
                elif price_change > -5:
                    return {"positive": 25, "negative": 35, "neutral": 40}
                else:
                    return {"positive": 15, "negative": 65, "neutral": 20}
            
            # Default neutral sentiment
            return {"positive": 33, "negative": 33, "neutral": 34}
            
        except Exception as e:
            print(f"Error getting coin sentiment: {e}")
            return {"positive": 33, "negative": 33, "neutral": 34}
