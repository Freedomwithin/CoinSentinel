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
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
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
        layout.addWidget(self.coin_combo, 0, 1)
        layout.addWidget(QLabel("Type:"), 1, 0)
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Buy", "Sell"])
        layout.addWidget(self.type_combo, 1, 1)
        layout.addWidget(QLabel("Amount:"), 2, 0)
        self.amount_input = QDoubleSpinBox()
        self.amount_input.setRange(0.00000001, 1000000)
        self.amount_input.setDecimals(8)
        layout.addWidget(self.amount_input, 2, 1)
        layout.addWidget(QLabel("Price per Coin:"), 3, 0)
        self.price_input = QDoubleSpinBox()
        self.price_input.setRange(0.00000001, 1000000)
        self.price_input.setDecimals(4)
        self.price_input.setPrefix("$")
        layout.addWidget(self.price_input, 3, 1)
        layout.addWidget(QLabel("Date:"), 4, 0)
        self.date_input = QLineEdit(datetime.now().strftime("%Y-%m-%d"))
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
    """Enhanced market overview with fallback to sample data"""

    def __init__(self, api_handler):
        super().__init__()
        self.api = api_handler
        self.coins_data = []
        self.init_ui()
        QTimer.singleShot(100, self.load_coins)

    def init_ui(self):
        layout = QVBoxLayout()

        # Title
        title_label = QLabel("📊 Market Overview - Cryptocurrency Dashboard")
        title_label.setStyleSheet(
            "font-size: 18px; font-weight: bold; margin: 10px; color: #2c3e50;"
        )
        layout.addWidget(title_label)

        # Search and controls
        controls_layout = QHBoxLayout()
        controls_layout.addWidget(QLabel("🔍 Search:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Type coin name or symbol...")
        self.search_input.textChanged.connect(self.filter_coins)
        self.search_input.setMinimumWidth(200)
        controls_layout.addWidget(self.search_input)

        controls_layout.addSpacing(20)

        # Options
        controls_layout.addWidget(QLabel("Show:"))
        self.limit_combo = QComboBox()
        self.limit_combo.addItems(["Top 10", "Top 20", "Top 50"])
        self.limit_combo.currentTextChanged.connect(self.load_coins)
        controls_layout.addWidget(self.limit_combo)

        controls_layout.addWidget(QLabel("Currency:"))
        self.currency_combo = QComboBox()
        self.currency_combo.addItems(["USD", "EUR"])
        self.currency_combo.currentTextChanged.connect(self.load_coins)
        controls_layout.addWidget(self.currency_combo)

        controls_layout.addSpacing(20)

        # Refresh button
        self.refresh_btn = QPushButton("🔄 Refresh Data")
        self.refresh_btn.clicked.connect(self.load_coins)
        self.refresh_btn.setStyleSheet(
            """
            QPushButton {
                padding: 8px 15px;
                background-color: #3498db;
                color: white;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """
        )
        controls_layout.addWidget(self.refresh_btn)

        controls_layout.addStretch()
        layout.addLayout(controls_layout)

        # Status label
        self.status_label = QLabel("⏳ Loading cryptocurrency data...")
        self.status_label.setStyleSheet(
            "color: #7f8c8d; font-weight: bold; margin: 5px;"
        )
        layout.addWidget(self.status_label)

        # Create table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(
            ["Rank", "Coin", "Symbol", "Price", "24h Change", "Market Cap"]
        )
        self.table.setMinimumSize(600, 400)
        self.table.setSortingEnabled(True)
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setStretchLastSection(True)

        layout.addWidget(self.table)

        self.setLayout(layout)

    def load_coins(self):
        try:
            self.refresh_btn.setEnabled(False)
            self.refresh_btn.setText("Loading...")
            self.status_label.setText("⏳ Fetching live data from CoinGecko...")

            limit = int(self.limit_combo.currentText().split()[1])
            currency = self.currency_combo.currentText().lower()

            coins = self.api.get_top_coins(limit=limit, vs_currency=currency)
            print(f"API returned {len(coins)} coins")

            if coins and len(coins) > 0:
                self.coins_data = coins
                self.update_table_with_real_data()
                self.status_label.setText(f"✅ Live data loaded: {len(coins)} coins")
            else:
                self.status_label.setText("⚠️ No data returned from API")
                self.show_sample_data()
        except Exception as e:
            print(f"Error loading coins: {e}")
            self.status_label.setText(f"⚠️ Error: {str(e)[:50]}... - Using sample data")
            self.show_sample_data()
        finally:
            self.refresh_btn.setText("🔄 Refresh Data")
            self.refresh_btn.setEnabled(True)

    def update_table_with_real_data(self):
        if not self.coins_data:
            return

        self.table.setRowCount(len(self.coins_data))

        for row, coin in enumerate(self.coins_data):
            rank = coin.get("market_cap_rank", row + 1)
            name = coin.get("name", "Unknown")
            symbol = coin.get("symbol", "").upper()
            price = coin.get("current_price", 0)
            change_24h = coin.get("price_change_percentage_24h_in_currency", 0) or 0
            market_cap = coin.get("market_cap", 0)

            self.table.setItem(row, 0, QTableWidgetItem(str(rank)))
            self.table.setItem(row, 1, QTableWidgetItem(name))
            self.table.setItem(row, 2, QTableWidgetItem(symbol))

            if price >= 1:
                price_text = f"${price:,.2f}"
            elif price >= 0.0001:
                price_text = f"${price:.4f}"
            else:
                price_text = f"${price:.8f}"
            self.table.setItem(row, 3, QTableWidgetItem(price_text))

            change_item = QTableWidgetItem(f"{change_24h:+.2f}%")
            if change_24h > 0:
                change_item.setForeground(QBrush(QColor("#27ae60")))
            elif change_24h < 0:
                change_item.setForeground(QBrush(QColor("#e74c3c")))
            self.table.setItem(row, 4, change_item)

            if market_cap >= 1e12:
                mcap_text = f"${market_cap/1e12:.2f}T"
            elif market_cap >= 1e9:
                mcap_text = f"${market_cap/1e9:.2f}B"
            elif market_cap >= 1e6:
                mcap_text = f"${market_cap/1e6:.2f}M"
            else:
                mcap_text = f"${market_cap:,.0f}"
            self.table.setItem(row, 5, QTableWidgetItem(mcap_text))

        self.table.resizeColumnsToContents()

    def show_sample_data(self):
        sample_coins = [
            {
                "name": "Bitcoin",
                "symbol": "btc",
                "price": 45123.45,
                "change": 2.34,
                "market_cap": 850200000000,
                "rank": 1,
            },
            {
                "name": "Ethereum",
                "symbol": "eth",
                "price": 2456.78,
                "change": 1.23,
                "market_cap": 295400000000,
                "rank": 2,
            },
            {
                "name": "Solana",
                "symbol": "sol",
                "price": 102.34,
                "change": 5.67,
                "market_cap": 44800000000,
                "rank": 3,
            },
        ]

        self.table.setRowCount(len(sample_coins))

        for row, coin in enumerate(sample_coins):
            self.table.setItem(row, 0, QTableWidgetItem(str(coin["rank"])))
            self.table.setItem(row, 1, QTableWidgetItem(coin["name"]))
            self.table.setItem(row, 2, QTableWidgetItem(coin["symbol"].upper()))

            price_text = (
                f"${coin['price']:,.2f}"
                if coin["price"] >= 1
                else f"${coin['price']:.4f}"
            )
            self.table.setItem(row, 3, QTableWidgetItem(price_text))

            change_item = QTableWidgetItem(f"{coin['change']:+.2f}%")
            if coin["change"] > 0:
                change_item.setForeground(QBrush(QColor("#27ae60")))
            elif coin["change"] < 0:
                change_item.setForeground(QBrush(QColor("#e74c3c")))
            self.table.setItem(row, 4, change_item)

            mcap = coin["market_cap"]
            mcap_text = f"${mcap/1e9:.1f}B" if mcap >= 1e9 else f"${mcap/1e6:.1f}M"
            self.table.setItem(row, 5, QTableWidgetItem(mcap_text))

        self.table.resizeColumnsToContents()

    def filter_coins(self):
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


