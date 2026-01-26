from pycoingecko import CoinGeckoAPI
import pandas as pd
import time
from functools import wraps
import requests

class ImprovedCryptoAPIHandler:
    def __init__(self):
        self.cg = CoinGeckoAPI()
        self.rate_limit_delay = 1.2  # Seconds between requests to avoid rate limiting
        self.last_request_time = 0
        self.coin_id_cache = {}
        
    def _rate_limit(func):
        """Decorator to enforce rate limiting on API calls"""
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            elapsed = time.time() - self.last_request_time
            if elapsed < self.rate_limit_delay:
                time.sleep(self.rate_limit_delay - elapsed)
            
            try:
                result = func(self, *args, **kwargs)
                self.last_request_time = time.time()
                return result
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429:  # Rate limit exceeded
                    print("Rate limit exceeded. Waiting 60 seconds...")
                    time.sleep(60)
                    return func(self, *args, **kwargs)
                else:
                    raise
            except Exception as e:
                print(f"API Error in {func.__name__}: {e}")
                return None
                
        return wrapper
    
    def get_coin_id_from_symbol(self, symbol):
        """
        Convert coin symbol to CoinGecko ID with caching.
        
        Args:
            symbol: Coin symbol (e.g., 'BTC', 'ETH')
            
        Returns:
            CoinGecko coin ID or None
        """
        symbol = symbol.lower()
        
        # Check cache first
        if symbol in self.coin_id_cache:
            return self.coin_id_cache[symbol]
        
        # Common symbol to ID mappings
        common_mappings = {
            'btc': 'bitcoin',
            'eth': 'ethereum',
            'usdt': 'tether',
            'bnb': 'binancecoin',
            'sol': 'solana',
            'usdc': 'usd-coin',
            'xrp': 'ripple',
            'ada': 'cardano',
            'doge': 'dogecoin',
            'avax': 'avalanche-2',
            'dot': 'polkadot',
            'matic': 'matic-network',
            'link': 'chainlink',
            'uni': 'uniswap',
            'atom': 'cosmos',
            'ltc': 'litecoin',
            'etc': 'ethereum-classic',
            'xlm': 'stellar',
            'algo': 'algorand',
            'vet': 'vechain',
            'trx': 'tron',
            'fil': 'filecoin',
            'icp': 'internet-computer',
            'apt': 'aptos',
            'arb': 'arbitrum',
            'op': 'optimism'
        }
        
        if symbol in common_mappings:
            coin_id = common_mappings[symbol]
            self.coin_id_cache[symbol] = coin_id
            return coin_id
        
        # Search in coins list
        try:
            coins_list = self.cg.get_coins_list()
            for coin in coins_list:
                if coin['symbol'].lower() == symbol:
                    self.coin_id_cache[symbol] = coin['id']
                    return coin['id']
        except Exception as e:
            print(f"Error finding coin ID for {symbol}: {e}")
        
        return None
    
    @_rate_limit
    def get_top_coins(self, limit=50, vs_currency='usd', include_sparkline=True):
        """
        Get top cryptocurrencies by market cap.
        
        Args:
            limit: Number of coins to retrieve
            vs_currency: Currency for prices
            include_sparkline: Include 7-day price sparkline
            
        Returns:
            List of coin data dictionaries
        """
        try:
            return self.cg.get_coins_markets(
                vs_currency=vs_currency,
                order='market_cap_desc',
                per_page=limit,
                page=1,
                sparkline=include_sparkline,
                price_change_percentage='1h,24h,7d,30d,1y'
            )
        except Exception as e:
            print(f"Error fetching top coins: {e}")
            return []
    
    @_rate_limit
    def get_historical_prices(self, coin_id, days=30, vs_currency='usd'):
        """
        Get historical price data for a coin.
        
        Args:
            coin_id: CoinGecko coin ID
            days: Number of days of historical data
            vs_currency: Currency for prices
            
        Returns:
            Dictionary with prices, volumes, and market_caps
        """
        try:
            data = self.cg.get_coin_market_chart_by_id(
                id=coin_id,
                vs_currency=vs_currency,
                days=days
            )
            return data
        except Exception as e:
            print(f"Error fetching historical prices for {coin_id}: {e}")
            return None
    
    @_rate_limit
    def get_ohlc_data(self, coin_id, days=7, vs_currency='usd'):
        """
        Get OHLC (Open, High, Low, Close) data.
        
        Args:
            coin_id: CoinGecko coin ID
            days: Number of days (1, 7, 14, 30, 90, 180, 365, or max)
            vs_currency: Currency for prices
            
        Returns:
            List of [timestamp, open, high, low, close]
        """
        try:
            # OHLC only available for specific day ranges
            valid_days = [1, 7, 14, 30, 90, 180, 365]
            if days not in valid_days:
                days = min(valid_days, key=lambda x: abs(x - days))
            
            data = self.cg.get_coin_ohlc_by_id(
                id=coin_id,
                vs_currency=vs_currency,
                days=days
            )
            return data
        except Exception as e:
            print(f"Error fetching OHLC data for {coin_id}: {e}")
            return None
    
    @_rate_limit
    def get_coin_details(self, coin_id):
        """
        Get detailed information about a specific coin.
        
        Args:
            coin_id: CoinGecko coin ID
            
        Returns:
            Dictionary with detailed coin information
        """
        try:
            data = self.cg.get_coin_by_id(
                id=coin_id,
                localization=False,
                tickers=False,
                market_data=True,
                community_data=True,
                developer_data=True,
                sparkline=False
            )
            return data
        except Exception as e:
            print(f"Error fetching details for {coin_id}: {e}")
            return None
    
    @_rate_limit
    def get_trending_coins(self):
        """
        Get currently trending coins.
        
        Returns:
            List of trending coin data
        """
        try:
            data = self.cg.get_search_trending()
            return data.get('coins', [])
        except Exception as e:
            print(f"Error fetching trending coins: {e}")
            return []
    
    @_rate_limit
    def get_global_data(self):
        """
        Get global cryptocurrency market data.
        
        Returns:
            Dictionary with global market statistics
        """
        try:
            return self.cg.get_global()
        except Exception as e:
            print(f"Error fetching global data: {e}")
            return {}
    
    @_rate_limit
    def get_coin_price(self, coin_ids, vs_currencies='usd', include_24h_change=True):
        """
        Get current price for one or more coins.
        
        Args:
            coin_ids: Single coin ID or list of coin IDs
            vs_currencies: Currency or list of currencies
            include_24h_change: Include 24h price change
            
        Returns:
            Dictionary with price data
        """
        try:
            if isinstance(coin_ids, str):
                coin_ids = [coin_ids]
            if isinstance(vs_currencies, str):
                vs_currencies = [vs_currencies]
            
            return self.cg.get_price(
                ids=coin_ids,
                vs_currencies=vs_currencies,
                include_24hr_change=include_24h_change,
                include_24hr_vol=True,
                include_market_cap=True
            )
        except Exception as e:
            print(f"Error fetching prices: {e}")
            return {}
    
    def get_historical_data_dataframe(self, coin_id, days=30, vs_currency='usd'):
        """
        Get historical data as a pandas DataFrame.
        
        Args:
            coin_id: CoinGecko coin ID
            days: Number of days
            vs_currency: Currency
            
        Returns:
            DataFrame with timestamp, price, volume, market_cap
        """
        data = self.get_historical_prices(coin_id, days, vs_currency)
        
        if not data:
            return None
        
        try:
            df = pd.DataFrame({
                'timestamp': [p[0] for p in data['prices']],
                'price': [p[1] for p in data['prices']],
                'volume': [v[1] for v in data['total_volumes']],
                'market_cap': [m[1] for m in data['market_caps']]
            })
            
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df = df.set_index('timestamp')
            
            return df
        except Exception as e:
            print(f"Error creating DataFrame: {e}")
            return None
    
    def get_ohlc_dataframe(self, coin_id, days=7, vs_currency='usd'):
        """
        Get OHLC data as a pandas DataFrame.
        
        Args:
            coin_id: CoinGecko coin ID
            days: Number of days
            vs_currency: Currency
            
        Returns:
            DataFrame with timestamp, open, high, low, close
        """
        data = self.get_ohlc_data(coin_id, days, vs_currency)
        
        if not data:
            return None
        
        try:
            df = pd.DataFrame(
                data,
                columns=['timestamp', 'open', 'high', 'low', 'close']
            )
            
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df = df.set_index('timestamp')
            
            return df
        except Exception as e:
            print(f"Error creating OHLC DataFrame: {e}")
            return None
    
    def batch_get_prices(self, symbols, vs_currency='usd'):
        """
        Get current prices for multiple symbols efficiently.
        
        Args:
            symbols: List of coin symbols
            vs_currency: Currency for prices
            
        Returns:
            Dictionary mapping symbols to price data
        """
        # Convert symbols to IDs
        coin_ids = []
        symbol_to_id = {}
        
        for symbol in symbols:
            coin_id = self.get_coin_id_from_symbol(symbol)
            if coin_id:
                coin_ids.append(coin_id)
                symbol_to_id[symbol.upper()] = coin_id
        
        if not coin_ids:
            return {}
        
        # Get prices for all coins in one request
        prices = self.get_coin_price(coin_ids, vs_currency)
        
        # Map back to symbols
        result = {}
        for symbol, coin_id in symbol_to_id.items():
            if coin_id in prices:
                result[symbol] = prices[coin_id]
        
        return result
    
    def get_fear_greed_index(self):
        """
        Get crypto Fear & Greed Index from alternative.me API.
        Note: This is not from CoinGecko but is useful for sentiment.
        
        Returns:
            Dictionary with fear & greed data
        """
        try:
            response = requests.get('https://api.alternative.me/fng/')
            if response.status_code == 200:
                data = response.json()
                return data.get('data', [{}])[0]
            return None
        except Exception as e:
            print(f"Error fetching Fear & Greed Index: {e}")
            return None


