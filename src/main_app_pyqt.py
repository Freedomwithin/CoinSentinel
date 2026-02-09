# src/main_app_pyqt.py

import sys
import pandas as pd
import numpy as np
import time
from pycoingecko import CoinGeckoAPI
from datetime import datetime, timedelta
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QPushButton,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QHeaderView,
    QStatusBar,
    QTabWidget,
    QTextEdit,
    QSplitter,
    QProgressBar,
    QGroupBox,
    QFormLayout,
    QLineEdit,
    QDoubleSpinBox,
    QMessageBox,
    QFileDialog,
    QDialog,
    QDialogButtonBox,
    QGridLayout,
    QScrollArea,  # ADD THIS
    QFrame,       # ADD THIS
    QListWidget,  # ADD THIS
    QListWidgetItem,  # ADD THIS
    QMenu,        # ADD THIS
)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt5.QtGui import QBrush, QColor, QFont, QPalette, QPixmap  # ADD QPixmap
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib
import requests
from io import BytesIO

matplotlib.use("Qt5Agg")


from improved_price_predictor import AdvancedPricePredictor
from improved_portfolio_tracker import PortfolioTracker
from improved_sentiment_tracker import SentimentTracker

class EnhancedCryptoAPIHandler:
    """Enhanced API handler with rate limiting and search functionality"""

    def __init__(self):
        self.cg = CoinGeckoAPI()
        self.last_request_time = time.time()
        self.min_request_interval = 1.2

    def _rate_limit(self):
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last)
        self.last_request_time = time.time()

    def get_coin_price(self, coin_ids, vs_currency="usd"):
        self._rate_limit()
        try:
            return self.cg.get_price(ids=",".join(coin_ids), vs_currencies=vs_currency)
        except Exception as e:
            print(f"Price Error: {e}")
            return {}

    def search_coins(self, query):
        """Search for coins by name or symbol"""
        self._rate_limit()
        try:
            search_results = self.cg.search(query)
            if search_results and "coins" in search_results:
                return search_results.get("coins", [])[:20]
            return []
        except Exception as e:
            print(f"Search error: {e}")
            return []


class PredictionWorker(QThread):
    """Worker thread for ML predictions"""

    prediction_complete = pyqtSignal(dict)
    progress_update = pyqtSignal(int, str)
    error_occurred = pyqtSignal(str)

    def __init__(self, predictor, coin_id, current_price):
        super().__init__()
        self.predictor = predictor
        self.coin_id = coin_id
        self.current_price = current_price

    def run(self):
        try:
            self.progress_update.emit(25, "Fetching historical data...")
            # Add small delay to show progress
            self.msleep(500)

            self.progress_update.emit(50, "Processing technical indicators...")
            self.msleep(500)
            self.progress_update.emit(75, "Running ML models...")
            result = self.predictor.predict_price(self.coin_id, self.current_price)
            self.progress_update.emit(100, "Prediction complete")
            self.prediction_complete.emit(result)
        except Exception as e:
            self.error_occurred.emit(f"Prediction error: {str(e)}")



class EnhancedCryptoAPIHandler:
    """Enhanced API handler with rate limiting and search functionality"""

    def __init__(self):
        self.cg = CoinGeckoAPI()
        self.last_request_time = time.time()
        self.min_request_interval = 1.2

    def _rate_limit(self):
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last)
        self.last_request_time = time.time()

    def get_coin_price(self, coin_ids, vs_currency="usd"):
        self._rate_limit()
        try:
            return self.cg.get_price(ids=",".join(coin_ids), vs_currencies=vs_currency)
        except Exception as e:
            print(f"Price Error: {e}")
            return {}

    def search_coins(self, query):
        """Search for coins by name or symbol"""
        self._rate_limit()
        try:
            search_results = self.cg.search(query)
            if search_results and "coins" in search_results:
                return search_results.get("coins", [])[:20]
            return []
        except Exception as e:
            print(f"Search error: {e}")
            return []

