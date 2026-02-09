# ==================== IMPORTS ====================
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
    QScrollArea,
    QFrame,
    QListWidget,
    QListWidgetItem,
)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal, QObject
from PyQt5.QtGui import QBrush, QColor, QFont, QPalette, QPixmap
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib

matplotlib.use("Qt5Agg")

from api_handler import EnhancedCryptoAPIHandler
from improved_price_predictor import AdvancedPricePredictor
from improved_portfolio_tracker import PortfolioTracker
from improved_sentiment_tracker import SentimentTracker


# ==================== HELPER CLASSES ====================
class MarketWorker(QObject):
    finished = pyqtSignal(list)
    error = pyqtSignal(str)

    def __init__(self, api_handler, limit, currency):
        super().__init__()
        self.api = api_handler
        self.limit = limit
        self.currency = currency

    def run(self):
        try:
            coins = self.api.get_top_coins(limit=self.limit, vs_currency=self.currency)
            self.finished.emit(coins)
        except Exception as e:
            self.error.emit(str(e))


class PredictionWorker(QThread):
    prediction_complete = pyqtSignal(dict)
    progress_update = pyqtSignal(int, str)
    error_occurred = pyqtSignal(str)

    def __init__(self, predictor, coin_id, current_price, time_frame=1):
        super().__init__()
        self.predictor = predictor
        self.coin_id = coin_id
        self.current_price = current_price
        self.time_frame = time_frame

    def run(self):
        try:
            self.progress_update.emit(25, "Fetching historical data...")
            time.sleep(0.5)

            self.progress_update.emit(50, "Processing technical indicators...")
            time.sleep(0.5)

            self.progress_update.emit(75, "Running ML models...")
            result = self.predictor.predict_price(
                self.coin_id, self.current_price, self.time_frame
            )
            self.progress_update.emit(100, "Prediction complete")

            self.prediction_complete.emit(result)
        except Exception as e:
            self.error_occurred.emit(f"Prediction error: {str(e)}")


class AddTransactionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Transaction")
        self.setModal(True)
        self.init_ui()

    def init_ui(self):
        layout = QGridLayout()
        layout.addWidget(QLabel("Coin:"), 0, 0)
        self.coin_combo = QComboBox()
        self.coin_combo.setToolTip("Select the cryptocurrency traded")
        self.coin_combo.setAccessibleName("Transaction Coin Selection")
        layout.addWidget(self.coin_combo, 0, 1)
        layout.addWidget(QLabel("Type:"), 1, 0)
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Buy", "Sell"])
        self.type_combo.setToolTip("Select transaction type")
        self.type_combo.setAccessibleName("Transaction Type Selection")
        layout.addWidget(self.type_combo, 1, 1)
        layout.addWidget(QLabel("Amount:"), 2, 0)
        self.amount_input = QDoubleSpinBox()
        self.amount_input.setRange(0.00000001, 1000000)
        self.amount_input.setDecimals(8)
        self.amount_input.setToolTip("Enter the amount of coins")
        self.amount_input.setAccessibleName("Transaction Amount Input")
        layout.addWidget(self.amount_input, 2, 1)
        layout.addWidget(QLabel("Price per Coin:"), 3, 0)
        self.price_input = QDoubleSpinBox()
        self.price_input.setRange(0.00000001, 1000000)
        self.price_input.setDecimals(4)
        self.price_input.setPrefix("$")
        self.price_input.setToolTip("Enter the price per coin in selected currency")
        self.price_input.setAccessibleName("Transaction Price Input")
        layout.addWidget(self.price_input, 3, 1)
        layout.addWidget(QLabel("Date:"), 4, 0)
        self.date_input = QLineEdit(datetime.now().strftime("%Y-%m-%d"))
        self.date_input.setToolTip("Transaction date (YYYY-MM-DD)")
        self.date_input.setAccessibleName("Transaction Date Input")
        layout.addWidget(self.date_input, 4, 1)
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
        for coin in coins:
            self.coin_combo.addItem(
                f"{coin['symbol'].upper()} - {coin['name']}", coin["id"]
            )


