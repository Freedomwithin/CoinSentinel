# CoinSentinel 🚀

**Advanced Cryptocurrency Tracking & AI-Powered Price Prediction**

CoinSentinel is a professional-grade cryptocurrency tracking and analysis application that empowers traders and investors to make data-driven decisions. Built with Python and PyQt5, CoinSentinel combines real-time market data, advanced machine learning predictions, comprehensive portfolio management, and market sentiment analysis in one powerful desktop application.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)

---

## ✨ Features

### 📊 **Market Overview**
- Real-time data for top 50+ cryptocurrencies
- Live price tracking with 24h/7d change indicators
- Market cap and volume statistics
- Sortable and filterable data tables
- Export market data to CSV

### 💼 **Advanced Portfolio Management**
- Track multiple cryptocurrency holdings
- Automated profit/loss calculations (realized & unrealized)
- Weighted average purchase price tracking
- Buy/sell transaction history
- Portfolio diversity score
- Risk metrics (Sharpe ratio, volatility)
- CSV export functionality

### 🔮 **AI-Powered Price Predictions**
- **Ensemble Machine Learning Models**:
  - Random Forest Regressor
  - Gradient Boosting Regressor
- **Advanced Technical Indicators** (20+ features):
  - RSI (Relative Strength Index)
  - MACD (Moving Average Convergence Divergence)
  - Bollinger Bands
  - Moving Averages (SMA, EMA)
  - Price Momentum & Volatility
  - Volume Analysis
- **90 days** of historical data for training
- Confidence intervals with predictions
- Visual prediction charts

### 📈 **Market Sentiment Analysis**
- **Live Fear & Greed Index** integration
- Overall market sentiment scoring
- Gainers vs. Losers analysis
- Market distribution visualization
- Text-based sentiment analysis
- Market-based sentiment indicators

### ⭐ **Watchlist & Alerts**
- Custom watchlist creation
- Real-time price monitoring
- Desktop notifications
- Email alerts (optional)
- Price alert threshold settings

### 📊 **Analytics & Visualization**
- 30-day price history charts
- Interactive data visualizations
- Technical indicator overlays
- Portfolio performance graphs
- Market distribution pie charts

### 🎨 **User Interface**
- Clean, modern PyQt5 interface
- Light & Dark theme support
- Multi-tab organization
- Real-time data updates
- Progress indicators
- Responsive design

---

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager
- Virtual environment (recommended)

### Step-by-Step Guide

1. **Clone the repository:**
```bash# CoinSentinel 🚀

**Advanced Cryptocurrency Tracking & AI-Powered Price Prediction**

CoinSentinel is a professional-grade cryptocurrency tracking and analysis application that empowers traders and investors to make data-driven decisions. Built with Python and PyQt5, CoinSentinel combines real-time market data, advanced machine learning predictions, comprehensive portfolio management, and market sentiment analysis in one powerful desktop application.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)

---

## ✨ Features

### 📊 **Market Overview**
- Real-time data for top 50+ cryptocurrencies
- Live price tracking with 24h/7d change indicators
- Market cap and volume statistics
- Sortable and filterable data tables
- Export market data to CSV

### 💼 **Advanced Portfolio Management**
- Track multiple cryptocurrency holdings
- Automated profit/loss calculations (realized & unrealized)
- Weighted average purchase price tracking
- Buy/sell transaction history
- Portfolio diversity score
- Risk metrics (Sharpe ratio, volatility)
- CSV export functionality

### 🔮 **AI-Powered Price Predictions**
- **Ensemble Machine Learning Models**:
  - Random Forest Regressor
  - Gradient Boosting Regressor
- **Advanced Technical Indicators** (20+ features):
  - RSI (Relative Strength Index)
  - MACD (Moving Average Convergence Divergence)
  - Bollinger Bands
  - Moving Averages (SMA, EMA)
  - Price Momentum & Volatility
  - Volume Analysis
- **90 days** of historical data for training
- Confidence intervals with predictions
- Visual prediction charts

### 📈 **Market Sentiment Analysis**
- **Live Fear & Greed Index** integration
- Overall market sentiment scoring
- Gainers vs. Losers analysis
- Market distribution visualization
- Text-based sentiment analysis
- Market-based sentiment indicators

### ⭐ **Watchlist & Alerts**
- Custom watchlist creation
- Real-time price monitoring
- Desktop notifications
- Email alerts (optional)
- Price alert threshold settings

### 📊 **Analytics & Visualization**
- 30-day price history charts
- Interactive data visualizations
- Technical indicator overlays
- Portfolio performance graphs
- Market distribution pie charts

### 🎨 **User Interface**
- Clean, modern PyQt5 interface
- Light & Dark theme support
- Multi-tab organization
- Real-time data updates
- Progress indicators
- Responsive design

---

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager
- Virtual environment (recommended)

### Step-by-Step Guide

1. **Clone the repository:**
```bash
   git clone https://github.com/YourUsername/CoinSentinel.git
   cd CoinSentinel
```

2. **Create and activate a virtual environment:**

   **Windows:**
```bash
   python -m venv venv
   venv\Scripts\activate
```

   **macOS/Linux:**
```bash
   python3 -m venv venv
   source venv/bin/activate
```

3. **Upgrade pip:**
```bash
   pip install --upgrade pip
```

4. **Install dependencies:**
```bash
   pip install -r requirements.txt