class AddTransactionDialog(QDialog):
    """Dialog for adding portfolio transactions"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Transaction")
        self.setModal(True)
        self.init_ui()

    def init_ui(self):
        layout = QGridLayout()

        # Coin selection
        layout.addWidget(QLabel("Coin:"), 0, 0)
        self.coin_combo = QComboBox()
        layout.addWidget(self.coin_combo, 0, 1)
        # Transaction type
        layout.addWidget(QLabel("Type:"), 1, 0)
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Buy", "Sell"])
        layout.addWidget(self.type_combo, 1, 1)
        # Amount
        layout.addWidget(QLabel("Amount:"), 2, 0)
        self.amount_input = QDoubleSpinBox()
        self.amount_input.setRange(0.00000001, 1000000)
        self.amount_input.setDecimals(8)
        layout.addWidget(self.amount_input, 2, 1)
        # Price per coin
        layout.addWidget(QLabel("Price per Coin:"), 3, 0)
        self.price_input = QDoubleSpinBox()
        self.price_input.setRange(0.00000001, 1000000)
        self.price_input.setDecimals(4)
        self.price_input.setPrefix("$")
        layout.addWidget(self.price_input, 3, 1)
        # Date
        layout.addWidget(QLabel("Date:"), 4, 0)
        self.date_input = QLineEdit(datetime.now().strftime("%Y-%m-%d"))
        layout.addWidget(self.date_input, 4, 1)
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel, Qt.Horizontal, self
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons, 5, 0, 1, 2)
        self.setLayout(layout)
        self.resize(300, 200)

    def get_data(self):
        return {
            "coin": self.coin_combo.currentData(),
            "type": self.type_combo.currentText().lower(),
            "amount": self.amount_input.value(),
            "price": self.price_input.value(),
            "date": self.date_input.text(),
        }

    def load_coins(self, coins):
        """Load coins into combo box"""
        for coin in coins:
            self.coin_combo.addItem(
                f"{coin['symbol'].upper()} - {coin['name']}", coin["id"]
            )


class EnhancedPredictionTab(QWidget):
    """Simple prediction tab to get started"""
    def __init__(self, api_handler, predictor):
        super().__init__()
        self.api = api_handler
        self.predictor = predictor
        layout = QVBoxLayout()
        layout.addWidget(QLabel("🤖 AI Predictions - Enhanced"))
        self.setLayout(layout)

    def __init__(self, api_handler, predictor):  
        super().__init__(api_handler, predictor)

    def init_ui(self):
        layout = QVBoxLayout()
        # Title
        title_label = QLabel("AI Price Predictions")
        title_label.setStyleSheet(
            "font-size: 20px; font-weight: bold; margin: 10px; color: #2c3e50;"
        )
        layout.addWidget(title_label)
        # Controls section
        control_panel = QGroupBox("Prediction Controls")
        control_layout = QGridLayout()
        # Coin selection with search
        control_layout.addWidget(QLabel("Select Coin:"), 0, 0)
        coin_search_layout = QHBoxLayout()
        self.coin_selector = QComboBox()
        self.coin_selector.setMinimumWidth(250)
        self.coin_selector.setEditable(True)
        self.coin_selector.setInsertPolicy(QComboBox.NoInsert)
        # Add search functionality
        coin_search_layout.addWidget(self.coin_selector)
        search_btn = QPushButton("🔍")
        search_btn.setToolTip("Search for any coin")
        search_btn.clicked.connect(self.search_coin)
        coin_search_layout.addWidget(search_btn)
        control_layout.addLayout(coin_search_layout, 0, 1, 1, 2)
        # Timeframe selection
        control_layout.addWidget(QLabel("Timeframe:"), 1, 0)
        self.timeframe_combo = QComboBox()
        self.timeframe_combo.addItems(["24 Hours", "7 Days", "Both"])
        control_layout.addWidget(self.timeframe_combo, 1, 1)
        # Current price display
        control_layout.addWidget(QLabel("Current Price:"), 0, 3)
        self.current_price_display = QLabel("N/A")
        self.current_price_display.setStyleSheet("font-weight: bold; color: #2c3e50;")
        control_layout.addWidget(self.current_price_display, 0, 4)
        # Buttons
        button_layout = QHBoxLayout()
        self.predict_button = QPushButton("🚀 Generate Prediction")
        self.predict_button.clicked.connect(self.run_prediction)
        self.predict_button.setStyleSheet(
            """
            QPushButton {
                padding: 10px 20px;
                background-color: #27ae60;
                color: white;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        """
        )
        button_layout.addWidget(self.predict_button)
        self.train_button = QPushButton("⚙️ Train Model")
        self.train_button.clicked.connect(self.train_model)
        self.train_button.setStyleSheet(
            """
            QPushButton {
                padding: 10px 20px;
                background-color: #3498db;
                color: white;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        """
        )
        button_layout.addWidget(self.train_button)
        control_layout.addLayout(button_layout, 2, 0, 1, 5)
        control_panel.setLayout(control_layout)
        layout.addWidget(control_panel)
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet(
            """
            QProgressBar {
                border: 1px solid #ddd;
                border-radius: 3px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #3498db;
                border-radius: 3px;
            }
        """
        )
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        # Results splitter
        splitter = QSplitter(Qt.Vertical)
        # Results section
        results_group = QGroupBox("Prediction Results")
        results_layout = QGridLayout()
        # Current price
        results_layout.addWidget(QLabel("Current Price:"), 0, 0)
        self.current_price_label = QLabel("N/A")
        self.current_price_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        results_layout.addWidget(self.current_price_label, 0, 1)
        # 24h prediction
        results_layout.addWidget(QLabel("24h Prediction:"), 1, 0)
        self.predicted_24h_label = QLabel("N/A")
        self.predicted_24h_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        results_layout.addWidget(self.predicted_24h_label, 1, 1)
        results_layout.addWidget(QLabel("24h Change:"), 2, 0)
        self.change_24h_label = QLabel("N/A")
        results_layout.addWidget(self.change_24h_label, 2, 1)
        # 7d prediction
        results_layout.addWidget(QLabel("7d Prediction:"), 0, 2)
        self.predicted_7d_label = QLabel("N/A")
        self.predicted_7d_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        results_layout.addWidget(self.predicted_7d_label, 0, 3)
        results_layout.addWidget(QLabel("7d Change:"), 1, 2)
        self.change_7d_label = QLabel("N/A")
        results_layout.addWidget(self.change_7d_label, 1, 3)
        # Confidence scores
        results_layout.addWidget(QLabel("24h Confidence:"), 2, 2)
        self.confidence_24h_label = QLabel("N/A")
        results_layout.addWidget(self.confidence_24h_label, 2, 3)
        results_layout.addWidget(QLabel("7d Confidence:"), 3, 2)
        self.confidence_7d_label = QLabel("N/A")
        results_layout.addWidget(self.confidence_7d_label, 3, 3)
        results_group.setLayout(results_layout)
        splitter.addWidget(results_group)
        # Insights section
        insights_group = QGroupBox("Trading Insights & Analysis")
        insights_layout = QVBoxLayout()
        self.insights_text = QTextEdit()
        self.insights_text.setReadOnly(True)
        self.insights_text.setMaximumHeight(150)
        self.insights_text.setStyleSheet(
            """
            QTextEdit {
                background-color: #f8f9fa;
                border: 1px solid #ddd;
                border-radius: 3px;
                padding: 5px;
                font-size: 12px;
            }
        """
        )
        insights_layout.addWidget(self.insights_text)
        insights_group.setLayout(insights_layout)
        splitter.addWidget(insights_group)
        # Charts section
        charts_group = QGroupBox("Prediction Charts")
        charts_layout = QHBoxLayout()
        # 24h chart
        self.chart_24h = self.create_chart_widget("24-Hour Prediction")
        charts_layout.addWidget(self.chart_24h)
        # 7d chart
        self.chart_7d = self.create_chart_widget("7-Day Prediction")
        charts_layout.addWidget(self.chart_7d)
        charts_group.setLayout(charts_layout)
        splitter.addWidget(charts_group)
        splitter.setSizes([150, 150, 400])
        layout.addWidget(splitter)
        self.setLayout(layout)
        # Load coins
        self.load_coins()
        # Connect signals
        self.coin_selector.currentIndexChanged.connect(self.on_coin_selected)
        # Initialize charts
        self.init_charts()

    def create_chart_widget(self, title):
        """Create a chart widget"""
        widget = QWidget()
        layout = QVBoxLayout()
        chart_label = QLabel(title)
        chart_label.setStyleSheet(
            "font-weight: bold; font-size: 14px; margin-bottom: 5px;"
        )
        layout.addWidget(chart_label)
        figure = Figure(figsize=(5, 3))
        canvas = FigureCanvas(figure)
        layout.addWidget(canvas)
        widget.setLayout(layout)
        return widget

    def init_charts(self):
        """Initialize matplotlib charts"""
        # 24h chart
        self.figure_24h = Figure(figsize=(5, 3))
        self.ax_24h = self.figure_24h.add_subplot(111)
        self.canvas_24h = FigureCanvas(self.figure_24h)
        self.chart_24h.layout().addWidget(self.canvas_24h)
        # 7d chart
        self.figure_7d = Figure(figsize=(5, 3))
        self.ax_7d = self.figure_7d.add_subplot(111)
        self.canvas_7d = FigureCanvas(self.figure_7d)
        self.chart_7d.layout().addWidget(self.canvas_7d)

    def set_current_coin(self, coin_id):
        """Set the current coin programmatically and trigger prediction"""
        index = self.coin_selector.findData(coin_id)
        if index >= 0:
            self.coin_selector.setCurrentIndex(index)
            self.run_prediction()

    def search_coin(self):
        """Search for any coin"""
        search_text = self.coin_selector.currentText().strip()
        if not search_text:
            return
        try:
            # Search for coin
            search_results = self.api.search_coins(search_text)
            if search_results:
                # Clear and add search results
                self.coin_selector.clear()
                for coin in search_results[:20]:  # Limit to 20 results
                    self.coin_selector.addItem(
                        f"{coin.get('symbol', '').upper()} - {coin.get('name', 'Unknown')}",
                        coin.get("id"),
                    )
                QMessageBox.information(
                    self,
                    "Search Complete",
                    f"Found {len(search_results)} coins matching '{search_text}'",
                )
            else:
                QMessageBox.warning(
                    self, "No Results", f"No coins found matching '{search_text}'"
                )
        except Exception as e:
            QMessageBox.critical(self, "Search Error", f"Search failed: {str(e)}")

    def run_prediction(self):
        """Run prediction for selected timeframe"""
        coin_id = self.coin_selector.currentData()
        if not coin_id:
            QMessageBox.warning(self, "Warning", "Please select a coin first")
            return
        timeframe = self.timeframe_combo.currentText()
        # Get current price
        try:
            price_data = self.api.get_coin_price([coin_id], "usd")
            current_price = price_data.get(coin_id, {}).get("usd", 0)
            if current_price == 0:
                QMessageBox.warning(self, "Warning", "Failed to get current price")
                return
            # Disable UI
            self.predict_button.setEnabled(False)
            self.train_button.setEnabled(False)
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            # Run predictions based on timeframe
            if timeframe == "24 Hours":
                self.predict_24h(coin_id, current_price)
            elif timeframe == "7 Days":
                self.predict_7d(coin_id, current_price)
            elif timeframe == "Both":
                self.predict_both(
                    coin_id
                )  # <-- Removed the trailing comma and closed it
        except Exception as e:
            print(f"Prediction error: {e}")
            self.predict_button.setEnabled(True)
            self.train_button.setEnabled(True)
            self.progress_bar.setVisible(False)

 
class EnhancedPredictionTab(QWidget):
    def __init__(self, api_handler, predictor):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("AI Predictions Tab"))
        self.setLayout(layout)

class EnhancedPortfolioTab(QWidget):
    def __init__(self, api_handler, portfolio):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Portfolio Tab"))
        self.setLayout(layout)

class EnhancedSentimentTab(QWidget):
    def __init__(self, api_handler):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Sentiment Tab"))
        self.setLayout(layout)
               
class CryptoTrackerApp(QMainWindow):
    """Main application window - Holds all 4 tabs"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("CoinSentinel AI - Enhanced Cryptocurrency Tracker")
        self.setGeometry(100, 100, 1600, 900)

        # Initialize components
        self.api = EnhancedCryptoAPIHandler()
        self.predictor = AdvancedPricePredictor(self.api)  # Your existing predictor
        self.portfolio = PortfolioTracker()
        self.sentiment = SentimentTracker(self.api)

        self.current_currency = "usd"
        self.top_coins = []

        self.init_ui()
        self.load_initial_data()

    def init_ui(self):
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Create tab widget
        self.tabs = QTabWidget()

        # Add enhanced tabs
        self.tabs.addTab(ImprovedMarketTab(self.api), "Market Overview")
        self.tabs.addTab(
            EnhancedPredictionTab(self.api, self.predictor), "AI Predictions"
        )
        self.tabs.addTab(EnhancedPortfolioTab(self.api, self.portfolio), "Portfolio")
        self.tabs.addTab(EnhancedSentimentTab(self.api), "Market Sentiment")

        main_layout.addWidget(self.tabs)

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Application ready")
        

    def load_initial_data(self):
        """Load initial data"""
        self.status_bar.showMessage("Loading initial data...")

        # Data loaded by individual tabs
        self.status_bar.showMessage("Ready")

    def create_simple_market_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.addWidget(QLabel("Market Tab"))
        return widget
    
class EnhancedPredictionTab(QWidget):
    """Enhanced predictions with multiple timeframes"""

    def __init__(self, api_handler, predictor):
        super().__init__()
        self.api = api_handler
        self.predictor = predictor

    def init_ui(self):
        layout = QVBoxLayout()
        # Title
        title_label = QLabel("AI Price Predictions")
        title_label.setStyleSheet(
            "font-size: 20px; font-weight: bold; margin: 10px; color: #2c3e50;"
        )
        layout.addWidget(title_label)
        # Controls section
        control_panel = QGroupBox("Prediction Controls")
        control_layout = QGridLayout()
        # Coin selection with search
        control_layout.addWidget(QLabel("Select Coin:"), 0, 0)
        coin_search_layout = QHBoxLayout()
        self.coin_selector = QComboBox()
        self.coin_selector.setMinimumWidth(250)
        self.coin_selector.setEditable(True)
        self.coin_selector.setInsertPolicy(QComboBox.NoInsert)
        # Add search functionality
        coin_search_layout.addWidget(self.coin_selector)
        search_btn = QPushButton("🔍")
        search_btn.setToolTip("Search for any coin")
        search_btn.clicked.connect(self.search_coin)
        coin_search_layout.addWidget(search_btn)
        control_layout.addLayout(coin_search_layout, 0, 1, 1, 2)
        # Timeframe selection
        control_layout.addWidget(QLabel("Timeframe:"), 1, 0)
        self.timeframe_combo = QComboBox()
        self.timeframe_combo.addItems(["24 Hours", "7 Days", "Both"])
        control_layout.addWidget(self.timeframe_combo, 1, 1)
        # Current price display
        control_layout.addWidget(QLabel("Current Price:"), 0, 3)
        self.current_price_display = QLabel("N/A")
        self.current_price_display.setStyleSheet("font-weight: bold; color: #2c3e50;")
        control_layout.addWidget(self.current_price_display, 0, 4)
        # Buttons
        button_layout = QHBoxLayout()
        self.predict_button = QPushButton("🚀 Generate Prediction")
        self.predict_button.clicked.connect(self.run_prediction)
        self.predict_button.setStyleSheet(
            """
            QPushButton {
                padding: 10px 20px;
                background-color: #27ae60;
                color: white;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        """
        )
        button_layout.addWidget(self.predict_button)
        self.train_button = QPushButton("⚙️ Train Model")
        self.train_button.clicked.connect(self.train_model)
        self.train_button.setStyleSheet(
            """
            QPushButton {
                padding: 10px 20px;
                background-color: #3498db;
                color: white;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        """
        )
        button_layout.addWidget(self.train_button)
        control_layout.addLayout(button_layout, 2, 0, 1, 5)
        control_panel.setLayout(control_layout)
        layout.addWidget(control_panel)
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet(
            """
            QProgressBar {
                border: 1px solid #ddd;
                border-radius: 3px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #3498db;
                border-radius: 3px;
            }
        """
        )
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        # Results splitter
        splitter = QSplitter(Qt.Vertical)
        # Results section
        results_group = QGroupBox("Prediction Results")
        results_layout = QGridLayout()
        # Current price
        results_layout.addWidget(QLabel("Current Price:"), 0, 0)
        self.current_price_label = QLabel("N/A")
        self.current_price_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        results_layout.addWidget(self.current_price_label, 0, 1)
        # 24h prediction
        results_layout.addWidget(QLabel("24h Prediction:"), 1, 0)
        self.predicted_24h_label = QLabel("N/A")
        self.predicted_24h_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        results_layout.addWidget(self.predicted_24h_label, 1, 1)
        results_layout.addWidget(QLabel("24h Change:"), 2, 0)
        self.change_24h_label = QLabel("N/A")
        results_layout.addWidget(self.change_24h_label, 2, 1)
        # 7d prediction
        results_layout.addWidget(QLabel("7d Prediction:"), 0, 2)
        self.predicted_7d_label = QLabel("N/A")
        self.predicted_7d_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        results_layout.addWidget(self.predicted_7d_label, 0, 3)
        results_layout.addWidget(QLabel("7d Change:"), 1, 2)
        self.change_7d_label = QLabel("N/A")
        results_layout.addWidget(self.change_7d_label, 1, 3)
        # Confidence scores
        results_layout.addWidget(QLabel("24h Confidence:"), 2, 2)
        self.confidence_24h_label = QLabel("N/A")
        results_layout.addWidget(self.confidence_24h_label, 2, 3)
        results_layout.addWidget(QLabel("7d Confidence:"), 3, 2)
        self.confidence_7d_label = QLabel("N/A")
        results_layout.addWidget(self.confidence_7d_label, 3, 3)
        results_group.setLayout(results_layout)
        splitter.addWidget(results_group)
        # Insights section
        insights_group = QGroupBox("Trading Insights & Analysis")
        insights_layout = QVBoxLayout()
        self.insights_text = QTextEdit()
        self.insights_text.setReadOnly(True)
        self.insights_text.setMaximumHeight(150)
        self.insights_text.setStyleSheet(
            """
            QTextEdit {
                background-color: #f8f9fa;
                border: 1px solid #ddd;
                border-radius: 3px;
                padding: 5px;
                font-size: 12px;
            }
        """
        )
        insights_layout.addWidget(self.insights_text)
        insights_group.setLayout(insights_layout)
        splitter.addWidget(insights_group)
        # Charts section
        charts_group = QGroupBox("Prediction Charts")
        charts_layout = QHBoxLayout()
        # 24h chart
        self.chart_24h = self.create_chart_widget("24-Hour Prediction")
        charts_layout.addWidget(self.chart_24h)
        # 7d chart
        self.chart_7d = self.create_chart_widget("7-Day Prediction")
        charts_layout.addWidget(self.chart_7d)
        charts_group.setLayout(charts_layout)
        splitter.addWidget(charts_group)
        splitter.setSizes([150, 150, 400])
        layout.addWidget(splitter)
        self.setLayout(layout)
        # Load coins
        self.load_coins()
        # Connect signals
        self.coin_selector.currentIndexChanged.connect(self.on_coin_selected)
        # Initialize charts
        self.init_charts()

    def create_chart_widget(self, title):
        """Create a chart widget"""
        widget = QWidget()
        layout = QVBoxLayout()
        chart_label = QLabel(title)
        chart_label.setStyleSheet(
            "font-weight: bold; font-size: 14px; margin-bottom: 5px;"
        )
        layout.addWidget(chart_label)
        figure = Figure(figsize=(5, 3))
        canvas = FigureCanvas(figure)
        layout.addWidget(canvas)
        widget.setLayout(layout)
        return widget

    def init_charts(self):
        """Initialize matplotlib charts"""
        # 24h chart
        self.figure_24h = Figure(figsize=(5, 3))
        self.ax_24h = self.figure_24h.add_subplot(111)
        self.canvas_24h = FigureCanvas(self.figure_24h)
        self.chart_24h.layout().addWidget(self.canvas_24h)
        # 7d chart
        self.figure_7d = Figure(figsize=(5, 3))
        self.ax_7d = self.figure_7d.add_subplot(111)
        self.canvas_7d = FigureCanvas(self.figure_7d)
        self.chart_7d.layout().addWidget(self.canvas_7d)

    def search_coin(self):
        """Search for any coin"""
        search_text = self.coin_selector.currentText().strip()
        if not search_text:
            return
        try:
            # Search for coin
            search_results = self.api.search_coins(search_text)
            if search_results:
                # Clear and add search results
                self.coin_selector.clear()
                for coin in search_results[:20]:  # Limit to 20 results
                    self.coin_selector.addItem(
                        f"{coin.get('symbol', '').upper()} - {coin.get('name', 'Unknown')}",
                        coin.get("id"),
                    )
                QMessageBox.information(
                    self,
                    "Search Complete",
                    f"Found {len(search_results)} coins matching '{search_text}'",
                )
            else:
                QMessageBox.warning(
                    self, "No Results", f"No coins found matching '{search_text}'"
                )
        except Exception as e:
            QMessageBox.critical(self, "Search Error", f"Search failed: {str(e)}")

    def run_prediction(self):
        """Run prediction for selected timeframe"""
        coin_id = self.coin_selector.currentData()
        if not coin_id:
            QMessageBox.warning(self, "Warning", "Please select a coin first")
            return
        timeframe = self.timeframe_combo.currentText()
        # Get current price
        try:
            price_data = self.api.get_coin_price([coin_id], "usd")
            current_price = price_data.get(coin_id, {}).get("usd", 0)
            if current_price == 0:
                QMessageBox.warning(self, "Warning", "Failed to get current price")
                return
            # Disable UI
            self.predict_button.setEnabled(False)
            self.train_button.setEnabled(False)
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            # Run predictions based on timeframe
            # Run predictions based on timeframe
            if timeframe == "24 Hours":
                self.predict_24h(coin_id, current_price)
            elif timeframe == "7 Days":
                self.predict_7d(coin_id, current_price)
            elif timeframe == "Both":
                self.predict_both(coin_id)
        except Exception as e:
            print(f"Prediction error: {e}")
            self.predict_button.setEnabled(True)
            self.train_button.setEnabled(True)
            self.progress_bar.setVisible(False)
            self.predict_both(coin_id, current_price)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Prediction failed: {str(e)}")
            self.reset_ui()

    def predict_24h(self, coin_id, current_price):
        """Predict 24-hour price"""
        try:
            self.progress_bar.setValue(25)
            # Get 24-hour prediction
            result_24h = self.predictor.predict_price(coin_id, current_price)
            self.progress_bar.setValue(100)
            self.display_24h_prediction(result_24h, current_price)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"24h prediction failed: {str(e)}")
        finally:
            self.reset_ui()

    def predict_7d(self, coin_id, current_price):
        """Predict 7-day price"""
        try:
            self.progress_bar.setValue(25)
            # For 7-day prediction, we need to extend the predictor
            # This would require modifying the price_predictor.py to support multiple timeframes
            # For now, we'll use a simplified version
            # Get historical data for training
            historical_data = self.predictor.get_historical_data(coin_id, days=30)
            if historical_data is None or len(historical_data) < 20:
                QMessageBox.warning(
                    self,
                    "Insufficient Data",
                    "Not enough historical data for 7-day prediction",
                )
                self.reset_ui()
                return
            # Calculate 7-day moving average trend
            prices = historical_data["close"].values
            if len(prices) >= 7:
                # Simple trend analysis for 7-day prediction
                recent_avg = np.mean(prices[-7:])
                previous_avg = np.mean(prices[-14:-7])
                trend = (recent_avg - previous_avg) / previous_avg

                # Apply trend to current price for 7-day prediction
                predicted_7d_price = current_price * (1 + trend * 2)  # Amplify trend
                predicted_change = (
                    (predicted_7d_price - current_price) / current_price
                ) * 100
                result_7d = {
                    "current_price": current_price,
                    "predicted_price": predicted_7d_price,
                    "predicted_change_percent": predicted_change,
                    "confidence_score": 65.0,  # Lower confidence for 7-day
                    "direction": "bullish" if predicted_change > 0 else "bearish",
                    "timeframe": "7d",
                }
                self.progress_bar.setValue(100)
                self.display_7d_prediction(result_7d, current_price)
            else:
                QMessageBox.warning(
                    self, "Error", "Insufficient data for 7-day prediction"
                )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"7-day prediction failed: {str(e)}")
        finally:
            self.reset_ui()

    def predict_both(self, coin_id, current_price):
        """Predict both 24h and 7d prices"""
        try:
            self.progress_bar.setValue(25)
            # Get 24h prediction
            result_24h = self.predictor.predict_price(coin_id, current_price)
            self.progress_bar.setValue(50)
            # Get historical data for 7d prediction
            historical_data = self.predictor.get_historical_data(coin_id, days=30)
            result_7d = None
            if historical_data is not None and len(historical_data) >= 20:
                prices = historical_data["close"].values
                if len(prices) >= 7:
                    recent_avg = np.mean(prices[-7:])
                    previous_avg = np.mean(prices[-14:-7])
                    trend = (recent_avg - previous_avg) / previous_avg
                    predicted_7d_price = current_price * (1 + trend * 2)
                    predicted_change = (
                        (predicted_7d_price - current_price) / current_price
                    ) * 100

                    result_7d = {
                        "current_price": current_price,
                        "predicted_price": predicted_7d_price,
                        "predicted_change_percent": predicted_change,
                        "confidence_score": 65.0,
                        "direction": "bullish" if predicted_change > 0 else "bearish",
                        "timeframe": "7d",
                    }
            self.progress_bar.setValue(100)
            self.display_both_predictions(result_24h, result_7d, current_price)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Prediction failed: {str(e)}")
        finally:
            self.reset_ui()

    def display_24h_prediction(self, result, current_price):
        """Display 24-hour prediction results"""
        self.current_price_label.setText(f"${current_price:,.4f}")
        # 24h prediction
        pred_price = result["predicted_price"]
        pred_change = result["predicted_change_percent"]
        confidence = result["confidence_score"]
        color = "#27ae60" if pred_change > 0 else "#e74c3c"
        self.predicted_24h_label.setText(
            f"<span style='color: {color};'>${pred_price:,.4f}</span>"
        )
        self.change_24h_label.setText(
            f"<span style='color: {color};'>{pred_change:+.2f}%</span>"
        )
        self.confidence_24h_label.setText(
            f"<span style='color: {'#27ae60' if confidence >= 70 else '#f39c12'};'>{confidence:.1f}%</span>"
        )
        # Clear 7d fields
        self.predicted_7d_label.setText("N/A")
        self.change_7d_label.setText("N/A")
        self.confidence_7d_label.setText("N/A")
        # Update insights
        insights = [
            f"24-hour trend: {'Bullish' if pred_change > 0 else 'Bearish'}",
            f"Confidence level: {'High' if confidence >= 70 else 'Moderate' if confidence >= 50 else 'Low'}",
            f"Expected movement: {abs(pred_change):.2f}%",
            "Trading suggestion: Consider "
            + (
                "buying opportunities"
                if pred_change > 2
                else (
                    "holding position"
                    if abs(pred_change) <= 2
                    else "taking profits or setting stop losses"
                )
            ),
        ]
        if result.get("is_fallback", False):
            insights.append("⚠️ Using statistical fallback model")
        self.insights_text.setPlainText(
            "\n".join([f"• {insight}" for insight in insights])
        )
        # Update chart
        self.update_24h_chart(result)

    def display_7d_prediction(self, result, current_price):
        """Display 7-day prediction results"""
        self.current_price_label.setText(f"${current_price:,.4f}")
        # 7d prediction
        pred_price = result["predicted_price"]
        pred_change = result["predicted_change_percent"]
        confidence = result["confidence_score"]
        color = "#27ae60" if pred_change > 0 else "#e74c3c"
        self.predicted_7d_label.setText(
            f"<span style='color: {color};'>${pred_price:,.4f}</span>"
        )
        self.change_7d_label.setText(
            f"<span style='color: {color};'>{pred_change:+.2f}%</span>"
        )
        self.confidence_7d_label.setText(
            f"<span style='color: {'#27ae60' if confidence >= 70 else '#f39c12'};'>{confidence:.1f}%</span>"
        )
        # Clear 24h fields
        self.predicted_24h_label.setText("N/A")
        self.change_24h_label.setText("N/A")
        self.confidence_24h_label.setText("N/A")
        # Update insights
        insights = [
            f"7-day trend: {'Bullish' if pred_change > 0 else 'Bearish'}",
            f"Confidence level: {'High' if confidence >= 70 else 'Moderate' if confidence >= 50 else 'Low'}",
            f"Expected movement: {abs(pred_change):.2f}%",
            "Weekly outlook: "
            + (
                "Strong upward momentum"
                if pred_change > 5
                else (
                    "Moderate growth expected"
                    if pred_change > 0
                    else (
                        "Correction phase"
                        if pred_change < -5
                        else "Sideways movement likely"
                    )
                )
            ),
            "Investment advice: "
            + (
                "Consider accumulating on dips"
                if pred_change > 0
                else (
                    "Wait for better entry points"
                    if pred_change < -10
                    else "Dollar-cost average if long-term bullish"
                )
            ),
        ]
        self.insights_text.setPlainText(
            "\n".join([f"• {insight}" for insight in insights])
        )
        # Update chart
        self.update_7d_chart(result)

    def display_both_predictions(self, result_24h, result_7d, current_price):
        """Display both 24h and 7d predictions"""
        self.current_price_label.setText(f"${current_price:,.4f}")
        # Display 24h prediction
        if result_24h:
            pred_24h_price = result_24h["predicted_price"]
            pred_24h_change = result_24h["predicted_change_percent"]
            confidence_24h = result_24h["confidence_score"]
            color_24h = "#27ae60" if pred_24h_change > 0 else "#e74c3c"
            self.predicted_24h_label.setText(
                f"<span style='color: {color_24h};'>${pred_24h_price:,.4f}</span>"
            )
            self.change_24h_label.setText(
                f"<span style='color: {color_24h};'>{pred_24h_change:+.2f}%</span>"
            )
            self.confidence_24h_label.setText(
                f"<span style='color: {'#27ae60' if confidence_24h >= 70 else '#f39c12'};'>{confidence_24h:.1f}%</span>"
            )
        # Display 7d prediction
        if result_7d:
            pred_7d_price = result_7d["predicted_price"]
            pred_7d_change = result_7d["predicted_change_percent"]
            confidence_7d = result_7d["confidence_score"]
            color_7d = "#27ae60" if pred_7d_change > 0 else "#e74c3c"
            self.predicted_7d_label.setText(
                f"<span style='color: {color_7d};'>${pred_7d_price:,.4f}</span>"
            )
            self.change_7d_label.setText(
                f"<span style='color: {color_7d};'>{pred_7d_change:+.2f}%</span>"
            )
            self.confidence_7d_label.setText(
                f"<span style='color: {'#27ae60' if confidence_7d >= 70 else '#f39c12'};'>{confidence_7d:.1f}%</span>"
            )
        # Update insights
        insights = []
        if result_24h and result_7d:
            # Compare trends
            same_trend = result_24h["direction"] == result_7d["direction"]
            insights.append(
                f"24h outlook: {result_24h['direction'].upper()} ({result_24h['predicted_change_percent']:+.2f}%)"
            )
            insights.append(
                f"7d outlook: {result_7d['direction'].upper()} ({result_7d['predicted_change_percent']:+.2f}%)"
            )
            if same_trend:
                insights.append(
                    f"📈 Trend consistency: {'BULLISH' if result_24h['direction'] == 'bullish' else 'BEARISH'} momentum across timeframes"
                )
                if result_24h["direction"] == "bullish":
                    insights.append(
                        "🎯 Trading strategy: Consider scaling into position"
                    )
                else:
                    insights.append("🎯 Trading strategy: Consider reducing exposure")
            else:
                insights.append(
                    "⚠️ Trend divergence: Short-term and long-term views differ"
                )
                insights.append(
                    "🎯 Trading strategy: Wait for clearer trend confirmation"
                )
            # Add confidence comparison
            insights.append(
                f"Confidence: 24h={result_24h['confidence_score']:.1f}%, 7d={result_7d['confidence_score']:.1f}%"
            )
        elif result_24h:
            insights.append(
                f"24h prediction: {result_24h['direction'].upper()} ({result_24h['predicted_change_percent']:+.2f}%)"
            )
            insights.append(f"Confidence: {result_24h['confidence_score']:.1f}%")
            insights.append("7-day data unavailable")
        elif result_7d:
            insights.append(
                f"7d prediction: {result_7d['direction'].upper()} ({result_7d['predicted_change_percent']:+.2f}%)"
            )
            insights.append(f"Confidence: {result_7d['confidence_score']:.1f}%")
            insights.append("24-hour data unavailable")
        self.insights_text.setPlainText(
            "\n".join([f"• {insight}" for insight in insights])
        )
        # Update charts
        if result_24h:
            self.update_24h_chart(result_24h)
        if result_7d:
            self.update_7d_chart(result_7d)

    def update_24h_chart(self, result):
        """Update 24-hour prediction chart"""
        self.ax_24h.clear()
        labels = ["Current", "Predicted"]
        prices = [result["current_price"], result["predicted_price"]]
        colors = [
            "#3498db",
            "#27ae60" if result["predicted_change_percent"] > 0 else "#e74c3c",
        ]
        bars = self.ax_24h.bar(labels, prices, color=colors, alpha=0.8, width=0.6)
        # Add value labels
        for bar, price in zip(bars, prices):
            height = bar.get_height()
            self.ax_24h.text(
                bar.get_x() + bar.get_width() / 2.0,
                height,
                f"${price:,.4f}",
                ha="center",
                va="bottom",
                fontsize=10,
                fontweight="bold",
            )
        # Add change percentage
        change_text = f"{result['predicted_change_percent']:+.2f}%"
        self.ax_24h.text(
            1,
            result["predicted_price"] * 0.9,
            f"Δ: {change_text}",
            ha="center",
            fontsize=9,
            fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="#f0f0f0", alpha=0.8),
        )
        # Format chart
        self.ax_24h.set_ylabel("Price (USD)", fontsize=10)
        self.ax_24h.set_title(
            "24-Hour Price Prediction", fontsize=12, fontweight="bold"
        )
        self.ax_24h.grid(True, alpha=0.3, linestyle="--")
        self.figure_24h.tight_layout()
        self.canvas_24h.draw()

    def update_7d_chart(self, result):
        """Update 7-day prediction chart"""
        self.ax_7d.clear()
        # Create timeline for 7 days
        days = ["Today", "+1d", "+2d", "+3d", "+4d", "+5d", "+6d", "+7d"]
        # Create a simple projection curve
        current_price = result["current_price"]
        target_price = result["predicted_price"]
        # Create exponential curve for projection
        x = np.arange(len(days))
        base_change = (target_price / current_price) ** (1 / 7)
        projected_prices = [current_price * (base_change**i) for i in range(len(days))]
        # Plot
        line = self.ax_7d.plot(
            days,
            projected_prices,
            marker="o",
            color="#9b59b6",
            linewidth=2,
            markersize=5,
        )[0]
        # Fill area under curve
        self.ax_7d.fill_between(days, projected_prices, alpha=0.2, color="#9b59b6")
        # Add labels for start and end
        self.ax_7d.annotate(
            f"${current_price:,.2f}",
            xy=(0, projected_prices[0]),
            xytext=(-10, 10),
            textcoords="offset points",
            fontsize=9,
            fontweight="bold",
        )
        self.ax_7d.annotate(
            f'${target_price:,.2f}\n({result["predicted_change_percent"]:+.1f}%)',
            xy=(7, projected_prices[-1]),
            xytext=(10, -20),
            textcoords="offset points",
            fontsize=9,
            fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="#f0f0f0", alpha=0.8),
        )
        # Format chart
        self.ax_7d.set_ylabel("Price (USD)", fontsize=10)
        self.ax_7d.set_title("7-Day Price Projection", fontsize=12, fontweight="bold")
        self.ax_7d.grid(True, alpha=0.3, linestyle="--")
        # Rotate x-axis labels
        plt.setp(self.ax_7d.get_xticklabels(), rotation=45, ha="right")
        self.figure_7d.tight_layout()
        self.canvas_7d.draw()