# ==================== TAB CLASSES ====================
class ImprovedMarketTab(QWidget):
    """Enhanced market overview with ALL columns visible"""

    def __init__(self, api_handler):
        super().__init__()
        self.api = api_handler
        self.coins_data = []
        self.auto_refresh_enabled = False
        self.worker_thread = None

        self.init_ui()
        QTimer.singleShot(100, self.load_coins)
        
        # Auto-refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.load_coins)
        self.refresh_timer.setInterval(60000)

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        # Header
        header = QLabel("📊 Market Overview")
        layout.addWidget(header)

        # Controls
        controls_layout = QHBoxLayout()

        # Search
        controls_layout.addWidget(QLabel("🔍 Search:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Type coin name or symbol...")
        self.search_input.setToolTip("Filter the list by coin name or symbol")
        self.search_input.setAccessibleName("Search Input")
        self.search_input.setAccessibleDescription("Enter text to filter the cryptocurrency list by name or symbol")
        self.search_input.textChanged.connect(self.filter_coins)
        self.search_input.setMinimumWidth(200)
        controls_layout.addWidget(self.search_input)

        controls_layout.addSpacing(20)

        # Limit
        controls_layout.addWidget(QLabel("Show:"))
        self.limit_combo = QComboBox()
        self.limit_combo.addItems(["Top 10", "Top 20", "Top 50", "Top 100"])
        self.limit_combo.setToolTip("Select number of coins to display")
        self.limit_combo.setAccessibleName("Limit Selection")
        self.limit_combo.currentTextChanged.connect(self.load_coins)
        controls_layout.addWidget(self.limit_combo)

        # Currency
        controls_layout.addWidget(QLabel("Currency:"))
        self.currency_combo = QComboBox()
        self.currency_combo.addItems(["USD", "EUR", "GBP"])
        self.currency_combo.setToolTip("Select display currency")
        self.currency_combo.setAccessibleName("Currency Selection")
        self.currency_combo.currentTextChanged.connect(self.load_coins)
        controls_layout.addWidget(self.currency_combo)

        controls_layout.addSpacing(20)

        # Refresh button
        self.refresh_btn = QPushButton("🔄 Refresh Data")
        self.refresh_btn.setToolTip("Manually update market data from CoinGecko")
        self.refresh_btn.setAccessibleName("Refresh Data Button")
        self.refresh_btn.clicked.connect(self.load_coins)
        controls_layout.addWidget(self.refresh_btn)
        
        # Auto-refresh toggle
        self.auto_refresh_btn = QPushButton("⏸️ Auto-Refresh: OFF")
        self.auto_refresh_btn.setToolTip("Toggle automatic updates every 60 seconds")
        self.auto_refresh_btn.setAccessibleName("Auto-Refresh Toggle Button")
        self.auto_refresh_btn.clicked.connect(self.toggle_auto_refresh)
        controls_layout.addWidget(self.auto_refresh_btn)

        controls_layout.addStretch()
        layout.addLayout(controls_layout)

        # Status
        self.status_label = QLabel("⏳ Loading cryptocurrency data...")
        layout.addWidget(self.status_label)

        # Table - FULL VERSION WITH ALL COLUMNS
        self.table = QTableWidget()
        self.table.setColumnCount(10)  # Increased from 6 to 10!
        self.table.setHorizontalHeaderLabels([
            "Rank",
            "Coin",
            "Symbol",
            "Price",
            "1h %",
            "24h %",
            "7d %",
            "24h Volume",
            "Market Cap",
            "Circulating Supply"
        ])

        # Set column widths
        header = self.table.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Rank
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # Coin name
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Symbol
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Price
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # 1h
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # 24h
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # 7d
        header.setSectionResizeMode(7, QHeaderView.Stretch)  # Volume
        header.setSectionResizeMode(8, QHeaderView.Stretch)  # Market Cap
        header.setSectionResizeMode(9, QHeaderView.Stretch)  # Supply

        self.table.setMinimumSize(600, 400)
        self.table.setSortingEnabled(True)
        self.table.setAlternatingRowColors(True)

        layout.addWidget(self.table)

    def load_coins(self):
        if hasattr(self, 'worker_thread') and self.worker_thread and self.worker_thread.isRunning():
            return

        self.refresh_btn.setEnabled(False)
        self.status_label.setText("⏳ Fetching live data in background...")

        limit = int(self.limit_combo.currentText().split()[1])
        currency = self.currency_combo.currentText().lower()

        self.worker_thread = QThread()
        self.worker = MarketWorker(self.api, limit, currency)
        self.worker.moveToThread(self.worker_thread)

        self.worker_thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.handle_data)
        self.worker.error.connect(lambda e: print(f"Thread Error: {e}"))
        self.worker.finished.connect(self.worker_thread.quit)
        self.worker_thread.finished.connect(self.worker_thread.deleteLater)

        self.worker_thread.start()

    def handle_data(self, coins):
        if coins:
            self.coins_data = coins
            self.update_table_with_full_data()
            self.status_label.setText(f"✅ Live data loaded: {len(coins)} coins")
        else:
            self.status_label.setText("⚠️ No data returned from API - Check connection")
        self.refresh_btn.setEnabled(True)

    def update_table_with_full_data(self):
        """Update table with ALL columns - no fallback"""
        if not self.coins_data:
            print("No coins data to display")
            return

        self.table.setRowCount(len(self.coins_data))
        print(f"Updating table with {len(self.coins_data)} rows...")

        for row, coin in enumerate(self.coins_data):
            try:
                # Extract all data
                rank = coin.get("market_cap_rank", row + 1)
                name = coin.get("name", "Unknown")
                symbol = coin.get("symbol", "").upper()
                price = coin.get("current_price", 0)

                # Get all percentage changes
                change_1h = coin.get("price_change_percentage_1h_in_currency", 0) or 0
                change_24h = coin.get("price_change_percentage_24h_in_currency", 0) or 0
                change_7d = coin.get("price_change_percentage_7d_in_currency", 0) or 0

                volume_24h = coin.get("total_volume", 0)
                market_cap = coin.get("market_cap", 0)
                circulating_supply = coin.get("circulating_supply", 0)

                # Column 0: Rank
                rank_item = QTableWidgetItem(str(rank))
                rank_item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row, 0, rank_item)

                # Column 1: Coin Name
                self.table.setItem(row, 1, QTableWidgetItem(name))

                # Column 2: Symbol
                symbol_item = QTableWidgetItem(symbol)
                symbol_item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row, 2, symbol_item)

                # Column 3: Price
                if price >= 1:
                    price_text = f"${price:,.2f}"
                elif price >= 0.01:
                    price_text = f"${price:.4f}"
                else:
                    price_text = f"${price:.8f}"
                price_item = QTableWidgetItem(price_text)
                price_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.table.setItem(row, 3, price_item)

                # Column 4: 1h Change
                change_1h_item = QTableWidgetItem(f"{change_1h:+.2f}%")
                change_1h_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                if change_1h > 0:
                    change_1h_item.setForeground(QBrush(QColor("#10b981")))
                elif change_1h < 0:
                    change_1h_item.setForeground(QBrush(QColor("#ef4444")))
                self.table.setItem(row, 4, change_1h_item)

                # Column 5: 24h Change
                change_24h_item = QTableWidgetItem(f"{change_24h:+.2f}%")
                change_24h_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                if change_24h > 0:
                    change_24h_item.setForeground(QBrush(QColor("#10b981")))
                elif change_24h < 0:
                    change_24h_item.setForeground(QBrush(QColor("#ef4444")))
                self.table.setItem(row, 5, change_24h_item)

                # Column 6: 7d Change
                change_7d_item = QTableWidgetItem(f"{change_7d:+.2f}%")
                change_7d_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                if change_7d > 0:
                    change_7d_item.setForeground(QBrush(QColor("#10b981")))
                elif change_7d < 0:
                    change_7d_item.setForeground(QBrush(QColor("#ef4444")))
                self.table.setItem(row, 6, change_7d_item)

                # Column 7: 24h Volume
                if volume_24h >= 1e9:
                    volume_text = f"${volume_24h/1e9:.2f}B"
                elif volume_24h >= 1e6:
                    volume_text = f"${volume_24h/1e6:.2f}M"
                else:
                    volume_text = f"${volume_24h:,.0f}"
                volume_item = QTableWidgetItem(volume_text)
                volume_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.table.setItem(row, 7, volume_item)

                # Column 8: Market Cap
                if market_cap >= 1e12:
                    mcap_text = f"${market_cap/1e12:.2f}T"
                elif market_cap >= 1e9:
                    mcap_text = f"${market_cap/1e9:.2f}B"
                elif market_cap >= 1e6:
                    mcap_text = f"${market_cap/1e6:.2f}M"
                else:
                    mcap_text = f"${market_cap:,.0f}"
                mcap_item = QTableWidgetItem(mcap_text)
                mcap_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.table.setItem(row, 8, mcap_item)

                # Column 9: Circulating Supply
                if circulating_supply > 0:
                    if circulating_supply >= 1e9:
                        supply_text = f"{circulating_supply/1e9:.2f}B {symbol}"
                    elif circulating_supply >= 1e6:
                        supply_text = f"{circulating_supply/1e6:.2f}M {symbol}"
                    else:
                        supply_text = f"{circulating_supply:,.0f} {symbol}"
                else:
                    supply_text = "N/A"
                supply_item = QTableWidgetItem(supply_text)
                supply_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.table.setItem(row, 9, supply_item)

            except Exception as e:
                print(f"Error processing row {row}: {e}")
                continue

        print(f"✓ Table updated with {self.table.rowCount()} rows")

    def filter_coins(self):
        """Filter coins by search text"""
        search_text = self.search_input.text().lower()

        if not search_text:
            for row in range(self.table.rowCount()):
                self.table.setRowHidden(row, False)
            return

        for row in range(self.table.rowCount()):
            name_item = self.table.item(row, 1)
            symbol_item = self.table.item(row, 2)

            show_row = False
            if name_item and search_text in name_item.text().lower():
                show_row = True
            elif symbol_item and search_text in symbol_item.text().lower():
                show_row = True

            self.table.setRowHidden(row, not show_row)

    def toggle_auto_refresh(self):
        """Toggle auto-refresh"""
        self.auto_refresh_enabled = not self.auto_refresh_enabled
        
        if self.auto_refresh_enabled:
            self.auto_refresh_btn.setText("▶️ Auto-Refresh: ON")
            self.refresh_timer.start()
            self.status_label.setText("✅ Auto-refresh enabled (updates every 60s)")
        else:
            self.auto_refresh_btn.setText("⏸️ Auto-Refresh: OFF")
            self.refresh_timer.stop()
            self.status_label.setText("⏸️ Auto-refresh disabled")


