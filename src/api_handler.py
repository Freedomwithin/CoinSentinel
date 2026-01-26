# src/api_handler.py - Alternative version

import time
from typing import Dict, List, Optional
from pycoingecko import CoinGeckoAPI


class ImprovedCryptoAPIHandler:
    """Base API handler class"""
    
    def __init__(self):
        self.cg = CoinGeckoAPI()
        self.request_count = 0
    
    def get_top_coins(self, limit: int = 100, vs_currency: str = 'usd') -> List[Dict]:
        """Get top cryptocurrencies"""
        try:
            coins = self.cg.get_coins_markets(
                vs_currency=vs_currency,
                per_page=limit,
                page=1
            )
            return coins if coins else []
        except Exception as e:
            print(f"Error: {e}")
            return []
    
    def get_coin_price(self, coin_ids: List[str], vs_currency: str = 'usd') -> Dict:
        """Get current prices"""
        try:
            if not coin_ids:
                return {}
            
            ids = ','.join(coin_ids)
            prices = self.cg.get_price(
                ids=ids,
                vs_currencies=vs_currency
            )
            return prices if prices else {}
        except Exception as e:
            print(f"Error: {e}")
            return {}


class EnhancedCryptoAPIHandler(ImprovedCryptoAPIHandler):
    """Enhanced API handler with rate limiting and additional features"""
    
    def __init__(self):
        super().__init__()
        self.last_request_time = time.time()
        self.min_request_interval = 1.2
    
    def _rate_limit(self):
        """Rate limiting implementation"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last)
        
        self.last_request_time = time.time()
        self.request_count += 1
    
    def get_top_coins(self, limit: int = 100, vs_currency: str = 'usd') -> List[Dict]:
        """Enhanced version with rate limiting"""
        self._rate_limit()
        return super().get_top_coins(limit, vs_currency)
    
    def get_coin_price(self, coin_ids: List[str], vs_currency: str = 'usd') -> Dict:
        """Enhanced version with rate limiting"""
        self._rate_limit()
        return super().get_coin_price(coin_ids, vs_currency)
    
    def get_coin_history(self, coin_id: str, days: int = 90):
        """Get historical data"""
        self._rate_limit()
        try:
            return self.cg.get_coin_ohlc_by_id(
                id=coin_id,
                vs_currency='usd',
                days=days
            )
        except Exception as e:
            print(f"Error: {e}")
            return None
    
    def batch_get_prices(self, coin_ids: List[str], vs_currency: str = 'usd') -> Dict:
        """Batch price fetching"""
        return self.get_coin_price(coin_ids, vs_currency)