class EnhancedSentimentTab(QWidget):
    """Enhanced market sentiment tab"""

    def __init__(self, api_handler):
        super().__init__()
        self.api = api_handler
        self.sentiment = SentimentTracker(api_handler)
        self.init_ui()
        self.load_sentiment_data()
        # Auto-refresh every 5 minutes
        self.timer = QTimer()
        self.timer.timeout.connect(self.load_sentiment_data)
        self.timer.start(300000)  # 5 minutes

    def init_ui(self):
        layout = QVBoxLayout()
        # Title
        title_label = QLabel("Market Sentiment Dashboard")
        title_label.setStyleSheet(
            "font-size: 20px; font-weight: bold; margin: 10px; color: #2c3e50;"
        )
        layout.addWidget(title_label)
        # Fear & Greed Index with gauge visualization
        fgi_panel = self.create_fgi_panel()
        layout.addWidget(fgi_panel)
        # Sentiment indicators
        indicators_panel = self.create_indicators_panel()
        layout.addWidget(indicators_panel)
        # Market overview
        market_panel = self.create_market_overview_panel()
        layout.addWidget(market_panel)
        # Analysis and recommendations
        analysis_panel = self.create_analysis_panel()
        layout.addWidget(analysis_panel)
        self.setLayout(layout)

    def create_fgi_panel(self):
        """Create Fear & Greed Index panel with visual gauge"""
        panel = QGroupBox("Crypto Fear & Greed Index")
        layout = QVBoxLayout()
        # Value and classification
        top_layout = QHBoxLayout()
        self.fgi_value_label = QLabel("Loading...")
        self.fgi_value_label.setStyleSheet(
            "font-size: 48px; font-weight: bold; margin: 10px;"
        )
        self.fgi_class_label = QLabel("")
        self.fgi_class_label.setStyleSheet(
            "font-size: 24px; font-weight: bold; margin: 10px;"
        )
        top_layout.addWidget(self.fgi_value_label)
        top_layout.addWidget(self.fgi_class_label)
        top_layout.addStretch()
        layout.addLayout(top_layout)
        # Visual gauge
        gauge_widget = QWidget()
        gauge_layout = QHBoxLayout()
        # Create gauge segments
        segments = [
            (0, 25, "Extreme Fear", "#e74c3c"),
            (25, 45, "Fear", "#e67e22"),
            (45, 55, "Neutral", "#f1c40f"),
            (55, 75, "Greed", "#27ae60"),
            (75, 100, "Extreme Greed", "#2ecc71"),
        ]
        for i, (start, end, label, color) in enumerate(segments):
            segment = QLabel()
            segment.setMinimumHeight(20)
            segment.setStyleSheet(f"background-color: {color}; border: 1px solid #ddd;")
            segment.setToolTip(f"{label}: {start}-{end}")
            gauge_layout.addWidget(segment)
        gauge_widget.setLayout(gauge_layout)
        layout.addWidget(gauge_widget)
        # Description and timestamp
        self.fgi_description = QLabel("")
        self.fgi_description.setWordWrap(True)
        self.fgi_description.setStyleSheet("margin: 5px; font-size: 13px;")
        self.fgi_timestamp = QLabel("")
        self.fgi_timestamp.setStyleSheet(
            "color: #7f8c8d; font-size: 11px; margin: 5px;"
        )
        layout.addWidget(self.fgi_description)
        layout.addWidget(self.fgi_timestamp)
        panel.setLayout(layout)
        return panel

    def create_indicators_panel(self):
        """Create sentiment indicators panel"""
        panel = QGroupBox("Market Sentiment Indicators")
        layout = QGridLayout()
        # Social sentiment
        layout.addWidget(QLabel("Social Sentiment:"), 0, 0)
        self.social_sentiment_label = QLabel("Loading...")
        self.social_sentiment_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(self.social_sentiment_label, 0, 1)
        # Market momentum
        layout.addWidget(QLabel("Market Momentum:"), 0, 2)
        self.momentum_label = QLabel("Loading...")
        self.momentum_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(self.momentum_label, 0, 3)
        # Volume trend
        layout.addWidget(QLabel("Volume Trend:"), 1, 0)
        self.volume_trend_label = QLabel("Loading...")
        self.volume_trend_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(self.volume_trend_label, 1, 1)
        # Volatility
        layout.addWidget(QLabel("Market Volatility:"), 1, 2)
        self.volatility_label = QLabel("Loading...")
        self.volatility_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(self.volatility_label, 1, 3)
        # BTC dominance trend
        layout.addWidget(QLabel("BTC Dominance:"), 2, 0)
        self.btc_dom_label = QLabel("Loading...")
        self.btc_dom_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(self.btc_dom_label, 2, 1)
        # Altcoin season index
        layout.addWidget(QLabel("Altcoin Season:"), 2, 2)
        self.altcoin_season_label = QLabel("Loading...")
        self.altcoin_season_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(self.altcoin_season_label, 2, 3)
        panel.setLayout(layout)
        return panel

    def create_market_overview_panel(self):
        """Create market overview panel"""
        panel = QGroupBox("Market Overview")
        layout = QGridLayout()
        # Gainers vs Losers
        self.gainers_losers_chart = QLabel()
        self.gainers_losers_chart.setMinimumHeight(150)
        self.gainers_losers_chart.setStyleSheet(
            "border: 1px solid #ddd; background-color: white;"
        )
        layout.addWidget(self.gainers_losers_chart, 0, 0, 2, 1)
        # Market statistics
        stats_widget = QWidget()
        stats_layout = QVBoxLayout()
        self.gainers_count = QLabel("Gainers (24h): 0")
        self.gainers_count.setStyleSheet(
            "font-size: 14px; font-weight: bold; color: #27ae60;"
        )
        self.losers_count = QLabel("Losers (24h): 0")
        self.losers_count.setStyleSheet(
            "font-size: 14px; font-weight: bold; color: #e74c3c;"
        )
        self.neutral_count = QLabel("Neutral (24h): 0")
        self.neutral_count.setStyleSheet(
            "font-size: 14px; font-weight: bold; color: #7f8c8d;"
        )
        self.extreme_moves = QLabel("Extreme Moves (>10%): 0")
        self.extreme_moves.setStyleSheet("font-size: 14px; font-weight: bold;")
        stats_layout.addWidget(self.gainers_count)
        stats_layout.addWidget(self.losers_count)
        stats_layout.addWidget(self.neutral_count)
        stats_layout.addWidget(self.extreme_moves)
        stats_layout.addStretch()
        stats_widget.setLayout(stats_layout)
        layout.addWidget(stats_widget, 0, 1)
        # Top gainers and losers
        top_coins_widget = QWidget()
        top_coins_layout = QVBoxLayout()
        self.top_gainers = QLabel("Top Gainers:\nLoading...")
        self.top_gainers.setStyleSheet("font-size: 12px;")
        self.top_losers = QLabel("Top Losers:\nLoading...")
        self.top_losers.setStyleSheet("font-size: 12px;")
        top_coins_layout.addWidget(self.top_gainers)
        top_coins_layout.addWidget(self.top_losers)
        top_coins_widget.setLayout(top_coins_layout)
        layout.addWidget(top_coins_widget, 1, 1)
        panel.setLayout(layout)
        return panel

        def create_analysis_panel(self):
            panel = QGroupBox("Market Analysis & Trading Recommendations")
            layout = QVBoxLayout()
            self.analysis_text = QTextEdit()
            self.analysis_text.setReadOnly(True) # This is 1246
            self.analysis_text.setMinimumHeight(200)
            self.analysis_text.setStyleSheet(
            """
            QTextEdit {
                background-color: #f8f9fa;
                border: 1px solid #ddd;
                border-radius: 3px;
                padding: 10px;
                font-size: 13px;
                line-height: 1.4;
            }
        """
        )
        layout.addWidget(self.analysis_text)
        panel.setLayout(layout)
        return panel

    def load_sentiment_data(self):
        """Load and display sentiment data"""
        try:
            sentiment_data = self.sentiment.get_market_sentiment()
            if not sentiment_data:
                QMessageBox.warning(self, "Warning", "No sentiment data available")
                return
            # Update Fear & Greed Index
            fgi = sentiment_data.get("fear_greed", {})
            fgi_value = fgi.get("value", 50)
            fgi_class = fgi.get("classification", "Neutral")
            # Set FGI color
            if fgi_value >= 75:
                color = "#2ecc71"  # Green
                bg_color = "#d5f4e6"
            elif fgi_value >= 60:
                color = "#27ae60"  # Light green
                bg_color = "#d5f4e6"
            elif fgi_value >= 45:
                color = "#f1c40f"  # Yellow
                bg_color = "#fef9e7"
            elif fgi_value >= 30:
                color = "#e67e22"  # Orange
                bg_color = "#fbeee6"
            else:
                color = "#e74c3c"  # Red
                bg_color = "#fdedec"
            self.fgi_value_label.setText(str(fgi_value))
            self.fgi_value_label.setStyleSheet(
                f"""
                font-size: 48px; 
                font-weight: bold; 
                margin: 10px; 
                color: {color};
                background-color: {bg_color};
                padding: 10px;
                border-radius: 5px;
            """
            )
            self.fgi_class_label.setText(fgi_class.upper())
            self.fgi_class_label.setStyleSheet(
                f"font-size: 24px; font-weight: bold; margin: 10px; color: {color};"
            )
            # Update description
            descriptions = {
                "extreme fear": "Investors are extremely fearful. This could indicate a buying opportunity for long-term investors.",
                "fear": "Market sentiment is fearful. Consider cautious accumulation.",
                "neutral": "Market sentiment is balanced. Good time for strategic entries.",
                "greed": "Investors are becoming greedy. Consider taking some profits.",
                "extreme greed": "Market is extremely greedy. High risk of correction. Consider reducing exposure.",
            }
            self.fgi_description.setText(
                descriptions.get(
                    fgi_class.lower(),
                    f"Fear & Greed Index at {fgi_value}/100 indicating {fgi_class} sentiment.",
                )
            )
            timestamp = fgi.get("timestamp", "")
            if timestamp:
                self.fgi_timestamp.setText(f"Last updated: {timestamp}")
            # Update market indicators
            market_analysis = sentiment_data.get("market_analysis", {})
            # Social sentiment (simulated)
            social_score = market_analysis.get("social_sentiment", 50)
            social_text = self.get_sentiment_text(social_score)
            self.social_sentiment_label.setText(social_text)
            self.set_sentiment_color(self.social_sentiment_label, social_score)
            # Market momentum
            momentum = market_analysis.get("momentum", 50)
            momentum_text = self.get_momentum_text(momentum)
            self.momentum_label.setText(momentum_text)
            self.set_sentiment_color(self.momentum_label, momentum)
            # Volume trend
            volume_trend = market_analysis.get("volume_trend", 50)
            volume_text = self.get_trend_text(volume_trend)
            self.volume_trend_label.setText(volume_text)
            self.set_sentiment_color(self.volume_trend_label, volume_trend)
            # Volatility
            volatility = market_analysis.get("volatility", 50)
            volatility_text = self.get_volatility_text(volatility)
            self.volatility_label.setText(volatility_text)
            self.set_sentiment_color(self.volatility_label, volatility, inverse=True)
            # Update market statistics
            gainers = market_analysis.get("gainers", 0)
            losers = market_analysis.get("losers", 0)
            neutral = market_analysis.get("neutral", 0)
            extreme = market_analysis.get("extreme_moves", 0)
            self.gainers_count.setText(f"Gainers (24h): {gainers}")
            self.losers_count.setText(f"Losers (24h): {losers}")
            self.neutral_count.setText(f"Neutral (24h): {neutral}")
            self.extreme_moves.setText(f"Extreme Moves (>10%): {extreme}")
            # Update top coins
            top_gainers = market_analysis.get("top_gainers", [])
            top_losers = market_analysis.get("top_losers", [])
            gainers_text = "Top Gainers:\n"
            for i, coin in enumerate(top_gainers[:5], 1):
                gainers_text += f"{i}. {coin.get('symbol', '').upper()}: +{coin.get('change_24h', 0):.1f}%\n"
            losers_text = "Top Losers:\n"
            for i, coin in enumerate(top_losers[:5], 1):
                losers_text += f"{i}. {coin.get('symbol', '').upper()}: {coin.get('change_24h', 0):.1f}%\n"
            self.top_gainers.setText(gainers_text)
            self.top_losers.setText(losers_text)
            # Update analysis
            analysis = self.generate_market_analysis(sentiment_data)
            self.analysis_text.setPlainText(analysis)
            # Draw simple chart for gainers vs losers
            self.draw_gainers_losers_chart(gainers, losers, neutral)
        except Exception as e:
            print(f"Error loading sentiment data: {e}")

    def get_sentiment_text(self, score):
        """Convert score to sentiment text"""
        if score >= 75:
            return "Very Bullish 🚀"
        elif score >= 60:
            return "Bullish 📈"
        elif score >= 40:
            return "Neutral ↔️"
        elif score >= 25:
            return "Bearish 📉"
        else:
            return "Very Bearish 🐻"

    def get_momentum_text(self, score):
        """Convert score to momentum text"""
        if score >= 75:
            return "Very Strong 💪"
        elif score >= 60:
            return "Strong ↗️"
        elif score >= 40:
            return "Moderate ➡️"
        elif score >= 25:
            return "Weak ↘️"
        else:
            return "Very Weak 👎"

    def get_trend_text(self, score):
        """Convert score to trend text"""
        if score >= 60:
            return "Increasing 📊"
        elif score >= 40:
            return "Stable ↔️"
        else:
            return "Decreasing 📉"

    def get_volatility_text(self, score):
        """Convert score to volatility text"""
        if score >= 75:
            return "Very High ⚡"
        elif score >= 60:
            return "High 🌊"
        elif score >= 40:
            return "Moderate 🌊"
        elif score >= 25:
            return "Low 🌊"
        else:return "Very Low ⚪"

    def set_sentiment_color(self, label, score, inverse=False):
        """Set color based on sentiment score"""
        if inverse:
            score = 100 - score  # Invert for volatility (lower is better)
        if score >= 70:
            color = "#27ae60"  # Green
        elif score >= 50:
            color = "#f39c12"  # Yellow/Orange
        else:
            color = "#e74c3c"  # Red
        label.setStyleSheet(f"font-weight: bold; color: {color};")

    def draw_gainers_losers_chart(self, gainers, losers, neutral):
        """Draw simple gainers vs losers chart"""
        try:
            # Create matplotlib figure
            fig, ax = plt.subplots(figsize=(4, 2))
            # Data
            categories = ["Gainers", "Losers", "Neutral"]
            values = [gainers, losers, neutral]
            colors = ["#27ae60", "#e74c3c", "#95a5a6"]
            # Create bar chart
            bars = ax.bar(categories, values, color=colors, alpha=0.8)
            # Add value labels
            bars = ax.bar(categories, values, color=colors, alpha=0.8)

            # Add value labels
            for bar, value in zip(bars, values):
                height = bar.get_height()
                ax.text(
                    bar.get_x() + bar.get_width() / 2.0,
                    height,
                    f"{value}",
                    ha="center",
                    va="bottom",
                    fontsize=10,
                    fontweight="bold",
                )

            # All these MUST line up with the 'for' and 'bars' above
            ax.grid(True, alpha=0.3, linestyle="--", axis="y")
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)
            fig.tight_layout()

            from io import BytesIO

            buf = BytesIO()
            fig.savefig(buf, format="png", dpi=100, bbox_inches="tight")
            buf.seek(0)

            pixmap = QPixmap()
            pixmap.loadFromData(buf.getvalue())
            # Set pixmap to label
            self.gainers_losers_chart.setPixmap(pixmap)
            self.gainers_losers_chart.setScaledContents(True)
            # Clean up
            plt.close(fig)
        except Exception as e:
            print(f"Error drawing chart: {e}")

    def generate_market_analysis(self, sentiment_data):
        """Generate comprehensive market analysis"""
        fgi = sentiment_data.get("fear_greed", {})
        market_analysis = sentiment_data.get("market_analysis", {})
        fgi_value = fgi.get("value", 50)
        fgi_class = fgi.get("classification", "neutral")
        gainers = market_analysis.get("gainers", 0)
        losers = market_analysis.get("losers", 0)
        neutral = market_analysis.get("neutral", 0)
        total = gainers + losers + neutral
        if total > 0:
            gainer_percentage = (gainers / total) * 100
            loser_percentage = (losers / total) * 100
        else:
            gainer_percentage = loser_percentage = 0
        # Generate analysis text
        analysis = "MARKET ANALYSIS REPORT\n"
        analysis += "=" * 50 + "\n\n"
        # Overall sentiment
        analysis += "📊 OVERALL SENTIMENT:\n"
        analysis += f"• Fear & Greed Index: {fgi_value}/100 ({fgi_class.upper()})\n"
        if fgi_value >= 75:
            analysis += "• Market Condition: EXTREME GREED - Overbought conditions\n"
            analysis += "• Risk Level: HIGH - Correction risk elevated\n"
        elif fgi_value >= 60:
            analysis += "• Market Condition: GREED - Bullish momentum\n"
            analysis += "• Risk Level: MODERATE-HIGH\n"
        elif fgi_value >= 45:
            analysis += "• Market Condition: NEUTRAL - Balanced market\n"
            analysis += "• Risk Level: MODERATE\n"
        elif fgi_value >= 30:
            analysis += "• Market Condition: FEAR - Cautious sentiment\n"
            analysis += "• Risk Level: MODERATE-LOW\n"
        else:
            analysis += "• Market Condition: EXTREME FEAR - Oversold conditions\n"
            analysis += "• Risk Level: LOW - Potential buying opportunity\n"
        analysis += "\n📈 MARKET DISTRIBUTION:\n"
        analysis += f"• Gainers: {gainers} coins ({gainer_percentage:.1f}% of market)\n"
        analysis += f"• Losers: {losers} coins ({loser_percentage:.1f}% of market)\n"
        analysis += f"• Neutral: {neutral} coins\n"
        # Market breadth analysis
        if gainer_percentage > 60:
            analysis += "• Market Breadth: STRONGLY POSITIVE\n"
        elif gainer_percentage > 55:
            analysis += "• Market Breadth: POSITIVE\n"
        elif loser_percentage > 60:
            analysis += "• Market Breadth: STRONGLY NEGATIVE\n"
        elif loser_percentage > 55:
            analysis += "• Market Breadth: NEGATIVE\n"
        else:
            analysis += "• Market Breadth: MIXED\n"
        analysis += "\n🎯 TRADING RECOMMENDATIONS:\n"
        # Generate recommendations based on FGI and market breadth
        if fgi_value >= 75 and gainer_percentage > 60:
            analysis += "• REDUCE EXPOSURE: Market extremely greedy and overbought\n"
            analysis += "• Consider taking profits on winning positions\n"
            analysis += "• Set tighter stop losses\n"
            analysis += "• Wait for pullback to add new positions\n"
        elif fgi_value >= 60:
            if gainer_percentage > 55:
                analysis += "• CAUTIOUS OPTIMISM: Bullish but approaching greed\n"
                analysis += "• Continue holding core positions\n"
                analysis += "• Consider partial profit taking\n"
                analysis += "• Scale into new positions on dips\n"
            else:
                analysis += "• SELECTIVE BUYING: Greed but mixed market\n"
                analysis += "• Focus on strongest performers\n"
                analysis += "• Use dollar-cost averaging\n"
        elif 45 <= fgi_value < 60:
            analysis += "• STRATEGIC ACCUMULATION: Neutral market\n"
            analysis += "• Good time for strategic entries\n"
            analysis += "• Build positions gradually\n"
            analysis += "• Focus on fundamentals\n"
        elif fgi_value >= 30:
            analysis += "• CAUTIOUS ACCUMULATION: Fearful market\n"
            analysis += "• Consider adding to long-term holdings\n"
            analysis += "• Look for oversold quality projects\n"
            analysis += "• Diversify across sectors\n"
        else:
            analysis += "• AGGRESSIVE ACCUMULATION: Extreme fear\n"
            analysis += "• High-conviction buying opportunities\n"
            analysis += "• Focus on BTC and blue-chip alts\n"
            analysis += "• Consider staking for long-term\n"
        analysis += "\n⚠️ RISK MANAGEMENT:\n"
        analysis += "• Never invest more than you can afford to lose\n"
        analysis += "• Diversify across different crypto sectors\n"
        analysis += "• Use stop-loss orders for protection\n"
        analysis += "• Consider taking profits at predetermined levels\n"
        analysis += "\n🔄 MARKET CYCLES:\n"
        analysis += (
            f"Current phase: {self.get_market_phase(fgi_value, gainer_percentage)}\n"
        )
        analysis += (
            "Typical cycle: Fear → Neutral → Greed → Extreme Greed → Correction\n"
        )
        analysis += "\n📅 Last Updated: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return analysis

    def get_market_phase(self, fgi_value, gainer_percentage):
        """Determine current market phase"""
        if fgi_value <= 25:
            return "Capitulation Phase (Extreme Fear)"
        elif fgi_value <= 45:
            return "Accumulation Phase (Fear)"
        elif fgi_value <= 55:
            return "Markup Phase (Neutral)"
        elif fgi_value <= 75:
            return "Distribution Phase (Greed)"
        else:
            return "Euphoria Phase (Extreme Greed)"