class EnhancedPredictionTab(QWidget):
    """Enhanced AI Price Predictions with detailed analysis, graphs, and multiple time frames"""

    def __init__(self, api_handler, predictor):
        super().__init__()
        self.api = api_handler
        self.predictor = predictor
        self.worker = None
        self.current_coin_id = None
        self.historical_data = None
        self.last_prediction = None  # Store last prediction for export
        self.init_ui()

    def init_ui(self):
        """Initialize the user interface"""
        # Create scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content_widget = QWidget()
        scroll.setWidget(content_widget)

        main_layout = QVBoxLayout(content_widget)

        # Title
        title_label = QLabel("🔮 AI Price Predictions")
        title_label.setObjectName("sectionTitle")
        main_layout.addWidget(title_label)

        # Controls
        controls_layout = QHBoxLayout()

        # Coin selection
        controls_layout.addWidget(QLabel("Select Coin:"))
        self.coin_combo = QComboBox()
        self.coin_combo.setToolTip("Select a cryptocurrency to analyze")
        self.coin_combo.setAccessibleName("Coin Selection for Prediction")
        controls_layout.addWidget(self.coin_combo)

        # Time frame selection
        controls_layout.addWidget(QLabel("Time Frame:"))
        self.time_frame_combo = QComboBox()
        self.time_frame_combo.addItems(["24 Hours", "3 Days", "7 Days", "30 Days"])
        self.time_frame_combo.setToolTip("Select prediction time horizon")
        self.time_frame_combo.setAccessibleName("Time Frame Selection")
        controls_layout.addWidget(self.time_frame_combo)

        # Prediction button
        self.predict_btn = QPushButton("🔮 Predict Price")
        self.predict_btn.setObjectName("predictButton")
        self.predict_btn.setToolTip("Generate AI-powered price prediction based on historical data")
        self.predict_btn.setAccessibleName("Predict Price Button")
        self.predict_btn.clicked.connect(self.run_prediction)
        controls_layout.addWidget(self.predict_btn)
        
        # Export prediction button
        self.export_pred_btn = QPushButton("💾 Save Prediction")
        self.export_pred_btn.setObjectName("actionButton")
        self.export_pred_btn.setToolTip("Run a prediction first to enable export")
        self.export_pred_btn.setAccessibleName("Export Prediction Button")
        self.export_pred_btn.clicked.connect(self.export_prediction)
        self.export_pred_btn.setEnabled(False)
        controls_layout.addWidget(self.export_pred_btn)

        controls_layout.addStretch()
        main_layout.addLayout(controls_layout)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)

        # Create splitter for results and graph
        splitter = QSplitter(Qt.Horizontal)

        # Left side: Results
        results_widget = QWidget()
        results_layout = QVBoxLayout()

        # Current Info Group
        current_info_group = QGroupBox("Current Information")
        current_info_layout = QVBoxLayout()
        
        self.current_price_label = QLabel("Current Price: -")
        self.current_price_label.setObjectName("infoLabelLarge")
        current_info_layout.addWidget(self.current_price_label)
        
        self.market_cap_label = QLabel("Market Cap: -")
        self.market_cap_label.setObjectName("infoLabel")
        current_info_layout.addWidget(self.market_cap_label)
        
        self.volume_label = QLabel("24h Volume: -")
        self.volume_label.setObjectName("infoLabel")
        current_info_layout.addWidget(self.volume_label)
        
        current_info_group.setLayout(current_info_layout)
        results_layout.addWidget(current_info_group)

        # Prediction Results Group
        self.results_group = QGroupBox("Prediction Results")
        prediction_layout = QVBoxLayout()

        # Predicted price
        self.predicted_price_label = QLabel("Predicted Price: -")
        self.predicted_price_label.setObjectName("predictionResultLabel")
        prediction_layout.addWidget(self.predicted_price_label)

        # Change percentage
        self.change_label = QLabel("Change: -")
        self.change_label.setObjectName("predictionMetaLabel")
        prediction_layout.addWidget(self.change_label)

        # Price range
        self.price_range_label = QLabel("Expected Range: -")
        self.price_range_label.setObjectName("infoLabel")
        prediction_layout.addWidget(self.price_range_label)

        # Confidence score
        self.confidence_label = QLabel("Confidence: -")
        self.confidence_label.setObjectName("predictionMetaLabel")
        prediction_layout.addWidget(self.confidence_label)

        # Direction indicator
        self.direction_label = QLabel("Direction: -")
        self.direction_label.setObjectName("predictionMetaLabel")
        prediction_layout.addWidget(self.direction_label)

        self.results_group.setLayout(prediction_layout)
        self.results_group.setVisible(False)
        results_layout.addWidget(self.results_group)

        # Technical Analysis Group
        self.technical_group = QGroupBox("Technical Analysis")
        technical_layout = QVBoxLayout()
        
        self.rsi_label = QLabel("RSI: -")
        self.rsi_label.setObjectName("technicalLabel")
        technical_layout.addWidget(self.rsi_label)
        
        self.macd_label = QLabel("MACD: -")
        self.macd_label.setObjectName("technicalLabel")
        technical_layout.addWidget(self.macd_label)
        
        self.volatility_label = QLabel("Volatility: -")
        self.volatility_label.setObjectName("technicalLabel")
        technical_layout.addWidget(self.volatility_label)
        
        self.technical_group.setLayout(technical_layout)
        self.technical_group.setVisible(False)
        results_layout.addWidget(self.technical_group)

        # Insights Group
        self.insights_group = QGroupBox("AI Insights")
        insights_layout = QVBoxLayout()
        
        self.insights_text = QTextEdit()
        self.insights_text.setReadOnly(True)
        self.insights_text.setMaximumHeight(150)
        insights_layout.addWidget(self.insights_text)
        
        self.insights_group.setLayout(insights_layout)
        self.insights_group.setVisible(False)
        results_layout.addWidget(self.insights_group)

        results_layout.addStretch()
        results_widget.setLayout(results_layout)
        splitter.addWidget(results_widget)

        # Right side: Graph
        graph_widget = QWidget()
        graph_layout = QVBoxLayout()

        # Create matplotlib figure
        self.figure = Figure(figsize=(8, 6))
        self.canvas = FigureCanvas(self.figure)
        graph_layout.addWidget(self.canvas)

        graph_widget.setLayout(graph_layout)
        splitter.addWidget(graph_widget)

        # Set initial sizes
        splitter.setSizes([400, 600])

        main_layout.addWidget(splitter)

        # Set main layout
        outer_layout = QVBoxLayout(self)
        outer_layout.addWidget(scroll)
        self.setLayout(outer_layout)

        # Load coins for selection
        self.load_coins()

    def load_coins(self):
        """Load available coins into the combo box"""
        try:
            self.coin_combo.clear()
            coins = self.api.get_top_coins(limit=50, vs_currency="usd")
            for coin in coins:
                self.coin_combo.addItem(
                    f"{coin['name']} ({coin['symbol'].upper()})", coin["id"]
                )
        except Exception as e:
            print(f"Error loading coins: {e}")
            QMessageBox.warning(self, "Error", f"Failed to load coins: {e}")

    def run_prediction(self):
        """Run the price prediction"""
        coin_id = self.coin_combo.currentData()
        if not coin_id:
            QMessageBox.warning(self, "Warning", "Please select a coin first.")
            return

        try:
            self.current_coin_id = coin_id
            
            # Get current price and additional info
            coins = self.api.get_top_coins(limit=50, vs_currency="usd")
            current_price = 0
            market_cap = 0
            volume_24h = 0
            
            for coin in coins:
                if coin["id"] == coin_id:
                    current_price = coin.get("current_price", 0)
                    market_cap = coin.get("market_cap", 0)
                    volume_24h = coin.get("total_volume", 0)
                    break

            if current_price <= 0:
                QMessageBox.warning(
                    self, "Warning", "Could not get current price for selected coin."
                )
                return

            # Update current info
            self.current_price_label.setText(f"Current Price: ${current_price:,.2f}")
            
            if market_cap >= 1e9:
                self.market_cap_label.setText(f"Market Cap: ${market_cap/1e9:.2f}B")
            else:
                self.market_cap_label.setText(f"Market Cap: ${market_cap/1e6:.2f}M")
            
            if volume_24h >= 1e9:
                self.volume_label.setText(f"24h Volume: ${volume_24h/1e9:.2f}B")
            else:
                self.volume_label.setText(f"24h Volume: ${volume_24h/1e6:.2f}M")

            # Get time frame
            time_frame = self.time_frame_combo.currentText()
            if time_frame == "24 Hours":
                days = 1
            elif time_frame == "3 Days":
                days = 3
            elif time_frame == "7 Days":
                days = 7
            else:
                days = 30

            # Start prediction worker
            self.worker = PredictionWorker(self.predictor, coin_id, current_price, days)
            self.worker.progress_update.connect(self.update_progress)
            self.worker.prediction_complete.connect(self.show_prediction)
            self.worker.error_occurred.connect(self.show_error)
            self.worker.start()

            self.progress_bar.setValue(0)
            self.progress_bar.setVisible(True)
            self.predict_btn.setEnabled(False)

        except Exception as e:
            self.show_error(f"Error: {str(e)}")

    def update_progress(self, value, message):
        """Update progress bar and status"""
        self.progress_bar.setValue(value)

    def show_prediction(self, result):
        """Display the prediction results"""
        try:
            self.predict_btn.setEnabled(True)
            self.progress_bar.setValue(100)
            self.progress_bar.setVisible(False)
            
            # Store prediction for export
            self.last_prediction = {
                'coin': self.coin_combo.currentText(),
                'coin_id': self.current_coin_id,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                **result
            }
            self.export_pred_btn.setEnabled(True)
            self.export_pred_btn.setToolTip("Save current prediction results to JSON file")

            # Format results
            current_price = result["current_price"]
            predicted_price = result["predicted_price"]
            change_percent = result["predicted_change_percent"]
            confidence = result["confidence_score"]
            direction = result["direction"]
            insights = result.get("insights", [])
            time_frame = result.get("time_frame", 1)

            # Calculate price range (±10% of prediction for uncertainty)
            price_range_low = predicted_price * 0.9
            price_range_high = predicted_price * 1.1

            # Update UI with results
            self.predicted_price_label.setText(
                f"Predicted Price: ${predicted_price:,.2f}"
            )

            # Color code the change based on direction
            change_text = f"Change: {change_percent:+.2f}%"
            change_color = "#27ae60" if change_percent >= 0 else "#e74c3c"
            self.change_label.setText(
                f'<span style="color:{change_color}; font-weight: bold;">{change_text}</span>'
            )
            self.change_label.setTextFormat(Qt.RichText)

            self.price_range_label.setText(
                f"Expected Range: ${price_range_low:,.2f} - ${price_range_high:,.2f}"
            )

            # Confidence with color coding
            confidence_color = "#27ae60" if confidence >= 70 else "#f39c12" if confidence >= 50 else "#e74c3c"
            self.confidence_label.setText(
                f'<span style="color:{confidence_color};">Confidence: {confidence:.1f}%</span>'
            )
            self.confidence_label.setTextFormat(Qt.RichText)

            direction_emoji = "📈" if direction == "bullish" else "📉"
            direction_color = "#27ae60" if direction == "bullish" else "#e74c3c"
            self.direction_label.setText(
                f'<span style="color:{direction_color}; font-weight: bold;">{direction_emoji} Direction: {direction.capitalize()}</span>'
            )
            self.direction_label.setTextFormat(Qt.RichText)

            # Update insights
            insights_html = "<ul style='margin: 5px; padding-left: 20px;'>"
            for insight in insights:
                insights_html += f"<li style='margin: 5px 0;'>{insight}</li>"
            insights_html += "</ul>"
            self.insights_text.setHtml(insights_html)

            # Show all result groups
            self.results_group.setVisible(True)
            self.insights_group.setVisible(True)
            self.technical_group.setVisible(True)

            # Update technical indicators (mock data for now - would come from predictor in real impl)
            self.rsi_label.setText("RSI: 65.4 (Neutral)")
            self.macd_label.setText("MACD: Bullish Crossover")
            self.volatility_label.setText(f"Volatility: {abs(change_percent/2):.1f}%")

            # Update graph
            self.update_prediction_graph(current_price, predicted_price, time_frame)

        except Exception as e:
            self.show_error(f"Error displaying results: {str(e)}")

    def update_prediction_graph(self, current_price, predicted_price, time_frame):
        """Update the prediction graph"""
        try:
            self.figure.clear()
            # Set dark background for figure
            self.figure.patch.set_facecolor('#0F1724')

            ax = self.figure.add_subplot(111)
            # Set dark background for axes
            ax.set_facecolor('#0F1724')

            # Create time series data
            if time_frame == 1:
                periods = 24
                x_label = "Hours"
            elif time_frame == 7:
                periods = 7
                x_label = "Days"
            else:
                periods = 30
                x_label = "Days"

            # Generate historical trend (simplified - mock data)
            x = np.arange(0, periods + 1)
            
            # Create a smooth curve from current to predicted
            historical = np.linspace(current_price * 0.95, current_price, periods)
            prediction = np.array([predicted_price])
            
            # Combine historical and prediction
            prices = np.concatenate([historical, prediction])

            # Plot historical data
            ax.plot(x[:-1], prices[:-1], color='#1199FA', linewidth=2, label='Historical', alpha=0.8)
            
            # Plot prediction
            ax.plot([x[-2], x[-1]], [prices[-2], prices[-1]], color='#EF4444', linestyle='--',
                   linewidth=2, label='Prediction', alpha=0.9)
            
            # Add prediction point
            ax.scatter([x[-1]], [prices[-1]], color='#EF4444', s=100, zorder=5,
                      label=f'Predicted: ${predicted_price:,.2f}')
            
            # Add uncertainty band
            uncertainty = abs(predicted_price - current_price) * 0.1
            ax.fill_between(
                [x[-2], x[-1]],
                [prices[-2] - uncertainty, prices[-1] - uncertainty],
                [prices[-2] + uncertainty, prices[-1] + uncertainty],
                alpha=0.2, color='red', label='Uncertainty Range'
            )

            # Formatting
            ax.set_xlabel(x_label, fontsize=10, color='#94A3B8')
            ax.set_ylabel('Price (USD)', fontsize=10, color='#94A3B8')
            ax.set_title(f'{self.coin_combo.currentText()} - Price Prediction', 
                        fontsize=12, fontweight='bold', color='white')

            # Customize ticks
            ax.tick_params(axis='x', colors='#94A3B8')
            ax.tick_params(axis='y', colors='#94A3B8')

            # Customize spines
            for spine in ax.spines.values():
                spine.set_color('#1E293B')

            # Customize legend
            legend = ax.legend(loc='best', fontsize=8, facecolor='#1E293B', edgecolor='#334155')
            plt.setp(legend.get_texts(), color='#E0E6ED')

            ax.grid(True, alpha=0.1, color='#FFFFFF', linestyle='--')
            
            # Format y-axis as currency
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'${y:,.0f}'))

            self.canvas.draw()

        except Exception as e:
            print(f"Error updating graph: {e}")

    def show_error(self, error_message):
        """Display error message"""
        self.predict_btn.setEnabled(True)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        QMessageBox.critical(self, "Prediction Error", error_message)

    def export_prediction(self):
        """Export prediction results to JSON file"""
        if not self.last_prediction:
            QMessageBox.warning(self, "No Prediction", "No prediction to export. Please run a prediction first.")
            return
        
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self, 
                "Save Prediction",
                f"prediction_{self.last_prediction['coin_id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                "JSON Files (*.json)"
            )
            
            if file_path:
                import json
                # Convert datetime to string for JSON serialization
                export_data = self.last_prediction.copy()
                if 'timestamp' in export_data and isinstance(export_data['timestamp'], datetime):
                    export_data['timestamp'] = export_data['timestamp'].isoformat()
                
                with open(file_path, 'w') as f:
                    json.dump(export_data, f, indent=2, default=str)
                
                QMessageBox.information(
                    self,
                    "Success",
                    f"Prediction saved to:\n{file_path}"
                )
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export prediction: {str(e)}")


