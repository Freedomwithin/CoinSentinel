# src/api_handler.py - Alternative version

import time
from typing import Dict, List, Optional
from pycoingecko import CoinGeckoAPI


# In api_handler.py
class EnhancedCryptoAPIHandler:
    def __init__(self):
        self.cg = CoinGeckoAPI()

    def get_top_coins(self, limit=100, vs_currency="usd"):
        """Get top cryptocurrencies by market cap"""
        try:
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
