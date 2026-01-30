<h1 style="text-align: center;"> CoinSentinel </h1>

**Advanced Cryptocurrency Tracking & AI-Powered Price Prediction**

CoinSentinel is a professional-grade cryptocurrency tracking and analysis application that empowers traders and investors to make data-driven decisions. Built with Python and PyQt5, CoinSentinel combines real-time market data, advanced machine learning predictions, comprehensive portfolio management, and market sentiment analysis in one powerful desktop application.

## Recent Updates (January 2026)

### Enhanced Portfolio Management
- **Added Currency Selector**: Users can now view portfolio values in USD, EUR, GBP, or JPY
- **Profit/Loss Column**: Dedicated column showing PnL for each asset with color coding (green for profit, red for loss)
- **Export Functionality**: Export portfolio data to CSV for further analysis
- **Improved Error Handling**: More robust error messages and user feedback
- **Status Bar Updates**: Shows total PnL with color coding

### Advanced Price Predictions
- **Time Frame Selection**: Predict price movements for 24 hours, 7 days, or 30 days
- **Enhanced Prediction Details**: Shows current price, predicted price, percentage change, confidence score, and direction
- **Prediction Strength**: Indicates strong, moderate, or weak predictions
- **Improved Insights**: More detailed technical analysis insights
- **Visual Improvements**: Color-coded results and better organized information display

### Improved UI/UX
- **Better Layout**: Improved organization of prediction results
- **Progress Feedback**: Clear progress updates during prediction
- **Rich Text Formatting**: Color-coded results for better visual feedback

## Quick Start

### Windows Users (Recommended):
Download and install CoinSentinel Setup 1.0.0.exe from Releases.

### Python Developers:
```bash
git clone https://github.com/Freedomwithin/CoinSentinel.git
cd CoinSentinel
pip install -r requirements.txt
python run.py
```
Key Features
## Market Overview
- Real-time data for 50+ cryptocurrencies from CoinGecko API 
- Live price tracking with 24h/7d change indicators
- Market cap, volume, and price statistics
- Sortable and filterable data tables
- CSV export functionality
- 
  ##Portfolio Management
- Track multiple cryptocurrency holdings
- Automated profit/loss calculations (realized & unrealized)
- Weighted average purchase price tracking
- Buy/sell transaction history
- Portfolio diversity analysis
- CSV import/export
- Multi-currency support (USD, EUR, GBP, JPY)

## AI Price Predictions
- Ensemble machine learning models (Random Forest + Gradient Boosting)
- 20+ technical indicators including RSI, MACD, Bollinger Bands
- Configurable training windows (24h, 7d, 30d)
- Price predictions with confidence intervals
- Prediction strength indicators
- Interactive prediction charts
- Detailed technical analysis insights
## Market Sentiment
- Live Fear & Greed Index integration
- Gainers vs losers analysis
- Market distribution visualization
- Real-time sentiment scoring
- 
## Additional Features
- Custom watchlists with price alerts
- Desktop notifications
- Multi-tab PyQt5 interface
- Light/dark theme support
- Real-time data updates

## Technical Architecture

```text
CoinSentinel/
├── run.py                    # Main entry point
├── requirements.txt          # Python dependencies
├── src/
│   ├── main_app_pyqt.py      # Main GUI application
│   ├── api_handler.py        # CoinGecko API wrapper
│   ├── crypto_data_fetcher.py# Data utilities
│   ├── price_predictor.py    # ML prediction engine
│   ├── portfolio_tracker.py  # Portfolio management
│   ├── sentiment_tracker.py  # Sentiment analysis
│   ├── notification_manager.py# Alert system
│   └── utils.py              # Helper functions
└── data/                    # Generated data files
```

## Technology Stack

### Core:

- Python 3.8+, PyQt5 (GUI framework)
- NumPy, Pandas (data processing)
- Matplotlib (visualizations)
### Machine Learning:
-scikit-learn (Random Forest, Gradient Boosting Regressor)

### APIs & Data:

- pycoingecko (CoinGecko API client)
- Alternative.me (Fear & Greed Index)
### Notifications:

- plyer (cross-platform desktop notifications)
## Installation (Development)
### Prerequisites

- Python 3.11 or higher
- pip package manager
- Virtual environment recommended

### Setup Steps
```bash
git clone https://github.com/Freedomwithin/CoinSentinel.git
cd CoinSentinel

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

pip install --upgrade pip
pip install -r requirements.txt

python run.py
```

## Usage Examples
### Portfolio Setup

1. Open Portfolio tab
2. Select cryptocurrency from dropdown
3. Enter purchase amount and price
4. Click "Add to Portfolio"
5. View real-time P/L calculations in your preferred currency

### Price Predictions

1. Navigate to Predictions tab
2. Select cryptocurrency
3. Choose time frame (24 hours, 7 days, or 30 days)
4. Click "Generate Prediction"
5. Review forecast with confidence intervals and strength indicators

### Market Monitoring

1. Market Overview tab shows live prices
2. Sort by 24h change, volume, or market cap
3. Export current data to CSV
## Machine Learning Details
### Models:

- Random Forest Regressor (100 estimators)
- Gradient Boosting Regressor (100 estimators)
- Ensemble approach with weighted predictions
### Features (20+ indicators):

- Technical: RSI, MACD, Bollinger Bands, SMA/EMA
- Momentum: Price momentum, rate of change
- Volatility: Standard deviation, ATR
- Volume: Volume ratios, price-volume correlation
- Training: Configurable historical data windows with automatic feature scaling
### Configuration

-API Rate Limits: Built-in 1.2s delay between CoinGecko requests (configurable)
Notifications: Desktop notifications enabled by default. Email alerts optional via notification_manager.py.
## Building from Source (Electron Version)
A Windows executable is also available via Electron build:
```bash

cd CoinSentinel-Electron
npm install
npm run build-react
npm run dist\:win
```
## Contributing

1. Fork the repository
2. Create feature branch: git checkout -b feature/YourFeature
3. Commit changes: git commit -m "Add YourFeature"
4. Push branch: git push origin feature/YourFeature
5. Open Pull Request
## Priority Areas for Future Development:

1. Additional ML models (LSTM, Prophet)
2. Exchange integrations (Binance, Coinbase)
3. Backtesting framework
4. Mobile companion app
5. Advanced charting tools
6. Customizable alerts and notifications

## License
MIT License - see LICENSE.md
Copyright (c) 2026 FreedomWithin
## Support

- Issues: GitHub Issues
- Feature requests: GitHub Discussions
## Disclaimer
- For educational and informational purposes only. Cryptocurrency trading involves substantial risk. Predictions are not financial advice. Always conduct your own research.

Professional cryptocurrency analysis tool for traders and investors.

Feature requests: GitHub Discussions

## Disclaimer
For educational and informational purposes only. Cryptocurrency trading involves substantial risk. Predictions are not financial advice. Always conduct your own research.

Professional cryptocurrency analysis tool for traders and investors.