# Example usage
if __name__ == "__main__":
    api = ImprovedCryptoAPIHandler()
    
    # Get top 10 coins
    print("=== Top 10 Coins ===")
    top_coins = api.get_top_coins(limit=10)
    for coin in top_coins[:5]:
        print(f"{coin['symbol'].upper()}: ${coin['current_price']:,.2f} "
              f"(24h: {coin.get('price_change_percentage_24h', 0):+.2f}%)")
    
    # Get Bitcoin historical data
    print("\n=== Bitcoin Historical Data ===")
    btc_df = api.get_historical_data_dataframe('bitcoin', days=30)
    if btc_df is not None:
        print(f"Data points: {len(btc_df)}")
        print(f"Latest price: ${btc_df['price'].iloc[-1]:,.2f}")
        print(f"Avg volume: ${btc_df['volume'].mean():,.0f}")
    
    # Get OHLC data
    print("\n=== Bitcoin OHLC Data ===")
    btc_ohlc = api.get_ohlc_dataframe('bitcoin', days=7)
    if btc_ohlc is not None:
        print(btc_ohlc.tail())
    
    # Get trending coins
    print("\n=== Trending Coins ===")
    trending = api.get_trending_coins()
    for coin in trending[:5]:
        item = coin.get('item', {})
        print(f"- {item.get('name')} ({item.get('symbol')})")
    
    # Get Fear & Greed Index
    print("\n=== Fear & Greed Index ===")
    fgi = api.get_fear_greed_index()
    if fgi:
        print(f"Value: {fgi.get('value')} - {fgi.get('value_classification')}")
    
    # Batch get prices
    print("\n=== Batch Price Check ===")
    prices = api.batch_get_prices(['BTC', 'ETH', 'SOL', 'ADA'])
    for symbol, data in prices.items():
        print(f"{symbol}: ${data.get('usd', 0):,.2f}")