from pycoingecko import CoinGeckoAPI
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time

class ImprovedCryptoDataFetcher:
    def __init__(self):
        self.cg = CoinGeckoAPI()
        self.coin_id_cache = {}
        
    def get_coin_id(self, symbol):
        """
        Convert coin symbol to CoinGecko ID.
        Uses cache to avoid repeated API calls.
        """
        symbol = symbol.lower()
        
        if symbol in self.coin_id_cache:
            return self.coin_id_cache[symbol]
        
        # Common mappings
        common_mappings = {
            'btc': 'bitcoin',
            'eth': 'ethereum',
            'usdt': 'tether',
            'bnb': 'binancecoin',
            'sol': 'solana',
            'xrp': 'ripple',
            'usdc': 'usd-coin',
            'ada': 'cardano',
            'avax': 'avalanche-2',
            'doge': 'dogecoin',
            'dot': 'polkadot',
            'matic': 'matic-network',
            'link': 'chainlink',
            'uni': 'uniswap',
            'atom': 'cosmos',
            'ltc': 'litecoin',
            'etc': 'ethereum-classic',
            'xlm': 'stellar',
            'algo': 'algorand',
            'vet': 'vechain'
        }
        
        if symbol in common_mappings:
            coin_id = common_mappings[symbol]
            self.coin_id_cache[symbol] = coin_id
            return coin_id
        
        # If not in common mappings, search
        try:
            coins_list = self.cg.get_coins_list()
            for coin in coins_list:
                if coin['symbol'].lower() == symbol:
                    self.coin_id_cache[symbol] = coin['id']
                    return coin['id']
        except Exception as e:
            print(f"Error finding coin ID for {symbol}: {e}")
        
        return None
    
    def get_top_coins(self, limit=50, vs_currency='usd'):
        """
        Get top coins by market cap with comprehensive data.
        
        Args:
            limit: Number of coins to fetch
            vs_currency: Currency for prices
            
        Returns:
            List of dictionaries with coin data
        """
        try:
            data = self.cg.get_coins_markets(
                vs_currency=vs_currency,
                order='market_cap_desc',
                per_page=limit,
                page=1,
                sparkline=True,  # Include 7-day sparkline data
                price_change_percentage='1h,24h,7d,30d'
            )
            return data
        except Exception as e:
            print(f"Error fetching top coins: {e}")
            return []
    
    def get_historical_data(self, symbol, days=90, vs_currency='usd', interval='daily'):
        """
        Get comprehensive historical data for a cryptocurrency.
        
        Args:
            symbol: Coin symbol (e.g., 'BTC')
            days: Number of days of historical data
            vs_currency: Currency for prices
            interval: 'daily' or 'hourly' (hourly limited to 90 days)
            
        Returns:
            Dictionary with prices, volumes, market_caps, and timestamps
        """
        coin_id = self.get_coin_id(symbol)
        if not coin_id:
            print(f"Could not find coin ID for {symbol}")
            return None
        
        try:
            # Get OHLC data if available
            if days <= 90:
                ohlc_data = self.cg.get_coin_ohlc_by_id(
                    id=coin_id,
                    vs_currency=vs_currency,
                    days=days
                )
                
                if ohlc_data:
                    df = pd.DataFrame(
                        ohlc_data,
                        columns=['timestamp', 'open', 'high', 'low', 'close']
                    )
                    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                    
                    # Also get volume data
                    market_chart = self.cg.get_coin_market_chart_by_id(
                        id=coin_id,
                        vs_currency=vs_currency,
                        days=days
                    )
                    
                    volumes = pd.DataFrame(
                        market_chart['total_volumes'],
                        columns=['timestamp', 'volume']
                    )
                    volumes['timestamp'] = pd.to_datetime(volumes['timestamp'], unit='ms')
                    
                    # Merge OHLC with volumes
                    df = pd.merge_asof(
                        df.sort_values('timestamp'),
                        volumes.sort_values('timestamp'),
                        on='timestamp',
                        direction='nearest'
                    )
                    
                    return {
                        'timestamps': df['timestamp'].tolist(),
                        'open': df['open'].tolist(),
                        'high': df['high'].tolist(),
                        'low': df['low'].tolist(),
                        'close': df['close'].tolist(),
                        'volume': df['volume'].fillna(0).tolist()
                    }
            
            # Fallback to market chart data
            market_chart = self.cg.get_coin_market_chart_by_id(
                id=coin_id,
                vs_currency=vs_currency,
                days=days
            )
            
            prices_df = pd.DataFrame(
                market_chart['prices'],
                columns=['timestamp', 'price']
            )
            volumes_df = pd.DataFrame(
                market_chart['total_volumes'],
                columns=['timestamp', 'volume']
            )
            market_caps_df = pd.DataFrame(
                market_chart['market_caps'],
                columns=['timestamp', 'market_cap']
            )
            
            # Convert timestamps
            prices_df['timestamp'] = pd.to_datetime(prices_df['timestamp'], unit='ms')
            volumes_df['timestamp'] = pd.to_datetime(volumes_df['timestamp'], unit='ms')
            market_caps_df['timestamp'] = pd.to_datetime(market_caps_df['timestamp'], unit='ms')
            
            # Merge all data
            df = prices_df.merge(volumes_df, on='timestamp', how='left')
            df = df.merge(market_caps_df, on='timestamp', how='left')
            
            return {
                'timestamps': df['timestamp'].tolist(),
                'prices': df['price'].tolist(),
                'volumes': df['volume'].fillna(0).tolist(),
                'market_caps': df['market_cap'].fillna(0).tolist()
            }
            
        except Exception as e:
            print(f"Error fetching historical data for {symbol}: {e}")
            return None
    
    def get_detailed_coin_info(self, symbol):
        """
        Get detailed information about a cryptocurrency.
        
        Args:
            symbol: Coin symbol
            
        Returns:
            Dictionary with detailed coin information
        """
        coin_id = self.get_coin_id(symbol)
        if not coin_id:
            return None
        
        try:
            data = self.cg.get_coin_by_id(
                id=coin_id,
                localization=False,
                tickers=False,
                market_data=True,
                community_data=True,
                developer_data=False
            )
            
            market_data = data.get('market_data', {})
            
            return {
                'name': data.get('name'),
                'symbol': data.get('symbol', '').upper(),
                'current_price': market_data.get('current_price', {}).get('usd'),
                'market_cap': market_data.get('market_cap', {}).get('usd'),
                'total_volume': market_data.get('total_volume', {}).get('usd'),
                'circulating_supply': market_data.get('circulating_supply'),
                'total_supply': market_data.get('total_supply'),
                'max_supply': market_data.get('max_supply'),
                'ath': market_data.get('ath', {}).get('usd'),
                'ath_date': market_data.get('ath_date', {}).get('usd'),
                'atl': market_data.get('atl', {}).get('usd'),
                'atl_date': market_data.get('atl_date', {}).get('usd'),
                'price_change_24h': market_data.get('price_change_24h'),
                'price_change_percentage_24h': market_data.get('price_change_percentage_24h'),
                'price_change_percentage_7d': market_data.get('price_change_percentage_7d'),
                'price_change_percentage_30d': market_data.get('price_change_percentage_30d'),
                'market_cap_rank': data.get('market_cap_rank'),
                'description': data.get('description', {}).get('en', '')[:500]  # First 500 chars
            }
            
        except Exception as e:
            print(f"Error fetching detailed info for {symbol}: {e}")
            return None
    
    def get_trending_coins(self):
        """
        Get currently trending coins.
        
        Returns:
            List of trending coins
        """
        try:
            data = self.cg.get_search_trending()
            coins = data.get('coins', [])
            return [
                {
                    'id': coin['item']['id'],
                    'name': coin['item']['name'],
                    'symbol': coin['item']['symbol'],
                    'market_cap_rank': coin['item'].get('market_cap_rank'),
                    'price_btc': coin['item'].get('price_btc')
                }
                for coin in coins
            ]
        except Exception as e:
            print(f"Error fetching trending coins: {e}")
            return []
    
    def get_global_market_data(self):
        """
        Get global cryptocurrency market statistics.
        
        Returns:
            Dictionary with global market data
        """
        try:
            data = self.cg.get_global()
            return {
                'total_market_cap_usd': data.get('total_market_cap', {}).get('usd'),
                'total_volume_usd': data.get('total_volume', {}).get('usd'),
                'market_cap_percentage': data.get('market_cap_percentage', {}),
                'active_cryptocurrencies': data.get('active_cryptocurrencies'),
                'markets': data.get('markets'),
                'market_cap_change_percentage_24h': data.get('market_cap_change_percentage_24h_usd')
            }
        except Exception as e:
            print(f"Error fetching global market data: {e}")
            return {}
    
    def batch_get_historical_data(self, symbols, days=90, delay=1.5):
        """
        Get historical data for multiple coins with rate limiting.
        
        Args:
            symbols: List of coin symbols
            days: Number of days of historical data
            delay: Delay between API calls (to avoid rate limiting)
            
        Returns:
            Dictionary mapping symbols to their historical data
        """
        results = {}
        
        for symbol in symbols:
            print(f"Fetching data for {symbol}...")
            data = self.get_historical_data(symbol, days=days)
            if data:
                results[symbol] = data
            time.sleep(delay)  # Rate limiting
        
        return results