class EnhancedPredictionTab(QWidget):
    """Enhanced AI Price Predictions with detailed analysis"""

    def __init__(self, api_handler, predictor):
        super().__init__()
        self.api = api_handler
        self.predictor = predictor
        self.worker = None
        self.init_ui()

    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout()

        # Title
        title_label = QLabel("🔮 AI Price Predictions")
        title_label.setStyleSheet(
            "font-size: 18px; font-weight: bold; margin: 10px; color: #2c3e50;"
        )
        layout.addWidget(title_label)

        # Controls
        controls_layout = QHBoxLayout()

        # Coin selection
        controls_layout.addWidget(QLabel("Select Coin:"))
        self.coin_combo = QComboBox()
        controls_layout.addWidget(self.coin_combo)

        # Time frame selection
        controls_layout.addWidget(QLabel("Time Frame:"))
        self.time_frame_combo = QComboBox()
        self.time_frame_combo.addItems(["24 Hours", "7 Days", "30 Days"])
        controls_layout.addWidget(self.time_frame_combo)

        # Prediction button
        self.predict_btn = QPushButton("🔮 Predict Price")
        self.predict_btn.clicked.connect(self.run_prediction)
        controls_layout.addWidget(self.predict_btn)

        layout.addLayout(controls_layout)

        # Results area
        self.results_group = QGroupBox("Prediction Results")
        results_layout = QVBoxLayout()

        # Current price
        self.current_price_label = QLabel("Current Price: -")
        self.current_price_label.setStyleSheet("font-size: 14px; margin: 5px; color: #2c3e50;")
        results_layout.addWidget(self.current_price_label)

        # Predicted price
        self.predicted_price_label = QLabel("Predicted Price: -")
        self.predicted_price_label.setStyleSheet("font-size: 16px; font-weight: bold; margin: 5px; color: #2c3e50;")
        results_layout.addWidget(self.predicted_price_label)

        # Change percentage
        self.change_label = QLabel("Change: -")
        self.change_label.setStyleSheet("font-size: 14px; margin: 5px; color: #2c3e50;")
        results_layout.addWidget(self.change_label)

        # Confidence score
        self.confidence_label = QLabel("Confidence: -")
        self.confidence_label.setStyleSheet("font-size: 14px; margin: 5px; color: #2c3e50;")
        results_layout.addWidget(self.confidence_label)

        # Direction indicator
        self.direction_label = QLabel("Direction: -")
        self.direction_label.setStyleSheet("font-size: 14px; margin: 5px; color: #2c3e50;")
        results_layout.addWidget(self.direction_label)

        # Insights
        self.insights_label = QLabel("Insights: -")
        self.insights_label.setStyleSheet("font-size: 14px; margin: 5px; color: #2c3e50;")
        self.insights_label.setWordWrap(True)
        results_layout.addWidget(self.insights_label)

        self.results_group.setLayout(results_layout)
        self.results_group.hide()  # Hide until we have results
        layout.addWidget(self.results_group)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        layout.addWidget(self.progress_bar)

        self.setLayout(layout)

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
            # Get current price
            current_price = 0
            coins = self.api.get_top_coins(limit=50, vs_currency="usd")
            for coin in coins:
                if coin["id"] == coin_id:
                    current_price = coin.get("current_price", 0)
                    break

            if current_price <= 0:
                QMessageBox.warning(self, "Warning", "Could not get current price for selected coin.")
                return

            # Show current price
            self.current_price_label.setText(f"Current Price: ${current_price:,.2f}")
            self.results_group.show()

            # Get time frame
            time_frame = self.time_frame_combo.currentText()
            days = 1 if time_frame == "24 Hours" else 7 if time_frame == "7 Days" else 30

            # Start prediction worker
            self.worker = PredictionWorker(self.predictor, coin_id, current_price, days)
            self.worker.progress_update.connect(self.update_progress)
            self.worker.prediction_complete.connect(self.show_prediction)
            self.worker.error_occurred.connect(self.show_error)
            self.worker.start()

            self.progress_bar.setValue(0)
            self.predict_btn.setEnabled(False)

        except Exception as e:
            self.show_error(f"Error: {str(e)}")

    def update_progress(self, value, message):
        """Update progress bar and status"""
        self.progress_bar.setValue(value)
        self.predicted_price_label.setText(message)

    def show_prediction(self, result):
        """Display the prediction results"""
        try:
            self.predict_btn.setEnabled(True)
            self.progress_bar.setValue(100)

            # Format results
            current_price = result['current_price']
            predicted_price = result['predicted_price']
            change_percent = result['predicted_change_percent']
            confidence = result['confidence_score']
            direction = result['direction']
            insights = result.get('insights', [])

            # Update UI with results
            self.predicted_price_label.setText(f"Predicted Price: ${predicted_price:,.2f}")

            # Color code the change based on direction
            change_text = f"Change: {change_percent:+.2f}%"
            change_color = "green" if change_percent >= 0 else "red"
            self.change_label.setText(f'<span style="color:{change_color};">{change_text}</span>')
            self.change_label.setTextFormat(Qt.RichText)

            self.confidence_label.setText(f"Confidence: {confidence:.1f}%")

            direction_color = "green" if direction == "bullish" else "red"
            self.direction_label.setText(f'<span style="color:{direction_color};">Direction: {direction.capitalize()}</span>')
            self.direction_label.setTextFormat(Qt.RichText)

            insights_text = "<br>".join(f"• {insight}" for insight in insights)
            self.insights_label.setText(f"Insights:<br>{insights_text}")
            self.insights_label.setTextFormat(Qt.RichText)

            self.results_group.show()

        except Exception as e:
            self.show_error(f"Error displaying results: {str(e)}")

    def show_error(self, error_message):
        """Display error message"""
        self.predict_btn.setEnabled(True)
        self.progress_bar.setValue(0)
        QMessageBox.critical(self, "Prediction Error", error_message)
        self.predicted_price_label.setText("Error occurred during prediction")


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
        main_layout = QVBoxLayout(self)

        # Top bar with buttons and currency selection
        top_bar = QHBoxLayout()
        self.add_btn = QPushButton("➕ Add Transaction")
        self.refresh_btn = QPushButton("🔄 Refresh")
        self.export_btn = QPushButton("📤 Export to CSV")

        # Currency Combo Box
        self.currency_combo = QComboBox()
        self.currency_combo.addItems(["USD", "EUR", "GBP", "JPY"])
        self.currency_combo.currentTextChanged.connect(self.on_currency_changed)

        self.total_lbl = QLabel("Total value: $0.00")

        top_bar.addWidget(self.add_btn)
        top_bar.addWidget(self.refresh_btn)
        top_bar.addWidget(self.export_btn)
        top_bar.addWidget(QLabel("Currency:"))
        top_bar.addWidget(self.currency_combo)
        top_bar.addStretch()
        top_bar.addWidget(self.total_lbl)
        main_layout.addLayout(top_bar)

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
            self.total_lbl.setText(f"Total value: {self.currency.upper()} 0.00")
            return

        # Get prices
        ids = list(holdings.keys())
        try:
            price_data = self.api.get_price(ids, vs_currency=self.currency)
        except Exception as e:
            print(f"Error fetching prices: {e}")
            self.total_lbl.setText("Error: Could not fetch prices")
            return

        # Fill the table
        self.table.setRowCount(len(ids))
        total_value = 0.0
        total_pnl = 0.0

        for row, coin_id in enumerate(ids):
            try:
                coin_info = self.api.get_coin_info(coin_id)
                name = coin_info.get("name", coin_id)
                symbol = coin_info.get("symbol", "").upper()

                amount = holdings[coin_id]["amount"]
                avg_price = holdings[coin_id]["avg_price"]
                cur_price = price_data.get(coin_id, {}).get(self.currency, 0.0)
                value = amount * cur_price
                pnl = (cur_price - avg_price) * amount
                total_value += value
                total_pnl += pnl

                # Populate cells
                self.table.setItem(row, 0, QTableWidgetItem(name))
                self.table.setItem(row, 1, QTableWidgetItem(symbol))
                self.table.setItem(row, 2, QTableWidgetItem(f"{amount:,.8f}"))
                self.table.setItem(
                    row,
                    3,
                    QTableWidgetItem(f"{self.currency.upper()} {avg_price:,.2f}"),
                )
                self.table.setItem(
                    row,
                    4,
                    QTableWidgetItem(f"{self.currency.upper()} {cur_price:,.2f}"),
                )
                self.table.setItem(
                    row, 5, QTableWidgetItem(f"{self.currency.upper()} {value:,.2f}")
                )

                # PnL column with color coding
                pnl_item = QTableWidgetItem(f"{self.currency.upper()} {pnl:,.2f}")
                if pnl >= 0:
                    pnl_item.setForeground(QBrush(QColor("green")))
                else:
                    pnl_item.setForeground(QBrush(QColor("red")))
                self.table.setItem(row, 6, pnl_item)

            except Exception as e:
                print(f"Error processing {coin_id}: {e}")
                continue

        # Calculate and display percentages
        for row in range(self.table.rowCount()):
            try:
                value_text = self.table.item(row, 5).text()
                value = float(value_text.split()[1].replace(",", ""))
                perc = (value / total_value) * 100 if total_value else 0
                perc_item = QTableWidgetItem(f"{perc:,.2f}%")
                perc_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.table.setItem(row, 7, perc_item)
            except Exception as e:
                print(f"Error calculating % for row {row}: {e}")

        # Update total value label
        currency_symbol = (
            "$"
            if self.currency == "usd"
            else (
                "€"
                if self.currency == "eur"
                else "£" if self.currency == "gbp" else "¥"
            )
        )
        self.total_lbl.setText(f"Total value: {currency_symbol}{total_value:,.2f}")

        # Update status bar with PnL
        pnl_color = "green" if total_pnl >= 0 else "red"
        self.parent().status_bar.showMessage(
            f"Total PnL: <span style='color:{pnl_color};'>{currency_symbol}{total_pnl:,.2f}</span>"
        )

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
            for coin_id in ids:
                coin_info = self.api.get_coin_info(coin_id)
                name = coin_info.get("name", coin_id)
                symbol = coin_info.get("symbol", "").upper()
                amount = holdings[coin_id]["amount"]
                avg_price = holdings[coin_id]["avg_price"]
                cur_price = price_data.get(coin_id, {}).get(self.currency, 0.0)
                value = amount * cur_price
                pnl = (cur_price - avg_price) * amount

                data.append(
                    {
                        "Coin": name,
                        "Symbol": symbol,
                        "Amount": amount,
                        f"Avg. Price ({self.currency.upper()})": avg_price,
                        f"Current Price ({self.currency.upper()})": cur_price,
                        f"Value ({self.currency.upper()})": value,
                        f"PnL ({self.currency.upper()})": pnl,
                        "% of Portfolio": (
                            (value / sum(p[5] for p in data)) * 100 if data else 0
                        ),
                    }
                )

            df = pd.DataFrame(data)
            df.to_csv(file_path, index=False)
            QMessageBox.information(
                self, "Success", f"Portfolio exported to {file_path}"
            )

        except Exception as e:
            print(f"Error exporting to CSV: {e}")
            QMessageBox.critical(self, "Error", f"Failed to export: {e}")


