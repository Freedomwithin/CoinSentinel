from pycoingecko import CoinGeckoAPI
import pandas as pd

class CryptoAPIHandler:
    def __init__(self):
        self.cg = CoinGeckoAPI()
    
    def get_top_coins(self, limit=50):
        return self.cg.get_coins_markets(
            vs_currency='usd', 
            order='market_cap_desc', 
            per_page=limit,
            sparkline=False
        )
    
    def get_historical_prices(self, coin_id, days=30):
        return self.cg.get_coin_market_chart_by_id(
            id=coin_id, 
            vs_currency='usd', 
            days=days
        )

