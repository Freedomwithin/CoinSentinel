# CoinSentinel

CoinSentinel is an advanced cryptocurrency tracking and analysis application that empowers users to make informed investment decisions with AI-driven insights. Built with Python, CoinSentinel provides a real-time market overview, portfolio management tools, and leverages machine learning to deliver accurate 24-hour and 48-hour price predictions. It also incorporates sentiment analysis to gauge market trends, offers custom price alerts, and aggregates cryptocurrency news to keep users ahead of the curve.

Gain a competitive edge with CoinSentinel's live analytics and predictive capabilities.

## Features

- Real-time market overview
- Portfolio management
- Price prediction using machine learning
- Sentiment analysis
- Custom price alerts
- Cryptocurrency news aggregation

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Freedomwithin/HealingWithMeditation.git
   cd CoinSentinel
   
2. Create and activate a virtual environment:

   ```bash
    python3 -m venv venv
    source venv/bin/activate
3. Upgrade pip (optional but recommended):

   ```bash
    pip install --upgrade pip
4. Install required packages:

   ```bash
    pip install --upgrade -r requirements.txt

## Usage

Run the application

   ```bash
python run.py
   ```

## Project Structure

CoinSentinel/
├── run.py                 # Main entry point
├── requirements.txt       # Dependencies list
├── src/                   # Core application logic
│   ├── api_handler.py
│   ├── crypto_data_fetcher.py
│   ├── portfolio_tracker.py
│   ├── sentiment_tracker.py
│   ├── price_predictor.py
│   └── notification_manager.py
└── gui/                   # User interface components
    └── main_app_pyqt.py


## Additional Options

You can create an executable script to simplify running the project.

1. Windows: You can create a run.bat file with:
   ```bat
   @echo off
   python run.py
   pause
   ```

For macOS users creating a .command file, follow the same steps but name the file run.command. The execution process remains the same.

## Dependencies

See `requirements.txt` for a full list of dependencies.
Note: If using scikit-learn, make sure sklearn is not in your requirements; use scikit-learn instead.

## Contributing

Contributions, issues, and feature requests are welcome!

 ## License
This project is licensed under the MIT License - see the LICENSE.md file for details.