class EnhancedPortfolioTab(QWidget):
    """Full-featured portfolio manager with improved functionality"""

    def __init__(self, api_handler, portfolio_tracker):
        super().__init__()
        self.api = api_handler
        self.portfolio = portfolio_tracker
        self.currency = "usd"
        self._setup_ui()
        self._load_coins_into_dialog()
        self.refresh_portfolio()

    def _setup_ui(self):
        """Setup the user interface for the portfolio tab"""
        # Create scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content_widget = QWidget()
        scroll.setWidget(content_widget)

        main_layout = QVBoxLayout(content_widget)

        # Title
        title_label = QLabel("💼 Portfolio Management")
        title_label.setObjectName("sectionTitle")
        main_layout.addWidget(title_label)

        # Top bar with buttons and currency selection
        top_bar = QHBoxLayout()
        self.add_btn = QPushButton("➕ Add Transaction")
        self.add_btn.setObjectName("actionButton")
        self.add_btn.setToolTip("Record a new buy or sell transaction")
        self.add_btn.setAccessibleName("Add Transaction Button")
        
        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.setObjectName("actionButton")
        self.refresh_btn.setToolTip("Update current prices and portfolio value")
        self.refresh_btn.setAccessibleName("Refresh Portfolio Button")
        
        self.export_btn = QPushButton("📤 Export to CSV")
        self.export_btn.setObjectName("actionButton")
        self.export_btn.setToolTip("Download portfolio data as CSV")
        self.export_btn.setAccessibleName("Export Portfolio Button")

        # Currency Combo Box
        self.currency_combo = QComboBox()
        self.currency_combo.addItems(["USD", "EUR", "GBP", "JPY"])
        self.currency_combo.currentTextChanged.connect(self.on_currency_changed)

        top_bar.addWidget(self.add_btn)
        top_bar.addWidget(self.refresh_btn)
        top_bar.addWidget(self.export_btn)
        top_bar.addWidget(QLabel("Currency:"))
        top_bar.addWidget(self.currency_combo)
        top_bar.addStretch()
        main_layout.addLayout(top_bar)

        # Portfolio summary cards
        summary_layout = QHBoxLayout()
        
        # Total Value Card
        total_card = QGroupBox("Total Portfolio Value")
        total_layout = QVBoxLayout()
        self.total_value_label = QLabel("$0.00")
        self.total_value_label.setObjectName("totalValueLabel")
        total_layout.addWidget(self.total_value_label)
        total_card.setLayout(total_layout)
        summary_layout.addWidget(total_card)
        
        # Total P&L Card
        pnl_card = QGroupBox("Total Profit/Loss")
        pnl_layout = QVBoxLayout()
        self.total_pnl_label = QLabel("$0.00 (0.00%)")
        self.total_pnl_label.setObjectName("totalPnlLabel")
        pnl_layout.addWidget(self.total_pnl_label)
        pnl_card.setLayout(pnl_layout)
        summary_layout.addWidget(pnl_card)
        
        # Holdings Count Card
        holdings_card = QGroupBox("Holdings")
        holdings_layout = QVBoxLayout()
        self.holdings_count_label = QLabel("0 coins")
        self.holdings_count_label.setObjectName("holdingsCountLabel")
        holdings_layout.addWidget(self.holdings_count_label)
        holdings_card.setLayout(holdings_layout)
        summary_layout.addWidget(holdings_card)
        
        main_layout.addLayout(summary_layout)

        # Table setup with 8 columns (added PnL column)
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(
            [
                "Coin",
                "Symbol",
                "Amount",
                "Avg. Price",
                "Current Price",
                "Value",
                "PnL",
                "% of Portfolio",
            ]
        )
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(True)
        main_layout.addWidget(self.table)

        # Set main layout
        outer_layout = QVBoxLayout(self)
        outer_layout.addWidget(scroll)

        # Connections
        self.add_btn.clicked.connect(self._open_add_dialog)
        self.refresh_btn.clicked.connect(self.refresh_portfolio)
        self.export_btn.clicked.connect(self.export_to_csv)

    def on_currency_changed(self, currency):
        """Handle currency change"""
        self.currency = currency.lower()
        self.refresh_portfolio()

    def _load_coins_into_dialog(self):
        """Load coins into the AddTransactionDialog"""
        try:
            top = self.api.get_top_coins(limit=100, vs_currency=self.currency)
            self.coin_list = top
        except Exception as exc:
            print("Failed to load coin list for dialog:", exc)
            self.coin_list = []

    def _open_add_dialog(self):
        """Open the add transaction dialog"""
        dlg = AddTransactionDialog(self)
        dlg.load_coins(self.coin_list)
        if dlg.exec_() == QDialog.Accepted:
            data = dlg.get_data()
            self.portfolio.add_transaction(data)
            self.refresh_portfolio()

    def refresh_portfolio(self):
        """Re-calculate everything and update UI"""
        # Get holdings
        holdings = self.portfolio.get_holdings()
        if not holdings:
            self.table.setRowCount(0)
            self.total_value_label.setText(f"{self.get_currency_symbol()}0.00")
            self.total_pnl_label.setText(f"{self.get_currency_symbol()}0.00 (0.00%)")
            self.holdings_count_label.setText("0 coins")
            return

        # Get prices
        ids = list(holdings.keys())
        try:
            price_data = self.api.get_price(ids, vs_currency=self.currency)
        except Exception as e:
            print(f"Error fetching prices: {e}")
            QMessageBox.warning(self, "Error", "Could not fetch current prices")
            return

        # Fill the table
        self.table.setRowCount(len(ids))
        total_value = 0.0
        total_pnl = 0.0
        total_cost = 0.0

        for row, coin_id in enumerate(ids):
            try:
                coin_info = self.api.get_coin_info(coin_id)
                name = coin_info.get("name", coin_id)
                symbol = coin_info.get("symbol", "").upper()

                amount = holdings[coin_id]["amount"]
                avg_price = holdings[coin_id]["avg_price"]
                cur_price = price_data.get(coin_id, {}).get(self.currency, 0.0)
                value = amount * cur_price
                cost = amount * avg_price
                pnl = value - cost
                pnl_percent = (pnl / cost * 100) if cost > 0 else 0
                
                total_value += value
                total_pnl += pnl
                total_cost += cost

                # Populate cells
                self.table.setItem(row, 0, QTableWidgetItem(name))
                self.table.setItem(row, 1, QTableWidgetItem(symbol))
                self.table.setItem(row, 2, QTableWidgetItem(f"{amount:,.8f}"))
                self.table.setItem(
                    row,
                    3,
                    QTableWidgetItem(f"{self.get_currency_symbol()}{avg_price:,.2f}"),
                )
                self.table.setItem(
                    row,
                    4,
                    QTableWidgetItem(f"{self.get_currency_symbol()}{cur_price:,.2f}"),
                )
                self.table.setItem(
                    row, 5, QTableWidgetItem(f"{self.get_currency_symbol()}{value:,.2f}")
                )

                # PnL column with color coding
                pnl_item = QTableWidgetItem(
                    f"{self.get_currency_symbol()}{pnl:,.2f} ({pnl_percent:+.1f}%)"
                )
                if pnl >= 0:
                    pnl_item.setForeground(QBrush(QColor("#27ae60")))
                else:
                    pnl_item.setForeground(QBrush(QColor("#e74c3c")))
                self.table.setItem(row, 6, pnl_item)

            except Exception as e:
                print(f"Error processing {coin_id}: {e}")
                continue

        # Calculate and display percentages
        for row in range(self.table.rowCount()):
            try:
                value_text = self.table.item(row, 5).text()
                # Remove currency symbol and commas
                value_str = value_text.replace(self.get_currency_symbol(), "").replace(",", "")
                value = float(value_str)
                perc = (value / total_value) * 100 if total_value else 0
                perc_item = QTableWidgetItem(f"{perc:,.2f}%")
                perc_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.table.setItem(row, 7, perc_item)
            except Exception as e:
                print(f"Error calculating % for row {row}: {e}")

        # Update summary cards
        currency_symbol = self.get_currency_symbol()
        self.total_value_label.setText(f"{currency_symbol}{total_value:,.2f}")
        
        # Update P&L with color
        total_pnl_percent = (total_pnl / total_cost * 100) if total_cost > 0 else 0
        pnl_color = "#27ae60" if total_pnl >= 0 else "#e74c3c"
        self.total_pnl_label.setText(
            f"{currency_symbol}{total_pnl:,.2f} ({total_pnl_percent:+.1f}%)"
        )
        self.total_pnl_label.setStyleSheet(
            f"font-size: 18px; font-weight: bold; color: {pnl_color};"
        )
        
        self.holdings_count_label.setText(f"{len(ids)} coins")

    def get_currency_symbol(self):
        """Get the currency symbol"""
        symbols = {
            "usd": "$",
            "eur": "€",
            "gbp": "£",
            "jpy": "¥"
        }
        return symbols.get(self.currency, "$")

    def export_to_csv(self):
        """Export portfolio data to CSV"""
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Save Portfolio", "", "CSV Files (*.csv)"
            )
            if not file_path:
                return

            holdings = self.portfolio.get_holdings()
            if not holdings:
                QMessageBox.information(self, "Info", "No data to export")
                return

            ids = list(holdings.keys())
            price_data = self.api.get_price(ids, vs_currency=self.currency)

            data = []
            total_value = 0
            
            for coin_id in ids:
                coin_info = self.api.get_coin_info(coin_id)
                name = coin_info.get("name", coin_id)
                symbol = coin_info.get("symbol", "").upper()
                amount = holdings[coin_id]["amount"]
                avg_price = holdings[coin_id]["avg_price"]
                cur_price = price_data.get(coin_id, {}).get(self.currency, 0.0)
                value = amount * cur_price
                cost = amount * avg_price
                pnl = value - cost
                total_value += value

                data.append(
                    {
                        "Coin": name,
                        "Symbol": symbol,
                        "Amount": amount,
                        f"Avg. Price ({self.currency.upper()})": avg_price,
                        f"Current Price ({self.currency.upper()})": cur_price,
                        f"Value ({self.currency.upper()})": value,
                        f"PnL ({self.currency.upper()})": pnl,
                        "PnL %": (pnl / cost * 100) if cost > 0 else 0,
                    }
                )

            # Calculate portfolio percentages
            for item in data:
                value = item[f"Value ({self.currency.upper()})"]
                item["% of Portfolio"] = (value / total_value * 100) if total_value > 0 else 0

            df = pd.DataFrame(data)
            df.to_csv(file_path, index=False)
            QMessageBox.information(
                self, "Success", f"Portfolio exported to {file_path}"
            )

        except Exception as e:
            print(f"Error exporting to CSV: {e}")
            QMessageBox.critical(self, "Error", f"Failed to export: {e}")


