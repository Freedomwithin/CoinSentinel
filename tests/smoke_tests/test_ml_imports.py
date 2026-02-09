import sys
sys.path.append("src")
from improved_price_predictor import AdvancedPricePredictor
from main_app_pyqt import EnhancedCryptoAPIHandler

print("Imports successful")
try:
    api = EnhancedCryptoAPIHandler()
    predictor = AdvancedPricePredictor(api)
    print("Predictor instantiated")
except Exception as e:
    print(f"Error: {e}")
