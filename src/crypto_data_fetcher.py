from pycoingecko import CoinGeckoAPI
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CryptoDataFetcher:
    def __init__(self):
        self.cg = CoinGeckoAPI()
        self.coin_list = None

    def get_top_50_coins(self):
        try:
            coins = self.cg.get_coins_markets(
                vs_currency='usd', 
                order='market_cap_desc', 
                per_page=50, 
                page=1, 
                sparkline=False,
                price_change_percentage='24h,7d'
            )
            logger.info(f"Successfully fetched data for {len(coins)} coins")
            self.coin_list = {coin['symbol'].upper(): coin['id'] for coin in coins}
            return coins
        except Exception as e:
            logger.error(f"Error fetching crypto data: {e}")
            return []

    def get_historical_data(self, coin_symbol, days=7):
        try:
            if self.coin_list is None:
                self.get_top_50_coins()
            
            coin_id = self.coin_list.get(coin_symbol.upper())
            if coin_id is None:
                logger.error(f"Coin ID not found for symbol: {coin_symbol}")
                return None

            data = self.cg.get_coin_market_chart_by_id(id=coin_id, vs_currency='usd', days=days)
            prices = [price[1] for price in data['prices']]
            logger.info(f"Successfully fetched historical data for {coin_symbol} ({len(prices)} data points)")
            return prices
        except Exception as e:
            logger.error(f"Error fetching historical data for {coin_symbol}: {e}")
            return None


