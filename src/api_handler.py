# api_handler.py - COMPLETE VERSION for YOUR predictor

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
        self.rate_limit_delay = 1.5

    def _rate_limit(self):
        """Rate limiting to avoid API throttling"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time

        if time_since_last < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - time_since_last)

        self.last_request_time = time.time()

    # ==================== CRITICAL METHOD FOR YOUR PREDICTOR ====================
    def get_comprehensive_coin_data(self, coin_id, days=90):
        """
        Get comprehensive data in the format expected by AdvancedPricePredictor

        Returns:
            Dictionary with 'prices' key containing [(timestamp_ms, price), ...] tuples
        """
        try:
            print(f"\n{'='*60}")
            print(f"FETCHING COMPREHENSIVE DATA FOR: {coin_id}")
            print(f"Days: {days}")
            print(f"{'='*60}")

            self._rate_limit()

            # Get market chart from CoinGecko
            market_chart = self.cg.get_coin_market_chart_by_id(
                id=coin_id,
                vs_currency='usd',
                days=days
            )

            if not market_chart or 'prices' not in market_chart:
                print("❌ No market data received")
                return None

            # CoinGecko returns prices as [[timestamp_ms, price], ...]
            prices = market_chart['prices']

            print(f"✓ Received {len(prices)} price points")

            # Your predictor expects the data in this exact format
            result = {
                'prices': prices,  # Already in [(timestamp, price), ...] format
                'market_caps': market_chart.get('market_caps', []),
                'total_volumes': market_chart.get('total_volumes', [])
            }

            print(f"✓ Data prepared successfully")
            if prices:
                print(f"  Price range: ${min(p[1] for p in prices):.2f} - ${max(p[1] for p in prices):.2f}")
                print(f"  Date range: {len(prices)} data points over {days} days")
            print(f"{'='*60}\n")

            return result

        except Exception as e:
            print(f"❌ Error in get_comprehensive_coin_data: {e}")
            import traceback
            traceback.print_exc()
            return None

    # ==================== MARKET DATA METHODS ====================
    def get_coin_history(self, coin_id: str, days: int = 90):
        """
        FIXED version with detailed logging
        """
        try:
            print(f"\\n{'='*60}")
            print(f"FETCHING HISTORY FOR: {coin_id}")
            print(f"Days requested: {days}")
            print(f"{'='*60}")
            
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
            print(f"{'='*60}\\n")
            
            return result
            
        except Exception as e:
            print(f"❌ ERROR in get_coin_history: {e}")
            import traceback
            traceback.print_exc()
            return None

    def get_top_coins(self, limit=100, vs_currency="usd"):
        """Get top cryptocurrencies with ALL percentage changes"""
        try:
            self._rate_limit()
            
            print(f"API: Requesting {limit} coins in {vs_currency}...")

            # CRITICAL: Request percentage changes for 1h, 24h, and 7d
            coins = self.cg.get_coins_markets(
                vs_currency=vs_currency,
                order="market_cap_desc",
                per_page=limit,
                page=1,
                sparkline=False,
                price_change_percentage="1h,24h,7d"  # THIS IS KEY!
            )

            print(f"API: Received {len(coins) if coins else 0} coins")

            # Verify we have the data
            if coins and len(coins) > 0:
                sample = coins[0]
                has_1h = 'price_change_percentage_1h_in_currency' in sample
                has_24h = 'price_change_percentage_24h_in_currency' in sample
                has_7d = 'price_change_percentage_7d_in_currency' in sample
                print(f"API: Data check - 1h: {has_1h}, 24h: {has_24h}, 7d: {has_7d}")

            return coins

        except Exception as e:
            print(f"API Error in get_top_coins: {e}")
            import traceback
            traceback.print_exc()
            return []

    def get_price(self, coin_ids: List[str], vs_currency: str = "usd") -> Dict:
        """Get current prices for multiple coins"""
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
        """Get detailed information about a specific coin"""
        try:
            # Check cache first (5 min cache)
            if coin_id in self.coin_cache:
                cache_time, data = self.coin_cache[coin_id]
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
        """Get sentiment data for a specific coin (simplified)"""
        try:
            # Get recent price data as proxy for sentiment
            data = self.get_comprehensive_coin_data(coin_id, days=7)
            
            if data and 'prices' in data and len(data['prices']) > 0:
                # Calculate price change
                first_price = data['prices'][0][1]
                last_price = data['prices'][-1][1]
                price_change = ((last_price / first_price) - 1) * 100
                
                # Simple sentiment based on price action
                if price_change > 5:
                    return {"positive": 70.0, "negative": 10.0, "neutral": 20.0}
                elif price_change > 0:
                    return {"positive": 55.0, "negative": 20.0, "neutral": 25.0}
                elif price_change > -5:
                    return {"positive": 25.0, "negative": 35.0, "neutral": 40.0}
                else:
                    return {"positive": 15.0, "negative": 65.0, "neutral": 20.0}
            
            # Default neutral sentiment
            return {"positive": 33.0, "negative": 33.0, "neutral": 34.0}
            
        except Exception as e:
            print(f"Error getting coin sentiment: {e}")
            return {"positive": 33.0, "negative": 33.0, "neutral": 34.0}


# Example usage and testing
if __name__ == "__main__":
    print("Testing EnhancedCryptoAPIHandler...")

    api = EnhancedCryptoAPIHandler()

    # Test comprehensive data (for predictor)
    print("\n1. Testing get_comprehensive_coin_data...")
    data = api.get_comprehensive_coin_data('bitcoin', days=30)
    if data:
        print(f"✓ Success! Got {len(data['prices'])} price points")
    else:
        print("✗ Failed to get data")

    # Test market data (for market tab)
    print("\n2. Testing get_top_coins...")
    coins = api.get_top_coins(limit=5)
    if coins:
        print(f"✓ Success! Got {len(coins)} coins")
        for coin in coins[:3]:
            print(f"  - {coin['name']}: ${coin['current_price']:,.2f}")
    else:
        print("✗ Failed to get coins")

    print("\n✓ All tests complete!")
