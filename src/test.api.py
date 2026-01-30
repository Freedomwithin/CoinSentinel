# test_api.py

from api_handler import EnhancedCryptoAPIHandler

api = EnhancedCryptoAPIHandler()
coins = api.get_top_coins(limit=10, vs_currency="usd")
print(coins)
