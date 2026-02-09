import sys
sys.path.append("src")
from improved_price_predictor import AdvancedPricePredictor
# Mock API handler
class MockAPI:
    def get_coin_history(self, coin_id, days):
        return None

print("ML Imports successful")
predictor = AdvancedPricePredictor(MockAPI())
print("Predictor instantiated")