# Example usage
if __name__ == "__main__":
    fetcher = ImprovedCryptoDataFetcher()
    
    # Get top 10 coins
    print("Fetching top 10 coins...")
    top_coins = fetcher.get_top_coins(limit=10)
    for coin in top_coins:
        print(f"{coin['symbol'].upper()}: ${coin['current_price']:,.2f} "
              f"(24h: {coin['price_change_percentage_24h']:+.2f}%)")
    
    # Get historical data for Bitcoin
    print("\nFetching Bitcoin historical data...")
    btc_data = fetcher.get_historical_data('BTC', days=90)
    if btc_data:
        print(f"Retrieved {len(btc_data['prices'])} data points")
        print(f"Latest price: ${btc_data['prices'][-1]:,.2f}")
    
    # Get detailed info
    print("\nFetching detailed Bitcoin info...")
    btc_info = fetcher.get_detailed_coin_info('BTC')
    if btc_info:
        print(f"Market Cap: ${btc_info['market_cap']:,.0f}")
        print(f"All-Time High: ${btc_info['ath']:,.2f} on {btc_info['ath_date']}")
    
    # Get trending coins
    print("\nFetching trending coins...")
    trending = fetcher.get_trending_coins()
    for coin in trending[:5]:
        print(f"- {coin['name']} ({coin['symbol']})")