```

---

## 💻 Usage

### Running the Application

**Method 1: Direct Python**
```bash
python run.py
```

**Method 2: From src directory**
```bash
cd src
python main_app_pyqt.py
```

### First Launch
1. The application will fetch initial market data (may take 10-20 seconds)
2. Navigate through tabs to explore different features
3. Add coins to your portfolio or watchlist
4. Try making a price prediction!

---

## 📁 Project Structure
```
CoinSentinel/
├── run.py                          # Main entry point
├── requirements.txt                # Python dependencies
├── README.md                       # This file
├── LICENSE.md                      # MIT License
├── .gitignore                      # Git ignore rules
│
├── src/                            # Core application modules
│   ├── main_app_pyqt.py           # Main GUI application
│   ├── api_handler.py             # CoinGecko API wrapper
│   ├── crypto_data_fetcher.py     # Data fetching utilities
│   ├── price_predictor.py         # ML prediction engine
│   ├── portfolio_tracker.py       # Portfolio management
│   ├── sentiment_tracker.py       # Sentiment analysis
│   ├── notification_manager.py    # Alert system
│   └── utils.py                   # Helper functions
│
└── data/                          # Auto-generated data files
    ├── portfolio_default.json     # Portfolio data
    ├── transactions_default.json  # Transaction history
    └── sentiment_cache.json       # Sentiment cache
```

---

## 🛠️ Technologies Used

### Core Technologies
- **Python 3.8+** - Primary programming language
- **PyQt5** - Desktop GUI framework
- **NumPy** - Numerical computing
- **Pandas** - Data manipulation and analysis
- **Matplotlib** - Data visualization

### Machine Learning
- **scikit-learn** - ML models (Random Forest, Gradient Boosting)
- **SciPy** - Scientific computing

### APIs & Data
- **pycoingecko** - CoinGecko API client
- **requests** - HTTP library
- **Alternative.me** - Fear & Greed Index

### Notifications
- **plyer** - Cross-platform desktop notifications
- **smtplib** - Email notifications (built-in)

---

## 📊 Machine Learning Details

### Prediction Models
CoinSentinel uses an **ensemble approach** combining:
- **Random Forest Regressor** (100 estimators)
- **Gradient Boosting Regressor** (100 estimators)

### Feature Engineering
Each prediction uses **20+ technical indicators**:
- **Moving Averages**: SMA (7, 14, 30), EMA (7, 14)
- **Momentum Indicators**: RSI, MACD, Price Momentum
- **Volatility Metrics**: Bollinger Bands, Standard Deviation
- **Volume Analysis**: Volume ratios, Price-Volume correlation
- **Price Position**: Relative to highs/lows

### Training Data
- **90 days** of historical OHLCV data
- Automatic feature scaling
- Train/test split for validation
- Confidence intervals on predictions

---

## ⚙️ Configuration

### Email Notifications (Optional)
Edit `src/notification_manager.py` to configure email alerts:
```python
email_config = {
    'smtp_server': 'smtp.gmail.com',
    'port': 587,
    'sender_email': 'your-email@gmail.com',
    'password': 'your-app-password',  # Use app-specific password
    'use_tls': True
}
```

### API Rate Limits
The application includes built-in rate limiting for CoinGecko API:
- Default: 1.2 seconds between requests
- Configurable in `api_handler.py`

---

## 📖 Usage Examples

### Adding to Portfolio
1. Navigate to the **Portfolio** tab
2. Select a coin from the dropdown
3. Enter amount and purchase price
4. Click **Add** button
5. Your portfolio updates automatically with P/L calculations

### Making Predictions
1. Go to the **Predictions** tab
2. Select a cryptocurrency
3. Click **Predict Price**
4. View 24-hour prediction with confidence intervals
5. Analyze the prediction chart

### Tracking Sentiment
1. Open the **Sentiment** tab
2. View live Fear & Greed Index
3. See market gainers/losers distribution
4. Refresh for latest data

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/AmazingFeature`)
3. **Commit your changes** (`git commit -m 'Add some AmazingFeature'`)
4. **Push to the branch** (`git push origin feature/AmazingFeature`)
5. **Open a Pull Request**

### Areas for Contribution
- Additional ML models (LSTM, Prophet)
- More technical indicators
- News aggregation integration
- Social media sentiment analysis
- Additional exchange integrations
- Mobile version
- Web dashboard

---

## 🐛 Known Issues

- Large portfolio datasets may slow down UI refresh
- API rate limiting may cause delays with frequent updates
- Email notifications require SMTP configuration

---

## 📝 Future Roadmap

- [ ] LSTM neural networks for predictions
- [ ] News sentiment integration
- [ ] Twitter/Reddit sentiment analysis
- [ ] Multi-exchange support
- [ ] Backtesting framework
- [ ] Mobile companion app
- [ ] Cloud sync for multi-device
- [ ] Advanced charting (candlesticks, patterns)

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE.md](LICENSE.md) file for details.

Copyright (c) 2025 Freedom Within

---

## 🙏 Acknowledgments

- **CoinGecko API** - Comprehensive cryptocurrency data
- **Alternative.me** - Fear & Greed Index
- **PyQt5** - Powerful GUI framework
- **scikit-learn** - Machine learning tools
- The open-source community

---

## 📧 Contact & Support

- **Issues**: [GitHub Issues](https://github.com/YourUsername/CoinSentinel/issues)
- **Discussions**: [GitHub Discussions](https://github.com/YourUsername/CoinSentinel/discussions)

---

## ⚠️ Disclaimer

**This software is for educational and informational purposes only.** 

Cryptocurrency trading involves substantial risk of loss. The predictions and analyses provided by CoinSentinel should not be considered financial advice. Always do your own research and consult with financial professionals before making investment decisions.

The developers of CoinSentinel are not responsible for any financial losses incurred through the use of this application.

---

## 📊 Screenshots

*Coming soon - Add screenshots of your application here*

---

**Made with ❤️ for the crypto community**

*Star ⭐ this repo if you find it helpful!*