class EnhancedPortfolioTab(QWidget):
    """Enhanced portfolio management with direct market integration"""

    def __init__(self, api_handler, portfolio_tracker):
        super().__init__()
        self.api = api_handler
        self.portfolio = portfolio_tracker
        self.coins_data = []
        self.init_ui()
        self.refresh_portfolio()
        # Auto-refresh portfolio values every minute
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh_portfolio_values)
        self.timer.start(60000)  # 1 minute

    def init_ui(self):
        layout = QVBoxLayout()
        # Title
        title_label = QLabel("Portfolio Management")
        title_label.setStyleSheet(
            "font-size: 20px; font-weight: bold; margin: 10px; color: #2c3e50;"
        )
        layout.addWidget(title_label)
        # Summary panel
        summary_panel = self.create_summary_panel()
        layout.addWidget(summary_panel)
        # Controls panel
        controls_panel = self.create_controls_panel()
        layout.addWidget(controls_panel)
        # Holdings table
        self.holdings_table = QTableWidget()
        self.holdings_table.setColumnCount(10)
        self.holdings_table.setHorizontalHeaderLabels(
            [
                "Coin",
                "Symbol",
                "Amount",
                "Avg Cost",
                "Current Price",
                "Current Value",
                "P/L ($)",
                "P/L (%)",
                "Allocation %",
                "Actions",
            ]
        )
        # Configure table
        self.holdings_table.setAlternatingRowColors(True)
        self.holdings_table.setSortingEnabled(True)
        self.holdings_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.holdings_table)
        # Transaction history
        history_panel = QGroupBox("Transaction History")
        history_layout = QVBoxLayout()
        self.transaction_table = QTableWidget()
        self.transaction_table.setColumnCount(7)
        self.transaction_table.setHorizontalHeaderLabels(
            ["Date", "Type", "Coin", "Amount", "Price", "Total", "Status"]
        )
        history_layout.addWidget(self.transaction_table)
        history_panel.setLayout(history_layout)
        layout.addWidget(history_panel)
        self.setLayout(layout)

    def create_summary_panel(self):
        """Create portfolio summary panel"""
        panel = QGroupBox("Portfolio Summary")
        layout = QGridLayout()
        # Total value
        self.total_value_label = QLabel("Total Value: $0.00")
        self.total_value_label.setStyleSheet(
            "font-size: 18px; font-weight: bold; color: #2c3e50;"
        )
        layout.addWidget(self.total_value_label, 0, 0, 1, 2)
        # P/L
        self.total_pnl_label = QLabel("Total P/L: $0.00 (0.00%)")
        layout.addWidget(self.total_pnl_label, 1, 0)
        # 24h change
        self.daily_change_label = QLabel("24h Change: $0.00 (0.00%)")
        layout.addWidget(self.daily_change_label, 1, 1)
        # Best performer
        self.best_performer_label = QLabel("Best Performer: N/A")
        layout.addWidget(self.best_performer_label, 2, 0)
        # Worst performer
        self.worst_performer_label = QLabel("Worst Performer: N/A")
        layout.addWidget(self.worst_performer_label, 2, 1)
        # Diversity score
        self.diversity_label = QLabel("Diversity Score: 0/100")
        layout.addWidget(self.diversity_label, 3, 0)
        # Risk level
        self.risk_level_label = QLabel("Risk Level: N/A")
        layout.addWidget(self.risk_level_label, 3, 1)
        panel.setLayout(layout)
        return panel

    def create_controls_panel(self):
        """Create portfolio controls panel"""
        panel = QGroupBox("Portfolio Controls")
        layout = QHBoxLayout()
        # Quick add from market
        self.quick_add_button = QPushButton("➕ Add from Market")
        self.quick_add_button.clicked.connect(self.quick_add_from_market)
        self.quick_add_button.setStyleSheet(
            """
            QPushButton {
                padding: 8px 15px;
                background-color: #27ae60;
                color: white;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """
        )
        layout.addWidget(self.quick_add_button)
        # Add transaction
        self.add_tx_button = QPushButton("📝 Add Transaction")
        self.add_tx_button.clicked.connect(self.add_transaction)
        layout.addWidget(self.add_tx_button)
        # Import CSV
        self.import_button = QPushButton("📂 Import CSV")
        self.import_button.clicked.connect(self.import_portfolio)
        layout.addWidget(self.import_button)
        # Export CSV
        self.export_button = QPushButton("💾 Export CSV")
        self.export_button.clicked.connect(self.export_portfolio)
        layout.addWidget(self.export_button)
        # Refresh
        self.refresh_button = QPushButton("🔄 Refresh")
        self.refresh_button.clicked.connect(self.refresh_portfolio)
        layout.addWidget(self.refresh_button)
        layout.addStretch()
        panel.setLayout(layout)
        return panel

    def quick_add_from_market(self):
        """Quick add from market view"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Coin from Market")
        dialog.setMinimumSize(500, 400)
        layout = QVBoxLayout()
        # Search bar
        search_layout = QHBoxLayout()
        search_label = QLabel("Search:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search coins...")
        self.search_input.textChanged.connect(self.search_coins)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)
        # Coin list
        self.coin_list = QListWidget()
        self.coin_list.itemDoubleClicked.connect(self.select_coin)
        layout.addWidget(self.coin_list)
        # Load top coins
        self.load_market_coins()
        dialog.setLayout(layout)
        dialog.exec_()

    def load_market_coins(self):
        """Load market coins into list"""
        try:
            self.coins_data = self.api.get_top_coins(limit=100)
            self.coin_list.clear()
            for coin in self.coins_data:
                name = coin.get("name", "Unknown")
                symbol = coin.get("symbol", "").upper()
                price = coin.get("current_price", 0)
                item_text = f"{name} ({symbol}) - ${price:,.4f}"
                item = QListWidgetItem(item_text)
                item.setData(Qt.UserRole, coin["id"])
                self.coin_list.addItem(item)
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to load market coins: {str(e)}"
            )

    def search_coins(self):
        """Filter coins based on search"""
        search_text = self.search_input.text().lower()
        if not search_text:
            self.load_market_coins()
            return
        self.coin_list.clear()
        for coin in self.coins_data:
            name = coin.get("name", "").lower()
            symbol = coin.get("symbol", "").lower()
            if search_text in name or search_text in symbol:
                item_text = f"{coin['name']} ({coin['symbol'].upper()}) - ${coin['current_price']:,.4f}"
                item = QListWidgetItem(item_text)
                item.setData(Qt.UserRole, coin["id"])
                self.coin_list.addItem(item)

    def select_coin(self, item):
        """Select coin from list and open transaction dialog"""
        coin_id = item.data(Qt.UserRole)
        # Find coin data
        coin_data = None
        for coin in self.coins_data:
            if coin["id"] == coin_id:
                coin_data = coin
                break
        if coin_data:
            self.open_transaction_dialog(coin_data)

    def open_transaction_dialog(self, coin_data):
        """Open transaction dialog for selected coin"""
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Add {coin_data['name']} to Portfolio")
        dialog.setFixedSize(400, 300)
        layout = QVBoxLayout()
        # Coin info
        info_group = QGroupBox("Coin Information")
        info_layout = QFormLayout()
        info_layout.addRow("Coin:", QLabel(coin_data["name"]))
        info_layout.addRow("Symbol:", QLabel(coin_data["symbol"].upper()))
        info_layout.addRow(
            "Current Price:", QLabel(f"${coin_data['current_price']:,.4f}")
        )
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        # Transaction details
        tx_group = QGroupBox("Transaction Details")
        tx_layout = QFormLayout()
        # Type
        type_combo = QComboBox()
        type_combo.addItems(["Buy", "Sell"])
        tx_layout.addRow("Type:", type_combo)
        # Amount
        amount_input = QDoubleSpinBox()
        amount_input.setRange(0.00000001, 1000000)
        amount_input.setDecimals(8)
        amount_input.setValue(0.1)
        tx_layout.addRow("Amount:", amount_input)
        # Price per coin
        price_input = QDoubleSpinBox()
        price_input.setRange(0.00000001, 1000000)
        price_input.setDecimals(8)
        price_input.setValue(coin_data["current_price"])
        tx_layout.addRow("Price per Coin:", price_input)
        # Date
        date_input = QLineEdit(datetime.now().strftime("%Y-%m-%d"))
        tx_layout.addRow("Date:", date_input)
        tx_group.setLayout(tx_layout)
        layout.addWidget(tx_group)
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        dialog.setLayout(layout)
        if dialog.exec_():
            try:
                # Add transaction
                self.portfolio.add_transaction(
                    coin_id=coin_data["id"],
                    coin_name=coin_data["name"],
                    transaction_type=type_combo.currentText().lower(),
                    amount=amount_input.value(),
                    price=price_input.value(),
                    date=date_input.text(),
                )
                QMessageBox.information(
                    self,
                    "Success",
                    f"Added {amount_input.value()} {coin_data['symbol'].upper()} to portfolio!",
                )
                self.refresh_portfolio()
            except Exception as e:
                QMessageBox.critical(
                    self, "Error", f"Failed to add transaction: {str(e)}"
                )


class EnhancedCryptoTrackerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CoinSentinel AI - Enhanced Cryptocurrency Tracker")
        self.setGeometry(100, 100, 1600, 900)
        # Initialize components
        self.api = EnhancedCryptoAPIHandler()
        self.predictor = AdvancedPricePredictor(self.api)
        self.portfolio = PortfolioTracker()
        self.init_ui()
        # Load initial data
        QTimer.singleShot(100, self.load_initial_data)

    def init_ui(self):
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        # Create tab widget
        self.tabs = QTabWidget()
        # Add enhanced tabs
        self.tabs.addTab(ImprovedMarketTab(self.api), "Market Overview")
        self.tabs.addTab(
            EnhancedPredictionTab(self.api, self.predictor), "AI Predictions"
        )
        self.tabs.addTab(EnhancedPortfolioTab(self.api, self.portfolio), "Portfolio")
        self.tabs.addTab(EnhancedSentimentTab(self.api), "Market Sentiment")
        main_layout.addWidget(self.tabs)
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("CoinSentinel Enhanced v2.0 - Ready")

    def load_initial_data(self):
        """Load initial data"""
        self.status_bar.showMessage("Loading initial data...")
        # Data will be loaded by individual tabs
        self.status_bar.showMessage("Ready - Data loading in background")

    def __init__(self):
        super().__init__()
        self.setWindowTitle("CoinSentinel AI - Advanced Cryptocurrency Tracker")
        self.setGeometry(100, 100, 1400, 850)
        # Initialize components
        self.api = EnhancedCryptoAPIHandler()
        self.predictor = AdvancedPricePredictor(self.api)
        self.portfolio = PortfolioTracker()
        self.sentiment = SentimentTracker(self.api)
        self.current_currency = "usd"
        self.top_coins = []
        self.init_ui()

    def init_ui(self):
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        # Create tab widget
        self.tabs = QTabWidget()
        # Add tabs
        self.tabs.addTab(self.create_market_tab(), "Market Overview")
        self.tabs.addTab(
            EnhancedPredictionTab(self.api, self.predictor), "AI Predictions"
        )
        self.tabs.addTab(self.create_portfolio_tab(), "Portfolio")
        self.tabs.addTab(self.create_sentiment_tab(), "Market Sentiment")
        main_layout.addWidget(self.tabs)
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Application ready")
        # Initialize data
        self.load_initial_data()

    def show_market_context_menu(self, position):
        menu = QMenu()
        predict_action = menu.addAction("Predict Price")
        action = menu.exec_(self.market_table.viewport().mapToGlobal(position))

        if action == predict_action:
            row = self.market_table.rowAt(position.y())
            if row >= 0:
                name_item = self.market_table.item(row, 1)
                if name_item:
                    coin_id = name_item.data(Qt.UserRole)
                    if coin_id:
                        self.open_prediction_tab(coin_id)

    def open_prediction_tab(self, coin_id):
        """Switch to prediction tab and select coin"""
        # Prediction tab is at index 1
        self.tabs.setCurrentIndex(1)
        # Get the prediction tab widget
        prediction_tab = self.tabs.currentWidget()
        if hasattr(prediction_tab, 'set_current_coin'):
            prediction_tab.set_current_coin(coin_id)

    def create_market_tab(self):
        """Create market overview tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        # Controls panel
        control_panel = QGroupBox("Market Controls")
        control_layout = QHBoxLayout()
        # Currency selection
        control_layout.addWidget(QLabel("Currency:"))
        self.currency_combo = QComboBox()
        self.currency_combo.addItems(["USD", "EUR", "GBP", "JPY", "BTC"])
        self.currency_combo.currentTextChanged.connect(self.change_currency)
        control_layout.addWidget(self.currency_combo)
        # Refresh button
        self.refresh_button = QPushButton("Refresh Data")
        self.refresh_button.clicked.connect(self.refresh_market_data)
        control_layout.addWidget(self.refresh_button)
        # Export button
        self.export_button = QPushButton("Export to CSV")
        self.export_button.clicked.connect(self.export_market_data)
        control_layout.addWidget(self.export_button)
        # Auto-refresh toggle
        control_layout.addWidget(QLabel("Auto-refresh:"))
        self.auto_refresh_combo = QComboBox()
        self.auto_refresh_combo.addItems(["Off", "30 seconds", "1 minute", "5 minutes"])
        self.auto_refresh_combo.currentTextChanged.connect(self.toggle_auto_refresh)
        control_layout.addWidget(self.auto_refresh_combo)
        control_layout.addStretch()
        control_panel.setLayout(control_layout)
        layout.addWidget(control_panel)
        # Market data table
        self.market_table = QTableWidget()
        self.market_table.setColumnCount(11)
        self.market_table.setHorizontalHeaderLabels(
            [
                "Rank",
                "Coin",
                "Symbol",
                "Price",
                "1h %",
                "24h %",
                "7d %",
                "Market Cap",
                "Volume (24h)",
                "AI Prediction",
                "AI Confidence",
            ]
        )
        # Configure table headers
        header = self.market_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Rank
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # Coin
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Symbol
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Price
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # 1h %
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # 24h %
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # 7d %
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents)  # Market Cap
        header.setSectionResizeMode(8, QHeaderView.ResizeToContents)  # Volume
        header.setSectionResizeMode(9, QHeaderView.ResizeToContents)  # Prediction
        header.setSectionResizeMode(10, QHeaderView.ResizeToContents)  # Confidence
        # Set table properties
        self.market_table.setSortingEnabled(True)
        self.market_table.setAlternatingRowColors(True)
        self.market_table.verticalHeader().setVisible(False)

        # Add context menu
        self.market_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.market_table.customContextMenuRequested.connect(self.show_market_context_menu)

        layout.addWidget(self.market_table)
        # Statistics panel
        stats_panel = QGroupBox("Market Statistics")
        stats_layout = QHBoxLayout()
        self.total_market_cap_label = QLabel("Total Market Cap: N/A")
        self.total_volume_label = QLabel("24h Volume: N/A")
        self.btc_dominance_label = QLabel("BTC Dominance: N/A")
        self.active_coins_label = QLabel("Active Coins: N/A")
        stats_layout.addWidget(self.total_market_cap_label)
        stats_layout.addWidget(self.total_volume_label)
        stats_layout.addWidget(self.btc_dominance_label)
        stats_layout.addWidget(self.active_coins_label)
        stats_layout.addStretch()
        stats_panel.setLayout(stats_layout)
        layout.addWidget(stats_panel)
        return widget

    def create_portfolio_tab(self):
        """Create portfolio management tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        # Portfolio controls
        control_panel = QGroupBox("Portfolio Controls")
        control_layout = QHBoxLayout()
        self.add_transaction_button = QPushButton("Add Transaction")
        self.add_transaction_button.clicked.connect(self.add_transaction)
        control_layout.addWidget(self.add_transaction_button)
        self.refresh_portfolio_button = QPushButton("Refresh Portfolio")
        self.refresh_portfolio_button.clicked.connect(self.refresh_portfolio)
        control_layout.addWidget(self.refresh_portfolio_button)
        self.export_portfolio_button = QPushButton("Export Portfolio")
        self.export_portfolio_button.clicked.connect(self.export_portfolio)
        control_layout.addWidget(self.export_portfolio_button)
        control_layout.addStretch()
        control_panel.setLayout(control_layout)
        layout.addWidget(control_panel)
        # Portfolio summary
        summary_panel = QGroupBox("Portfolio Summary")
        summary_layout = QGridLayout()
        self.total_value_label = QLabel("Total Value: $0.00")
        self.total_value_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        summary_layout.addWidget(self.total_value_label, 0, 0)
        self.total_pnl_label = QLabel("Total P/L: $0.00 (0.00%)")
        summary_layout.addWidget(self.total_pnl_label, 0, 1)
        self.daily_change_label = QLabel("24h Change: $0.00 (0.00%)")
        summary_layout.addWidget(self.daily_change_label, 1, 0)
        self.best_performer_label = QLabel("Best Performer: N/A")
        summary_layout.addWidget(self.best_performer_label, 1, 1)
        self.diversity_score_label = QLabel("Diversity Score: 0/100")
        summary_layout.addWidget(self.diversity_score_label, 2, 0)
        self.risk_score_label = QLabel("Risk Score: Medium")
        summary_layout.addWidget(self.risk_score_label, 2, 1)
        summary_panel.setLayout(summary_layout)
        layout.addWidget(summary_panel)
        # Portfolio holdings table
        self.portfolio_table = QTableWidget()
        self.portfolio_table.setColumnCount(9)
        self.portfolio_table.setHorizontalHeaderLabels(
            [
                "Coin",
                "Symbol",
                "Amount",
                "Avg Cost",
                "Current Price",
                "Current Value",
                "P/L ($)",
                "P/L (%)",
                "Allocation %",
            ]
        )
        # Configure table
        self.portfolio_table.setSortingEnabled(True)
        self.portfolio_table.setAlternatingRowColors(True)
        layout.addWidget(self.portfolio_table)
        return widget

    def create_sentiment_tab(self):
        """Create market sentiment tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        # Fear & Greed Index
        fgi_panel = QGroupBox("Crypto Fear & Greed Index")
        fgi_layout = QGridLayout()
        self.fgi_value_label = QLabel("Loading...")
        self.fgi_value_label.setStyleSheet("font-size: 32px; font-weight: bold;")
        fgi_layout.addWidget(self.fgi_value_label, 0, 0, 2, 1)
        self.fgi_class_label = QLabel("")
        self.fgi_class_label.setStyleSheet("font-size: 18px;")
        fgi_layout.addWidget(self.fgi_class_label, 0, 1)
        self.fgi_timestamp_label = QLabel("")
        fgi_layout.addWidget(self.fgi_timestamp_label, 1, 1)
        # FGI description
        self.fgi_description = QLabel("")
        self.fgi_description.setWordWrap(True)
        fgi_layout.addWidget(self.fgi_description, 2, 0, 1, 2)
        fgi_panel.setLayout(fgi_layout)
        layout.addWidget(fgi_panel)
        # Market sentiment analysis
        analysis_panel = QGroupBox("Market Sentiment Analysis")
        analysis_layout = QVBoxLayout()
        self.sentiment_text = QTextEdit()
        self.sentiment_text.setReadOnly(True)
        self.sentiment_text.setMaximumHeight(200)
        analysis_layout.addWidget(self.sentiment_text)
        analysis_panel.setLayout(analysis_layout)
        layout.addWidget(analysis_panel)
        # Market statistics
        stats_panel = QGroupBox("Market Statistics")
        stats_layout = QHBoxLayout()
        self.gainers_count_label = QLabel("Gainers (24h): N/A")
        self.losers_count_label = QLabel("Losers (24h): N/A")
        self.extreme_greed_label = QLabel("Extreme Greed: N/A")
        self.extreme_fear_label = QLabel("Extreme Fear: N/A")
        stats_layout.addWidget(self.gainers_count_label)
        stats_layout.addWidget(self.losers_count_label)
        stats_layout.addWidget(self.extreme_greed_label)
        stats_layout.addWidget(self.extreme_fear_label)
        stats_layout.addStretch()
        stats_panel.setLayout(stats_layout)
        layout.addWidget(stats_panel)
        return widget

    def load_initial_data(self):
        """Load initial data"""
        self.status_bar.showMessage("Loading initial data...")
        # Load market data
        self.refresh_market_data()
        # Load sentiment data
        self.refresh_sentiment()
        # Load portfolio if exists
        self.refresh_portfolio()
        self.status_bar.showMessage("Ready")

    def change_currency(self, currency):
        """Change display currency"""
        self.current_currency = currency.lower()
        self.refresh_market_data()

    def refresh_market_data(self):
        """Refresh market data with ML predictions"""
        try:
            self.status_bar.showMessage("Fetching market data...")
            self.refresh_button.setEnabled(False)
            # Get top coins
            coins = self.api.get_top_coins(limit=100, vs_currency=self.current_currency)
            self.top_coins = coins
            if not coins:
                self.status_bar.showMessage("No market data available")
                return
            self.market_table.setRowCount(len(coins))
            total_market_cap = 0
            total_volume = 0
            for row, coin in enumerate(coins):
                # Extract data
                rank = coin.get("market_cap_rank", row + 1)
                name = coin.get("name", "Unknown")
                symbol = coin.get("symbol", "").upper()
                price = coin.get("current_price", 0)
                # Price changes (handle None values)
                change_1h = coin.get("price_change_percentage_1h_in_currency", 0) or 0
                change_24h = coin.get("price_change_percentage_24h", 0) or 0
                change_7d = coin.get("price_change_percentage_7d_in_currency", 0) or 0
                # Market data
                market_cap = coin.get("market_cap", 0)
                volume = coin.get("total_volume", 0)
                # Accumulate totals
                total_market_cap += market_cap
                total_volume += volume
                # Get ML prediction (in background to avoid UI freeze)
                coin_id = coin.get("id")
                # Fill table with basic data
                self.market_table.setItem(row, 0, QTableWidgetItem(str(rank)))

                # Store coin_id in name item
                name_item = QTableWidgetItem(name)
                name_item.setData(Qt.UserRole, coin_id)
                self.market_table.setItem(row, 1, name_item)

                self.market_table.setItem(row, 2, QTableWidgetItem(symbol))
                self.market_table.setItem(row, 3, QTableWidgetItem(f"{price:,.2f}"))
                # Add percentage changes with color coding
                for col_idx, value in enumerate(
                    [change_1h, change_24h, change_7d], start=4
                ):
                    item = QTableWidgetItem(f"{value:+.2f}%")
                    if value > 0:
                        item.setForeground(QBrush(QColor("#00aa00")))  # Green
                    elif value < 0:
                        item.setForeground(QBrush(QColor("#aa0000")))  # Red
                    self.market_table.setItem(row, col_idx, item)
                # Market cap and volume
                self.market_table.setItem(
                    row, 7, QTableWidgetItem(f"{market_cap:,.0f}")
                )
                self.market_table.setItem(row, 8, QTableWidgetItem(f"{volume:,.0f}"))
                # Get prediction in background thread
                # Disabled auto-prediction to improve performance
                # User can request prediction via context menu
                # QTimer.singleShot(
                #     row * 100,
                #     lambda r=row, cid=coin_id, p=price: self.update_prediction_cell(
                #         r, cid, p
                #     ),
                # )
            # Update statistics
            self.update_market_statistics(total_market_cap, total_volume, coins)
            self.status_bar.showMessage(f"Market data updated: {len(coins)} coins")
        except Exception as e:
            self.status_bar.showMessage(f"Error: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to load market data: {str(e)}")
        finally:
            self.refresh_button.setEnabled(True)

    def update_prediction_cell(self, row, coin_id, current_price):
        """Update prediction cell for a specific coin"""
        try:
            if coin_id:
                prediction = self.predictor.predict_price(coin_id, current_price)
                if prediction:
                    pred_price = prediction["predicted_price"]
                    confidence = prediction["confidence_score"]
                    pred_change = ((pred_price - current_price) / current_price) * 100
                    # Prediction cell
                    pred_item = QTableWidgetItem(f"{pred_price:,.2f}")
                    if pred_change > 0:
                        pred_item.setForeground(QBrush(QColor("#00aa00")))
                    elif pred_change < 0:
                        pred_item.setForeground(QBrush(QColor("#aa0000")))
                    pred_item.setToolTip(f"Predicted change: {pred_change:+.2f}%")
                    self.market_table.setItem(row, 9, pred_item)
                    # Confidence cell
                    conf_item = QTableWidgetItem(f"{confidence:.1f}%")
                    if confidence >= 70:
                        conf_item.setForeground(QBrush(QColor("#00aa00")))
                    elif confidence >= 50:
                        conf_item.setForeground(QBrush(QColor("#ffaa00")))
                    else:
                        conf_item.setForeground(QBrush(QColor("#aa0000")))
                    self.market_table.setItem(row, 10, conf_item)
        except:
            pass  # Silently fail for individual predictions

    def update_market_statistics(self, total_market_cap, total_volume, coins):
        """Update market statistics display"""
        # Find BTC dominance
        btc_dominance = 0
        active_coins = len([c for c in coins if c.get("active", True)])
        for coin in coins:
            if coin.get("symbol", "").lower() == "btc":
                btc_dominance = coin.get("market_cap_percentage", 0)
                break
        # Update labels
        currency_symbol = (
            "$" if self.current_currency == "usd" else self.current_currency.upper()
        )
        self.total_market_cap_label.setText(
            f"Total Market Cap: {currency_symbol}{total_market_cap:,.0f}"
        )
        self.total_volume_label.setText(
            f"24h Volume: {currency_symbol}{total_volume:,.0f}"
        )
        self.btc_dominance_label.setText(f"BTC Dominance: {btc_dominance:.1f}%")
        self.active_coins_label.setText(f"Active Coins: {active_coins}")

    def export_market_data(self):
        """Export market data to CSV"""
        try:
            if not self.top_coins:
                QMessageBox.warning(self, "No Data", "No market data to export")
                return
            filename, _ = QFileDialog.getSaveFileName(
                self,
                "Export Market Data",
                "market_data.csv",
                "CSV Files (*.csv);;All Files (*)",
            )
            if filename:
                # Create DataFrame from coins data
                df_data = []
                for coin in self.top_coins:
                    # Get prediction for this coin
                    coin_id = coin.get("id")
                    price = coin.get("current_price", 0)
                    prediction = (
                        self.predictor.predict_price(coin_id, price) if coin_id else {}
                    )
                    row_data = {
                        "rank": coin.get("market_cap_rank", ""),
                        "name": coin.get("name", ""),
                        "symbol": coin.get("symbol", "").upper(),
                        "price": price,
                        "price_change_1h": coin.get(
                            "price_change_percentage_1h_in_currency", 0
                        )
                        or 0,
                        "price_change_24h": coin.get("price_change_percentage_24h", 0)
                        or 0,
                        "price_change_7d": coin.get(
                            "price_change_percentage_7d_in_currency", 0
                        )
                        or 0,
                        "market_cap": coin.get("market_cap", 0),
                        "volume_24h": coin.get("total_volume", 0),
                        "predicted_price": prediction.get("predicted_price", 0),
                        "predicted_change": prediction.get(
                            "predicted_change_percent", 0
                        ),
                        "confidence_score": prediction.get("confidence_score", 0),
                        "direction": prediction.get("direction", "neutral"),
                        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    }
                    df_data.append(row_data)
                df = pd.DataFrame(df_data)
                df.to_csv(filename, index=False)
                self.status_bar.showMessage(f"Market data exported to {filename}")
                QMessageBox.information(
                    self,
                    "Export Complete",
                    f"Market data successfully exported to:\n{filename}",
                )
        except Exception as e:
            QMessageBox.critical(
                self, "Export Error", f"Failed to export data: {str(e)}"
            )

    def toggle_auto_refresh(self, option):
        """Toggle auto-refresh timer"""
        if hasattr(self, "auto_refresh_timer"):
            self.auto_refresh_timer.stop()
        intervals = {
            "Off": 0,
            "30 seconds": 30000,
            "1 minute": 60000,
            "5 minutes": 300000,
        }
        interval = intervals.get(option, 0)
        if interval > 0:
            self.auto_refresh_timer = QTimer()
            self.auto_refresh_timer.timeout.connect(self.refresh_market_data)
            self.auto_refresh_timer.start(interval)
            self.status_bar.showMessage(f"Auto-refresh enabled: {option}")
        else:
            self.status_bar.showMessage("Auto-refresh disabled")

    def add_transaction(self):
        """Open dialog to add transaction"""
        dialog = AddTransactionDialog(self)
        # Load coins into dialog
        if self.top_coins:
            dialog.load_coins(self.top_coins[:50])  # Top 50 coins
        if dialog.exec_():
            transaction_data = dialog.get_data()
            # Validate data
            if not transaction_data["coin"]:
                QMessageBox.warning(self, "Error", "Please select a coin")
                return
            if transaction_data["amount"] <= 0:
                QMessageBox.warning(self, "Error", "Amount must be greater than 0")
                return
            if transaction_data["price"] <= 0:
                QMessageBox.warning(self, "Error", "Price must be greater than 0")
                return
            # Add transaction to portfolio
            try:
                self.portfolio.add_transaction(
                    coin_id=transaction_data["coin"],
                    coin_name=dialog.coin_combo.currentText().split(" - ")[0],
                    transaction_type=transaction_data["type"],
                    amount=transaction_data["amount"],
                    price=transaction_data["price"],
                    date=transaction_data["date"],
                )
                self.refresh_portfolio()
                self.status_bar.showMessage("Transaction added successfully")
            except Exception as e:
                QMessageBox.critical(
                    self, "Error", f"Failed to add transaction: {str(e)}"
                )

    def refresh_portfolio(self):
        """Refresh portfolio display"""
        try:
            portfolio_data = self.portfolio.get_portfolio_summary()
            if not portfolio_data["holdings"]:
                self.portfolio_table.setRowCount(0)
                self.total_value_label.setText("Total Value: $0.00")
                self.total_pnl_label.setText("Total P/L: $0.00 (0.00%)")
                return
            # Update summary
            total_value = portfolio_data["total_value"]
            total_pnl = portfolio_data["total_pnl"]
            total_pnl_percent = portfolio_data["total_pnl_percent"]
            daily_change = portfolio_data["daily_change"]
            daily_change_percent = portfolio_data["daily_change_percent"]
            # Color code P/L
            pnl_color = "#00aa00" if total_pnl >= 0 else "#aa0000"
            daily_color = "#00aa00" if daily_change >= 0 else "#aa0000"
            self.total_value_label.setText(f"Total Value: ${total_value:,.2f}")
            self.total_pnl_label.setText(
                f'<span style="color: {pnl_color}">'
                f"Total P/L: ${total_pnl:,.2f} ({total_pnl_percent:+.2f}%)"
                f"</span>"
            )
            self.daily_change_label.setText(
                f'<span style="color: {daily_color}">'
                f"24h Change: ${daily_change:,.2f} ({daily_change_percent:+.2f}%)"
                f"</span>"
            )
            # Find best performer
            best_performer = None
            best_performer_pnl = -float("inf")
            for holding in portfolio_data["holdings"]:
                pnl_percent = holding.get("pnl_percent", 0)
                if pnl_percent > best_performer_pnl:
                    best_performer_pnl = pnl_percent
                    best_performer = holding.get("symbol", "")
            if best_performer:
                best_color = "#00aa00" if best_performer_pnl >= 0 else "#aa0000"
                self.best_performer_label.setText(
                    f'<span style="color: {best_color}">'
                    f"Best Performer: {best_performer} ({best_performer_pnl:+.2f}%)"
                    f"</span>"
                )
            # Update diversity and risk scores
            self.diversity_score_label.setText(
                f"Diversity Score: {portfolio_data.get('diversity_score', 0)}/100"
            )
            self.risk_score_label.setText(
                f"Risk Score: {portfolio_data.get('risk_level', 'Medium')}"
            )
            # Update holdings table
            holdings = portfolio_data["holdings"]
            self.portfolio_table.setRowCount(len(holdings))
            for row, holding in enumerate(holdings):
                symbol = holding.get("symbol", "")
                name = holding.get("name", "")
                amount = holding.get("amount", 0)
                avg_cost = holding.get("avg_cost", 0)
                current_price = holding.get("current_price", 0)
                current_value = holding.get("current_value", 0)
                pnl_amount = holding.get("pnl_amount", 0)
                pnl_percent = holding.get("pnl_percent", 0)
                allocation = holding.get("allocation", 0)
                # Fill table
                self.portfolio_table.setItem(row, 0, QTableWidgetItem(name))
                self.portfolio_table.setItem(row, 1, QTableWidgetItem(symbol))
                self.portfolio_table.setItem(row, 2, QTableWidgetItem(f"{amount:.8f}"))
                self.portfolio_table.setItem(
                    row, 3, QTableWidgetItem(f"${avg_cost:.4f}")
                )
                self.portfolio_table.setItem(
                    row, 4, QTableWidgetItem(f"${current_price:.4f}")
                )
                self.portfolio_table.setItem(
                    row, 5, QTableWidgetItem(f"${current_value:.2f}")
                )
                # P/L columns with color coding
                pnl_amount_item = QTableWidgetItem(f"${pnl_amount:,.2f}")
                pnl_percent_item = QTableWidgetItem(f"{pnl_percent:+.2f}%")
                if pnl_amount >= 0:
                    pnl_amount_item.setForeground(QBrush(QColor("#00aa00")))
                    pnl_percent_item.setForeground(QBrush(QColor("#00aa00")))
                else:
                    pnl_amount_item.setForeground(QBrush(QColor("#aa0000")))
                    pnl_percent_item.setForeground(QBrush(QColor("#aa0000")))
                self.portfolio_table.setItem(row, 6, pnl_amount_item)
                self.portfolio_table.setItem(row, 7, pnl_percent_item)
                # Allocation
                self.portfolio_table.setItem(
                    row, 8, QTableWidgetItem(f"{allocation:.1f}%")
                )
            self.status_bar.showMessage(f"Portfolio updated: {len(holdings)} holdings")
        except Exception as e:
            self.status_bar.showMessage(f"Error updating portfolio: {str(e)}")

    def export_portfolio(self):
        """Export portfolio to CSV"""
        try:
            portfolio_data = self.portfolio.get_portfolio_summary()
            if not portfolio_data["holdings"]:
                QMessageBox.warning(self, "No Data", "No portfolio data to export")
                return
            filename, _ = QFileDialog.getSaveFileName(
                self,
                "Export Portfolio",
                "portfolio.csv",
                "CSV Files (*.csv);;All Files (*)",
            )
            if filename:
                # Prepare data for export
                export_data = []
                for holding in portfolio_data["holdings"]:
                    export_data.append(
                        {
                            "coin": holding.get("name", ""),
                            "symbol": holding.get("symbol", ""),
                            "amount": holding.get("amount", 0),
                            "avg_cost": holding.get("avg_cost", 0),
                            "current_price": holding.get("current_price", 0),
                            "current_value": holding.get("current_value", 0),
                            "pnl_amount": holding.get("pnl_amount", 0),
                            "pnl_percent": holding.get("pnl_percent", 0),
                            "allocation": holding.get("allocation", 0),
                            "last_updated": datetime.now().strftime(
                                "%Y-%m-%d %H:%M:%S"
                            ),
                        }
                    )
                # Add summary row
                export_data.append(
                    {
                        "coin": "TOTAL",
                        "symbol": "",
                        "amount": "",
                        "avg_cost": "",
                        "current_price": "",
                        "current_value": portfolio_data["total_value"],
                        "pnl_amount": portfolio_data["total_pnl"],
                        "pnl_percent": portfolio_data["total_pnl_percent"],
                        "allocation": 100.0,
                        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    }
                )
                df = pd.DataFrame(export_data)
                df.to_csv(filename, index=False)
                self.status_bar.showMessage(f"Portfolio exported to {filename}")
                QMessageBox.information(
                    self,
                    "Export Complete",
                    f"Portfolio successfully exported to:\n{filename}",
                )
        except Exception as e:
            QMessageBox.critical(
                self, "Export Error", f"Failed to export portfolio: {str(e)}"
            )

    def refresh_sentiment(self):
        """Refresh market sentiment data"""
        try:
            self.status_bar.showMessage("Fetching market sentiment...")
            sentiment_data = self.sentiment.get_market_sentiment()
            if not sentiment_data:
                self.status_bar.showMessage("No sentiment data available")
                return
            # Update Fear & Greed Index
            fgi_value = sentiment_data.get("fear_greed", {}).get("value", 0)
            fgi_class = sentiment_data.get("fear_greed", {}).get("classification", "")
            fgi_timestamp = sentiment_data.get("fear_greed", {}).get("timestamp", "")
            # Set color and text based on FGI value
            if fgi_value >= 75:
                color = "#00aa00"  # Green
                description = "Extreme Greed - Market may be overbought"
            elif fgi_value >= 60:
                color = "#55aa00"  # Light green
                description = "Greed - Market is optimistic"
            elif fgi_value >= 45:
                color = "#aaaa00"  # Yellow
                description = "Neutral - Market is balanced"
            elif fgi_value >= 30:
                color = "#aa5500"  # Orange
                description = "Fear - Market is cautious"
            else:
                color = "#aa0000"  # Red
                description = "Extreme Fear - Market may be oversold"
            self.fgi_value_label.setText(str(fgi_value))
            self.fgi_value_label.setStyleSheet(
                f"font-size: 32px; font-weight: bold; color: {color};"
            )
            self.fgi_class_label.setText(fgi_class.upper())
            self.fgi_class_label.setStyleSheet(f"font-size: 18px; color: {color};")
            if fgi_timestamp:
                self.fgi_timestamp_label.setText(f"Last updated: {fgi_timestamp}")
            self.fgi_description.setText(description)
            # Update sentiment analysis text
            market_analysis = sentiment_data.get("market_analysis", {})
            gainers = market_analysis.get("gainers", 0)
            losers = market_analysis.get("losers", 0)
            neutral = market_analysis.get("neutral", 0)
            sentiment_text = f"""MARKET SENTIMENT ANALYSIS
Fear & Greed Index: {fgi_value}/100 ({fgi_class})
Market Analysis:
• Gainers (24h): {gainers} cryptocurrencies
• Losers (24h): {losers} cryptocurrencies
• Neutral: {neutral} cryptocurrencies
Market Conditions: {description}
Trading Implications:
{fgi_value >= 75 and "Extreme greed suggests caution - consider taking profits or setting stop losses." or ""}
{fgi_value <= 25 and "Extreme fear may present buying opportunities for long-term investors." or ""}
{45 <= fgi_value <= 55 and "Neutral market conditions suggest balanced risk-reward." or ""}
Last Updated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""
            self.sentiment_text.setPlainText(sentiment_text)
            # Update statistics
            self.gainers_count_label.setText(f"Gainers (24h): {gainers}")
            self.losers_count_label.setText(f"Losers (24h): {losers}")
            # Calculate percentages for extreme conditions
            total_coins = gainers + losers + neutral
            if total_coins > 0:
                extreme_greed_pct = (
                    market_analysis.get("extreme_gainers", 0) / total_coins * 100
                )
                extreme_fear_pct = (
                    market_analysis.get("extreme_losers", 0) / total_coins * 100
                )
                self.extreme_greed_label.setText(
                    f"Extreme Greed: {extreme_greed_pct:.1f}%"
                )
                self.extreme_fear_label.setText(
                    f"Extreme Fear: {extreme_fear_pct:.1f}%"
                )
            self.status_bar.showMessage("Sentiment data updated")
        except Exception as e:
            self.status_bar.showMessage(f"Error loading sentiment: {str(e)}")
            QMessageBox.warning(
                self, "Error", f"Failed to load sentiment data: {str(e)}"
            )
def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle("Fusion")

    # Create the main window - NO parameters needed!
    # CryptoTrackerApp creates everything inside itself
    window = EnhancedCryptoTrackerApp()  # <-- NO PARAMETERS!
    window.show()
    
    # Start event loop
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()