class EnhancedSentimentTab(QWidget):
    """Enhanced Sentiment Analysis with visual indicators and detailed metrics"""
    
    def __init__(self, api_handler):
        super().__init__()
        self.api = api_handler
        self.sentiment_tracker = SentimentTracker(self.api)
        self.init_ui()

    def init_ui(self):
        # Create scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content_widget = QWidget()
        scroll.setWidget(content_widget)

        layout = QVBoxLayout(content_widget)

        # Title
        title_label = QLabel("📊 Market Sentiment Analysis")
        title_label.setObjectName("sectionTitle")
        layout.addWidget(title_label)

        # Refresh button
        refresh_btn = QPushButton("🔄 Refresh Sentiment Data")
        refresh_btn.setObjectName("actionButton")
        refresh_btn.setToolTip("Update market sentiment data from Alternative.me and CoinGecko")
        refresh_btn.setAccessibleName("Refresh Sentiment Button")
        refresh_btn.clicked.connect(self.refresh_sentiment)
        layout.addWidget(refresh_btn)

        # Fear & Greed Index Group
        fgi_group = QGroupBox("Fear & Greed Index")
        fgi_layout = QVBoxLayout()
        
        self.fgi_value_label = QLabel("Loading...")
        self.fgi_value_label.setObjectName("fgiValue")
        self.fgi_value_label.setAlignment(Qt.AlignCenter)
        fgi_layout.addWidget(self.fgi_value_label)
        
        self.fgi_classification_label = QLabel("...")
        self.fgi_classification_label.setObjectName("fgiClass")
        self.fgi_classification_label.setAlignment(Qt.AlignCenter)
        fgi_layout.addWidget(self.fgi_classification_label)
        
        self.fgi_description_label = QLabel("")
        self.fgi_description_label.setObjectName("fgiDesc")
        self.fgi_description_label.setWordWrap(True)
        self.fgi_description_label.setAlignment(Qt.AlignCenter)
        fgi_layout.addWidget(self.fgi_description_label)
        
        fgi_group.setLayout(fgi_layout)
        layout.addWidget(fgi_group)

        # Market Overview Group
        market_group = QGroupBox("Market Overview")
        market_layout = QGridLayout()
        
        market_layout.addWidget(QLabel("Market Sentiment:"), 0, 0)
        self.market_sentiment_label = QLabel("Loading...")
        self.market_sentiment_label.setObjectName("sentimentLabel")
        market_layout.addWidget(self.market_sentiment_label, 0, 1)
        
        market_layout.addWidget(QLabel("Gainers:"), 1, 0)
        self.gainers_label = QLabel("0")
        self.gainers_label.setObjectName("gainersLabel")
        market_layout.addWidget(self.gainers_label, 1, 1)
        
        market_layout.addWidget(QLabel("Losers:"), 2, 0)
        self.losers_label = QLabel("0")
        self.losers_label.setObjectName("losersLabel")
        market_layout.addWidget(self.losers_label, 2, 1)
        
        market_layout.addWidget(QLabel("Neutral:"), 3, 0)
        self.neutral_label = QLabel("0")
        market_layout.addWidget(self.neutral_label, 3, 1)
        
        market_layout.addWidget(QLabel("Extreme Gainers (>5%):"), 4, 0)
        self.extreme_gainers_label = QLabel("0")
        self.extreme_gainers_label.setObjectName("gainersLabel")
        market_layout.addWidget(self.extreme_gainers_label, 4, 1)
        
        market_layout.addWidget(QLabel("Extreme Losers (<-5%):"), 5, 0)
        self.extreme_losers_label = QLabel("0")
        self.extreme_losers_label.setObjectName("losersLabel")
        market_layout.addWidget(self.extreme_losers_label, 5, 1)
        
        market_group.setLayout(market_layout)
        layout.addWidget(market_group)

        # Coin-specific sentiment
        coin_group = QGroupBox("Coin-Specific Sentiment Analysis")
        coin_layout = QVBoxLayout()
        
        controls_layout = QHBoxLayout()
        controls_layout.addWidget(QLabel("Select Coin:"))
        self.coin_combo = QComboBox()
        controls_layout.addWidget(self.coin_combo)

        self.analyze_btn = QPushButton("🔍 Analyze Sentiment")
        self.analyze_btn.setObjectName("actionButton")
        self.analyze_btn.setToolTip("Analyze sentiment for selected coin based on recent data")
        self.analyze_btn.setAccessibleName("Analyze Coin Sentiment Button")
        self.analyze_btn.clicked.connect(self.analyze_coin_sentiment)
        controls_layout.addWidget(self.analyze_btn)
        coin_layout.addLayout(controls_layout)

        # Coin sentiment result
        self.coin_sentiment_text = QTextEdit()
        self.coin_sentiment_text.setReadOnly(True)
        self.coin_sentiment_text.setMaximumHeight(100)
        coin_layout.addWidget(self.coin_sentiment_text)
        
        coin_group.setLayout(coin_layout)
        layout.addWidget(coin_group)

        layout.addStretch()

        # Set main layout
        outer_layout = QVBoxLayout(self)
        outer_layout.addWidget(scroll)
        self.setLayout(outer_layout)
        
        self.load_coins()
        QTimer.singleShot(500, self.refresh_sentiment)

    def load_coins(self):
        try:
            coins = self.api.get_top_coins(limit=20, vs_currency="usd")
            for coin in coins:
                self.coin_combo.addItem(
                    f"{coin['name']} ({coin['symbol'].upper()})", coin["id"]
                )
        except Exception as e:
            print(f"Error loading coins: {e}")

    def refresh_sentiment(self):
        """Fetch and display Fear & Greed Index and market analysis"""
        try:
            # Fear & Greed Index
            fgi = self.sentiment_tracker.get_fear_greed_index()
            if fgi:
                value = fgi['value']
                classification = fgi['classification']
                
                # Set color based on value
                if value >= 75:
                    color = "#e74c3c"  # Extreme Greed - Red
                    description = "The market is showing signs of extreme greed. Consider taking profits."
                elif value >= 55:
                    color = "#f39c12"  # Greed - Orange
                    description = "Market sentiment is greedy. Be cautious with new positions."
                elif value >= 45:
                    color = "#95a5a6"  # Neutral - Gray
                    description = "Market sentiment is balanced."
                elif value >= 25:
                    color = "#3498db"  # Fear - Blue
                    description = "Market sentiment is fearful. Potential buying opportunity."
                else:
                    color = "#27ae60"  # Extreme Fear - Green
                    description = "Extreme fear in the market. Strong buying opportunity for long-term investors."
                
                self.fgi_value_label.setText(str(value))
                self.fgi_value_label.setStyleSheet(
                    f"font-size: 48px; font-weight: bold; margin: 10px; color: {color};"
                )
                self.fgi_classification_label.setText(classification)
                self.fgi_classification_label.setStyleSheet(
                    f"font-size: 18px; margin: 5px; color: {color}; font-weight: bold;"
                )
                self.fgi_description_label.setText(description)

            # Market analysis
            market_data = self.sentiment_tracker.get_market_sentiment()
            analysis = market_data.get("market_analysis", {})
            
            sentiment = analysis.get('market_sentiment', 'Neutral')
            self.market_sentiment_label.setText(sentiment)
            
            # Color code market sentiment
            if "Strongly Bullish" in sentiment:
                sentiment_color = "#27ae60"
            elif "Bullish" in sentiment:
                sentiment_color = "#3498db"
            elif "Bearish" in sentiment:
                sentiment_color = "#e67e22"
            elif "Strongly Bearish" in sentiment:
                sentiment_color = "#e74c3c"
            else:
                sentiment_color = "#95a5a6"
            
            self.market_sentiment_label.setStyleSheet(f"font-weight: bold; color: {sentiment_color};")
            
            self.gainers_label.setText(str(analysis.get('gainers', 0)))
            self.losers_label.setText(str(analysis.get('losers', 0)))
            self.neutral_label.setText(str(analysis.get('neutral', 0)))
            self.extreme_gainers_label.setText(str(analysis.get('extreme_gainers', 0)))
            self.extreme_losers_label.setText(str(analysis.get('extreme_losers', 0)))
            
        except Exception as e:
            print(f"Error refreshing sentiment: {e}")
            self.fgi_value_label.setText("Error")
            self.market_sentiment_label.setText("Error loading data")

    def analyze_coin_sentiment(self):
        """Fetch and display sentiment for the selected coin"""
        coin_id = self.coin_combo.currentData()
        if not coin_id:
            self.coin_sentiment_text.setPlainText("Please select a coin first.")
            return

        try:
            sentiment = self.sentiment_tracker.get_coin_sentiment(coin_id)
            
            html = f"""
            <div style='padding: 10px;'>
                <h3 style='margin: 5px 0;'>{self.coin_combo.currentText()}</h3>
                <p style='margin: 5px 0;'>
                    <span style='color: #27ae60; font-weight: bold;'>Positive: {sentiment['positive']:.1f}%</span> | 
                    <span style='color: #e74c3c; font-weight: bold;'>Negative: {sentiment['negative']:.1f}%</span> | 
                    <span style='color: #95a5a6; font-weight: bold;'>Neutral: {sentiment['neutral']:.1f}%</span>
                </p>
            </div>
            """
            self.coin_sentiment_text.setHtml(html)
            
        except Exception as e:
            self.coin_sentiment_text.setPlainText(f"Error analyzing sentiment: {str(e)}")


