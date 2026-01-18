from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import MinMaxScaler

def create_price_predictor_model():
    return LinearRegression(), MinMaxScaler(feature_range=(0, 1))