import numpy as np
from src.utils import create_price_predictor_model

class PricePredictor:
    def __init__(self, look_back=7):
        self.look_back = look_back
        self.model, self.scaler = create_price_predictor_model()

    def prepare_data(self, data):
        scaled_data = self.scaler.fit_transform(data.reshape(-1, 1))
        X, y = [], []
        for i in range(len(scaled_data) - self.look_back):
            X.append(scaled_data[i:i + self.look_back])
            y.append(scaled_data[i + self.look_back])
        return np.array(X), np.array(y)

    def predict_next_price(self, historical_prices):
        try:
            if len(historical_prices) < self.look_back + 1:
                print("Not enough data to make a prediction.")
                return None, None

            print("Preparing data...")
            X, y = self.prepare_data(historical_prices)
            X_reshaped = X.reshape(X.shape[0], -1)
            print("Data prepared. Fitting model...")
            self.model.fit(X_reshaped, y)

            last_sequence = X[-1].reshape(1, -1)
            predicted_scaled = self.model.predict(last_sequence)
            predicted_price = self.scaler.inverse_transform(predicted_scaled.reshape(-1, 1))[0][0]

            last_actual_price = historical_prices[-1]
            percentage_change = ((predicted_price - last_actual_price) / last_actual_price) * 100

            print(f"Predicted next price: ${predicted_price:.2f}")
            print(f"Percentage change: {percentage_change:.2f}%")

            return predicted_price, percentage_change

        except Exception as e:
            print(f"An error occurred during prediction: {e}")
            return None, None

# Example usage
if __name__ == "__main__":
    sample_prices = np.random.rand(10) * 100 + 1000

    predictor = PricePredictor()
    next_price, percentage_change = predictor.predict_next_price(sample_prices)
    if next_price is not None:
        print(f"Predicted next price: ${next_price:.2f}")
        print(f"Percentage change: {percentage_change:.2f}%")
    else:
        print("Not enough data to make a prediction.")