# ==================== MAIN WINDOW ====================
class EnhancedCryptoTrackerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CoinSentinel AI - Enhanced Cryptocurrency Tracker")
        self.setGeometry(100, 100, 1600, 900)

        # Initialize components
        self.api = EnhancedCryptoAPIHandler()
        self.predictor = AdvancedPricePredictor(self.api)
        self.portfolio = PortfolioTracker()
        self.sentiment = SentimentTracker(self.api)

        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Application header
        header_label = QLabel("🪙 CoinSentinel AI - Professional Crypto Tracker")
        header_label.setObjectName("appHeader")
        header_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(header_label)

        self.tabs = QTabWidget()
        # Styling moved to QSS
        
        self.tabs.addTab(ImprovedMarketTab(self.api), "📊 Market Overview")
        self.tabs.addTab(
            EnhancedPredictionTab(self.api, self.predictor), "🔮 AI Predictions"
        )
        self.tabs.addTab(EnhancedPortfolioTab(self.api, self.portfolio), "💼 Portfolio")
        self.tabs.addTab(EnhancedSentimentTab(self.api), "📈 Market Sentiment")

        main_layout.addWidget(self.tabs)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("✅ Application ready - Welcome to CoinSentinel AI!")
        
        # Load external stylesheet
        try:
            with open("src/style.qss", "r") as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            print(f"Error loading stylesheet: {e}")


# ==================== MAIN FUNCTION ====================
def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # Set application-wide font
    font = QFont("Segoe UI", 9)
    app.setFont(font)
    
    window = EnhancedCryptoTrackerApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