class EnhancedSentimentTab(QWidget):
    def __init__(self, api_handler):
        super().__init__()
        self.api = api_handler
        self.sentiment_tracker = SentimentTracker(self.api)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Title
        title_label = QLabel("📊 Market Sentiment Analysis")
        title_label.setStyleSheet(
            "font-size: 18px; font-weight: bold; margin: 10px; color: #2c3e50;"
        )
        layout.addWidget(title_label)

        # Fear & Greed Index
        self.fgi_label = QLabel("Fear & Greed Index: Loading...")
        self.fgi_label.setStyleSheet("font-size: 14px; margin: 10px; color: #2c3e50;")
        layout.addWidget(self.fgi_label)

        # Market Analysis
        self.market_analysis_label = QLabel("Market Analysis: Loading...")
        self.market_analysis_label.setStyleSheet(
            "font-size: 14px; margin: 10px; color: #2c3e50;"
        )
        layout.addWidget(self.market_analysis_label)

        # Coin-specific sentiment (optional)
        controls_layout = QHBoxLayout()
        controls_layout.addWidget(QLabel("Select Coin:"))
        self.coin_combo = QComboBox()
        controls_layout.addWidget(self.coin_combo)

        self.analyze_btn = QPushButton("🔍 Analyze Sentiment")
        self.analyze_btn.clicked.connect(self.analyze_coin_sentiment)
        controls_layout.addWidget(self.analyze_btn)
        layout.addLayout(controls_layout)

        # Coin sentiment result
        self.coin_sentiment_label = QLabel(
            "Coin Sentiment: Select a coin and click 'Analyze'"
        )
        self.coin_sentiment_label.setStyleSheet(
            "font-size: 14px; margin: 10px; color: #2c3e50;"
        )
        layout.addWidget(self.coin_sentiment_label)

        self.setLayout(layout)
        self.load_coins()
        self.refresh_sentiment()

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
                self.fgi_label.setText(
                    f"Fear & Greed Index: {fgi['value']} ({fgi['classification']})"
                )

            # Market analysis
            market_data = self.sentiment_tracker.get_market_sentiment()
            analysis = market_data.get("market_analysis", {})
            self.market_analysis_label.setText(
                f"Market Sentiment: {analysis.get('market_sentiment', 'Neutral')}\n"
                f"Gainers: {analysis.get('gainers', 0)} | Losers: {analysis.get('losers', 0)}"
            )
        except Exception as e:
            print(f"Error refreshing sentiment: {e}")

    def analyze_coin_sentiment(self):
        """Fetch and display sentiment for the selected coin"""
        coin_id = self.coin_combo.currentData()
        if not coin_id:
            self.coin_sentiment_label.setText("Please select a coin first.")
            return

        try:
            sentiment = self.sentiment_tracker.get_coin_sentiment(coin_id)
            self.coin_sentiment_label.setText(
                f"Sentiment for {self.coin_combo.currentText()}:\n"
                f"Positive: {sentiment['positive']:.2f}% | "
                f"Negative: {sentiment['negative']:.2f}% | "
                f"Neutral: {sentiment['neutral']:.2f}%"
            )
        except Exception as e:
            self.coin_sentiment_label.setText(f"Error analyzing sentiment: {str(e)}")
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

        self.tabs = QTabWidget()
        self.tabs.addTab(ImprovedMarketTab(self.api), "Market Overview")
        self.tabs.addTab(
            EnhancedPredictionTab(self.api, self.predictor), "AI Predictions"
        )
        self.tabs.addTab(EnhancedPortfolioTab(self.api, self.portfolio), "Portfolio")
        self.tabs.addTab(EnhancedSentimentTab(self.api), "Market Sentiment")

        main_layout.addWidget(self.tabs)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Application ready")


# ==================== MAIN FUNCTION ====================
def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = EnhancedCryptoTrackerApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
