# src/main_app_pyqt.py

import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QPushButton, QComboBox, QHBoxLayout, QLabel,
    QHeaderView, QStatusBar, QTabWidget, QTextEdit, QSplitter,
    QProgressBar, QGroupBox, QFormLayout, QLineEdit, QDoubleSpinBox,
    QMessageBox, QFileDialog, QDialog, QDialogButtonBox, QGridLayout
)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt5.QtGui import QBrush, QColor, QFont, QPalette
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib
matplotlib.use('Qt5Agg')

from api_handler import EnhancedCryptoAPIHandler
from improved_price_predictor import AdvancedPricePredictor
from improved_portfolio_tracker import PortfolioTracker
from improved_sentiment_tracker import SentimentTracker


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
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal, self
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons, 5, 0, 1, 2)
        
        self.setLayout(layout)
        self.resize(300, 200)
    
    def get_data(self):
        return {
            'coin': self.coin_combo.currentData(),
            'type': self.type_combo.currentText().lower(),
            'amount': self.amount_input.value(),
            'price': self.price_input.value(),
            'date': self.date_input.text()
        }
    
    def load_coins(self, coins):
        """Load coins into combo box"""
        for coin in coins:
            self.coin_combo.addItem(
                f"{coin['symbol'].upper()} - {coin['name']}",
                coin['id']
            )


class MLPredictionTab(QWidget):
    """Dedicated tab for ML predictions"""
    def __init__(self, api_handler, predictor):
        super().__init__()
        self.api = api_handler
        self.predictor = predictor
        self.current_prediction = None
        self.worker = None
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Title
        title_label = QLabel("AI Price Predictions")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(title_label)
        
        # Controls section
        control_group = QGroupBox("Prediction Controls")
        control_layout = QGridLayout()
        
        # Coin selection
        control_layout.addWidget(QLabel("Select Coin:"), 0, 0)
        self.coin_selector = QComboBox()
        self.coin_selector.setMinimumWidth(250)
        control_layout.addWidget(self.coin_selector, 0, 1)
        
        # Current price display
        control_layout.addWidget(QLabel("Current Price:"), 0, 2)
        self.current_price_display = QLabel("N/A")
        control_layout.addWidget(self.current_price_display, 0, 3)
        
        # Buttons
        self.predict_button = QPushButton("Predict Price")
        self.predict_button.clicked.connect(self.run_prediction)
        self.predict_button.setMinimumHeight(35)
        control_layout.addWidget(self.predict_button, 1, 0, 1, 2)
        
        self.train_button = QPushButton("Train Model")
        self.train_button.clicked.connect(self.train_model)
        self.train_button.setMinimumHeight(35)
        control_layout.addWidget(self.train_button, 1, 2, 1, 2)
        
        control_group.setLayout(control_layout)
        layout.addWidget(control_group)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Results splitter
        splitter = QSplitter(Qt.Vertical)
        
        # Results section
        results_group = QGroupBox("Prediction Results")
        results_layout = QGridLayout()
        
        results_layout.addWidget(QLabel("Current Price:"), 0, 0)
        self.current_price_label = QLabel("N/A")
        self.current_price_label.setStyleSheet("font-size: 14px;")
        results_layout.addWidget(self.current_price_label, 0, 1)
        
        results_layout.addWidget(QLabel("Predicted Price (24h):"), 1, 0)
        self.predicted_price_label = QLabel("N/A")
        self.predicted_price_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        results_layout.addWidget(self.predicted_price_label, 1, 1)
        
        results_layout.addWidget(QLabel("Predicted Change:"), 2, 0)
        self.change_label = QLabel("N/A")
        results_layout.addWidget(self.change_label, 2, 1)
        
        results_layout.addWidget(QLabel("Confidence Score:"), 0, 2)
        self.confidence_label = QLabel("N/A")
        results_layout.addWidget(self.confidence_label, 0, 3)
        
        results_layout.addWidget(QLabel("Market Direction:"), 1, 2)
        self.direction_label = QLabel("N/A")
        results_layout.addWidget(self.direction_label, 1, 3)
        
        results_layout.addWidget(QLabel("Model Status:"), 2, 2)
        self.model_status_label = QLabel("Not trained")
        results_layout.addWidget(self.model_status_label, 2, 3)
        
        results_group.setLayout(results_layout)
        splitter.addWidget(results_group)
        
        # Insights section
        insights_group = QGroupBox("Trading Insights & Technical Analysis")
        insights_layout = QVBoxLayout()
        
        self.insights_text = QTextEdit()
        self.insights_text.setReadOnly(True)
        self.insights_text.setMaximumHeight(120)
        insights_layout.addWidget(self.insights_text)
        
        insights_group.setLayout(insights_layout)
        splitter.addWidget(insights_group)
        
        # Chart section
        chart_group = QGroupBox("Prediction Visualization")
        chart_layout = QVBoxLayout()
        
        self.chart_canvas = self.create_prediction_chart()
        chart_layout.addWidget(self.chart_canvas)
        
        chart_group.setLayout(chart_layout)
        splitter.addWidget(chart_group)
        
        splitter.setSizes([150, 150, 400])
        layout.addWidget(splitter)
        
        self.setLayout(layout)
        
        # Load available coins
        self.load_coins()
        
        # Connect coin selection change
        self.coin_selector.currentIndexChanged.connect(self.on_coin_selected)
    
    def create_prediction_chart(self):
        """Create matplotlib canvas for predictions"""
        self.figure = Figure(figsize=(8, 4))
        self.ax = self.figure.add_subplot(111)
        canvas = FigureCanvas(self.figure)
        canvas.setMinimumHeight(300)
        return canvas
    
    def load_coins(self):
        """Load top coins for prediction"""
        try:
            self.coin_selector.clear()
            coins = self.api.get_top_coins(limit=30)
            for coin in coins:
                self.coin_selector.addItem(
                    f"{coin['symbol'].upper()} - {coin['name']}",
                    coin['id']
                )
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load coins: {str(e)}")
    
    def on_coin_selected(self):
        """Update current price when coin is selected"""
        coin_id = self.coin_selector.currentData()
        if coin_id:
            try:
                price_data = self.api.get_coin_price([coin_id], 'usd')
                current_price = price_data.get(coin_id, {}).get('usd', 0)
                if current_price > 0:
                    self.current_price_display.setText(f"${current_price:,.2f}")
                
                # Update model status
                performance = self.predictor.get_model_performance(coin_id)
                if performance:
                    self.model_status_label.setText(f"Trained (MAE: {performance.get('ensemble_mae', 0):.4f})")
                else:
                    self.model_status_label.setText("Not trained")
                    
            except:
                pass
    
    def run_prediction(self):
        """Run ML prediction"""
        coin_id = self.coin_selector.currentData()
        if not coin_id:
            QMessageBox.warning(self, "Warning", "Please select a coin first")
            return
        
        # Get current price
        try:
            price_data = self.api.get_coin_price([coin_id], 'usd')
            current_price = price_data.get(coin_id, {}).get('usd', 0)
            
            if current_price == 0:
                QMessageBox.warning(self, "Warning", "Failed to get current price")
                return
            
            # Disable UI during prediction
            self.predict_button.setEnabled(False)
            self.train_button.setEnabled(False)
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            
            # Start prediction worker
            self.worker = PredictionWorker(self.predictor, coin_id, current_price)
            self.worker.prediction_complete.connect(self.display_prediction)
            self.worker.progress_update.connect(self.update_progress)
            self.worker.error_occurred.connect(self.on_prediction_error)
            self.worker.start()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Prediction failed: {str(e)}")
            self.reset_ui()
    
    def train_model(self):
        """Train ML model for selected coin"""
        coin_id = self.coin_selector.currentData()
        if not coin_id:
            QMessageBox.warning(self, "Warning", "Please select a coin first")
            return
        
        # Show training dialog
        reply = QMessageBox.question(
            self, "Train Model",
            f"Train model for {self.coin_selector.currentText()}?\n\n"
            "This will use 90 days of historical data and may take a moment.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Disable UI during training
            self.predict_button.setEnabled(False)
            self.train_button.setEnabled(False)
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            
            # Train in background thread
            QTimer.singleShot(100, lambda: self.do_train_model(coin_id))
    
    def do_train_model(self, coin_id):
        """Perform model training"""
        try:
            self.progress_bar.setValue(25)
            
            success, message = self.predictor.train_ensemble_model(coin_id)
            
            self.progress_bar.setValue(100)
            
            if success:
                QMessageBox.information(self, "Success", 
                    f"Model trained successfully!\n\n{message}")
                
                # Update model status
                performance = self.predictor.get_model_performance(coin_id)
                if performance:
                    self.model_status_label.setText(f"Trained (MAE: {performance.get('ensemble_mae', 0):.4f})")
            else:
                QMessageBox.warning(self, "Warning", 
                    f"Model training failed:\n\n{message}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Training error: {str(e)}")
        finally:
            self.reset_ui()
    
    def display_prediction(self, result):
        """Display prediction results"""
        self.current_prediction = result
        
        # Update labels
        self.current_price_label.setText(f"${result['current_price']:,.2f}")
        
        # Color code based on direction
        if result['predicted_change_percent'] > 0:
            color = "#00aa00"  # Green
            direction_text = "BULLISH"
        elif result['predicted_change_percent'] < 0:
            color = "#aa0000"  # Red
            direction_text = "BEARISH"
        else:
            color = "#666666"  # Gray
            direction_text = "NEUTRAL"
        
        self.predicted_price_label.setText(
            f"<span style='color: {color}'>${result['predicted_price']:,.2f}</span>"
        )
        
        change_text = f"{result['predicted_change_percent']:+.2f}%"
        self.change_label.setText(
            f"<span style='color: {color}'>{change_text}</span>"
        )
        
        self.confidence_label.setText(f"{result['confidence_score']:.1f}%")
        self.direction_label.setText(
            f"<span style='color: {color}; font-weight: bold;'>{direction_text}</span>"
        )
        
        # Display insights
        insights_text = "TECHNICAL ANALYSIS INSIGHTS:\n\n"
        for insight in result['insights']:
            insights_text += f"• {insight}\n"
        
        if result.get('is_fallback', False):
            insights_text += "\nNOTE: Using fallback prediction model"
        
        self.insights_text.setPlainText(insights_text)
        
        # Update chart
        self.update_prediction_chart(result)
        
        # Reset UI
        self.reset_ui()
        
        # Show success message
        if not result.get('is_fallback', False):
            self.status_message = f"Prediction complete: {result['direction'].upper()} with {result['confidence_score']:.1f}% confidence"
    
    def update_prediction_chart(self, result):
        """Update prediction chart"""
        self.ax.clear()
        
        # Create data
        labels = ['Current Price', 'Predicted Price']
        prices = [result['current_price'], result['predicted_price']]
        
        # Set colors
        colors = ['#1f77b4']  # Blue for current
        if result['predicted_change_percent'] > 0:
            colors.append('#2ca02c')  # Green for bullish
        else:
            colors.append('#d62728')  # Red for bearish
        
        # Create bars
        bars = self.ax.bar(labels, prices, color=colors, alpha=0.7, width=0.6)
        
        # Add value labels on bars
        for bar, price in zip(bars, prices):
            height = bar.get_height()
            self.ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'${price:,.2f}', ha='center', va='bottom',
                       fontsize=10, fontweight='bold')
        
        # Add percentage change label
        change_text = f"{result['predicted_change_percent']:+.2f}%"
        self.ax.text(1, result['predicted_price'] * 0.9,
                   f"Change: {change_text}\nConfidence: {result['confidence_score']:.1f}%",
                   ha='center', fontsize=9,
                   bbox=dict(boxstyle="round,pad=0.3", facecolor="#f0f0f0", alpha=0.8))
        
        # Format chart
        self.ax.set_ylabel('Price (USD)', fontsize=10)
        self.ax.set_title('24-Hour Price Prediction', fontsize=12, fontweight='bold')
        self.ax.grid(True, alpha=0.3, linestyle='--')
        
        # Adjust layout
        self.figure.tight_layout()
        self.chart_canvas.draw()
    
    def update_progress(self, value, message):
        """Update progress bar"""
        self.progress_bar.setValue(value)
        self.progress_bar.setFormat(f"{message}... {value}%")
    
    def on_prediction_error(self, error_message):
        """Handle prediction errors"""
        QMessageBox.warning(self, "Prediction Error", error_message)
        self.reset_ui()
    
    def reset_ui(self):
        """Reset UI elements"""
        self.predict_button.setEnabled(True)
        self.train_button.setEnabled(True)
        self.progress_bar.setVisible(False)


class CryptoTrackerApp(QMainWindow):
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
        self.tabs.addTab(MLPredictionTab(self.api, self.predictor), "AI Predictions")
        self.tabs.addTab(self.create_portfolio_tab(), "Portfolio")
        self.tabs.addTab(self.create_sentiment_tab(), "Market Sentiment")
        
        main_layout.addWidget(self.tabs)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Application ready")
        
        # Initialize data
        self.load_initial_data()
    
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
        self.currency_combo.addItems(['USD', 'EUR', 'GBP', 'JPY', 'BTC'])
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
        self.auto_refresh_combo.addItems(['Off', '30 seconds', '1 minute', '5 minutes'])
        self.auto_refresh_combo.currentTextChanged.connect(self.toggle_auto_refresh)
        control_layout.addWidget(self.auto_refresh_combo)
        
        control_layout.addStretch()
        control_panel.setLayout(control_layout)
        layout.addWidget(control_panel)
        
        # Market data table
        self.market_table = QTableWidget()
        self.market_table.setColumnCount(11)
        self.market_table.setHorizontalHeaderLabels([
            "Rank", "Coin", "Symbol", "Price", "1h %", "24h %", "7d %", 
            "Market Cap", "Volume (24h)", "AI Prediction", "AI Confidence"
        ])
        
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
        self.portfolio_table.setHorizontalHeaderLabels([
            "Coin", "Symbol", "Amount", "Avg Cost", "Current Price", 
            "Current Value", "P/L ($)", "P/L (%)", "Allocation %"
        ])
        
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
                rank = coin.get('market_cap_rank', row + 1)
                name = coin.get('name', 'Unknown')
                symbol = coin.get('symbol', '').upper()
                price = coin.get('current_price', 0)
                
                # Price changes (handle None values)
                change_1h = coin.get('price_change_percentage_1h_in_currency', 0) or 0
                change_24h = coin.get('price_change_percentage_24h', 0) or 0
                change_7d = coin.get('price_change_percentage_7d_in_currency', 0) or 0
                
                # Market data
                market_cap = coin.get('market_cap', 0)
                volume = coin.get('total_volume', 0)
                
                # Accumulate totals
                total_market_cap += market_cap
                total_volume += volume
                
                # Get ML prediction (in background to avoid UI freeze)
                coin_id = coin.get('id')
                
                # Fill table with basic data
                self.market_table.setItem(row, 0, QTableWidgetItem(str(rank)))
                self.market_table.setItem(row, 1, QTableWidgetItem(name))
                self.market_table.setItem(row, 2, QTableWidgetItem(symbol))
                self.market_table.setItem(row, 3, QTableWidgetItem(f"{price:,.2f}"))
                
                # Add percentage changes with color coding
                for col_idx, value in enumerate([change_1h, change_24h, change_7d], start=4):
                    item = QTableWidgetItem(f"{value:+.2f}%")
                    if value > 0:
                        item.setForeground(QBrush(QColor("#00aa00")))  # Green
                    elif value < 0:
                        item.setForeground(QBrush(QColor("#aa0000")))  # Red
                    self.market_table.setItem(row, col_idx, item)
                
                # Market cap and volume
                self.market_table.setItem(row, 7, QTableWidgetItem(f"{market_cap:,.0f}"))
                self.market_table.setItem(row, 8, QTableWidgetItem(f"{volume:,.0f}"))
                
                # Get prediction in background thread
                QTimer.singleShot(row * 100, lambda r=row, cid=coin_id, p=price: 
                                self.update_prediction_cell(r, cid, p))
            
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
                    pred_price = prediction['predicted_price']
                    confidence = prediction['confidence_score']
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
        active_coins = len([c for c in coins if c.get('active', True)])
        
        for coin in coins:
            if coin.get('symbol', '').lower() == 'btc':
                btc_dominance = coin.get('market_cap_percentage', 0)
                break
        
        # Update labels
        currency_symbol = "$" if self.current_currency == "usd" else self.current_currency.upper()
        
        self.total_market_cap_label.setText(
            f"Total Market Cap: {currency_symbol}{total_market_cap:,.0f}"
        )
        
        self.total_volume_label.setText(
            f"24h Volume: {currency_symbol}{total_volume:,.0f}"
        )
        
        self.btc_dominance_label.setText(
            f"BTC Dominance: {btc_dominance:.1f}%"
        )
        
        self.active_coins_label.setText(
            f"Active Coins: {active_coins}"
        )
    
    def export_market_data(self):
        """Export market data to CSV"""
        try:
            if not self.top_coins:
                QMessageBox.warning(self, "No Data", "No market data to export")
                return
            
            filename, _ = QFileDialog.getSaveFileName(
                self, "Export Market Data", "market_data.csv",
                "CSV Files (*.csv);;All Files (*)"
            )
            
            if filename:
                # Create DataFrame from coins data
                df_data = []
                for coin in self.top_coins:
                    # Get prediction for this coin
                    coin_id = coin.get('id')
                    price = coin.get('current_price', 0)
                    prediction = self.predictor.predict_price(coin_id, price) if coin_id else {}
                    
                    row_data = {
                        'rank': coin.get('market_cap_rank', ''),
                        'name': coin.get('name', ''),
                        'symbol': coin.get('symbol', '').upper(),
                        'price': price,
                        'price_change_1h': coin.get('price_change_percentage_1h_in_currency', 0) or 0,
                        'price_change_24h': coin.get('price_change_percentage_24h', 0) or 0,
                        'price_change_7d': coin.get('price_change_percentage_7d_in_currency', 0) or 0,
                        'market_cap': coin.get('market_cap', 0),
                        'volume_24h': coin.get('total_volume', 0),
                        'predicted_price': prediction.get('predicted_price', 0),
                        'predicted_change': prediction.get('predicted_change_percent', 0),
                        'confidence_score': prediction.get('confidence_score', 0),
                        'direction': prediction.get('direction', 'neutral'),
                        'last_updated': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    df_data.append(row_data)
                
                df = pd.DataFrame(df_data)
                df.to_csv(filename, index=False)
                
                self.status_bar.showMessage(f"Market data exported to {filename}")
                QMessageBox.information(self, "Export Complete", 
                    f"Market data successfully exported to:\n{filename}")
                
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export data: {str(e)}")
    
    def toggle_auto_refresh(self, option):
        """Toggle auto-refresh timer"""
        if hasattr(self, 'auto_refresh_timer'):
            self.auto_refresh_timer.stop()
        
        intervals = {
            'Off': 0,
            '30 seconds': 30000,
            '1 minute': 60000,
            '5 minutes': 300000
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
            if not transaction_data['coin']:
                QMessageBox.warning(self, "Error", "Please select a coin")
                return
            
            if transaction_data['amount'] <= 0:
                QMessageBox.warning(self, "Error", "Amount must be greater than 0")
                return
            
            if transaction_data['price'] <= 0:
                QMessageBox.warning(self, "Error", "Price must be greater than 0")
                return
            
            # Add transaction to portfolio
            try:
                self.portfolio.add_transaction(
                    coin_id=transaction_data['coin'],
                    coin_name=dialog.coin_combo.currentText().split(" - ")[0],
                    transaction_type=transaction_data['type'],
                    amount=transaction_data['amount'],
                    price=transaction_data['price'],
                    date=transaction_data['date']
                )
                
                self.refresh_portfolio()
                self.status_bar.showMessage("Transaction added successfully")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to add transaction: {str(e)}")
    
    def refresh_portfolio(self):
        """Refresh portfolio display"""
        try:
            portfolio_data = self.portfolio.get_portfolio_summary()
            
            if not portfolio_data['holdings']:
                self.portfolio_table.setRowCount(0)
                self.total_value_label.setText("Total Value: $0.00")
                self.total_pnl_label.setText("Total P/L: $0.00 (0.00%)")
                return
            
            # Update summary
            total_value = portfolio_data['total_value']
            total_pnl = portfolio_data['total_pnl']
            total_pnl_percent = portfolio_data['total_pnl_percent']
            daily_change = portfolio_data['daily_change']
            daily_change_percent = portfolio_data['daily_change_percent']
            
            # Color code P/L
            pnl_color = "#00aa00" if total_pnl >= 0 else "#aa0000"
            daily_color = "#00aa00" if daily_change >= 0 else "#aa0000"
            
            self.total_value_label.setText(f"Total Value: ${total_value:,.2f}")
            self.total_pnl_label.setText(
                f'<span style="color: {pnl_color}">'
                f'Total P/L: ${total_pnl:,.2f} ({total_pnl_percent:+.2f}%)'
                f'</span>'
            )
            
            self.daily_change_label.setText(
                f'<span style="color: {daily_color}">'
                f'24h Change: ${daily_change:,.2f} ({daily_change_percent:+.2f}%)'
                f'</span>'
            )
            
            # Find best performer
            best_performer = None
            best_performer_pnl = -float('inf')
            
            for holding in portfolio_data['holdings']:
                pnl_percent = holding.get('pnl_percent', 0)
                if pnl_percent > best_performer_pnl:
                    best_performer_pnl = pnl_percent
                    best_performer = holding.get('symbol', '')
            
            if best_performer:
                best_color = "#00aa00" if best_performer_pnl >= 0 else "#aa0000"
                self.best_performer_label.setText(
                    f'<span style="color: {best_color}">'
                    f'Best Performer: {best_performer} ({best_performer_pnl:+.2f}%)'
                    f'</span>'
                )
            
            # Update diversity and risk scores
            self.diversity_score_label.setText(f"Diversity Score: {portfolio_data.get('diversity_score', 0)}/100")
            self.risk_score_label.setText(f"Risk Score: {portfolio_data.get('risk_level', 'Medium')}")
            
            # Update holdings table
            holdings = portfolio_data['holdings']
            self.portfolio_table.setRowCount(len(holdings))
            
            for row, holding in enumerate(holdings):
                symbol = holding.get('symbol', '')
                name = holding.get('name', '')
                amount = holding.get('amount', 0)
                avg_cost = holding.get('avg_cost', 0)
                current_price = holding.get('current_price', 0)
                current_value = holding.get('current_value', 0)
                pnl_amount = holding.get('pnl_amount', 0)
                pnl_percent = holding.get('pnl_percent', 0)
                allocation = holding.get('allocation', 0)
                
                # Fill table
                self.portfolio_table.setItem(row, 0, QTableWidgetItem(name))
                self.portfolio_table.setItem(row, 1, QTableWidgetItem(symbol))
                self.portfolio_table.setItem(row, 2, QTableWidgetItem(f"{amount:.8f}"))
                self.portfolio_table.setItem(row, 3, QTableWidgetItem(f"${avg_cost:.4f}"))
                self.portfolio_table.setItem(row, 4, QTableWidgetItem(f"${current_price:.4f}"))
                self.portfolio_table.setItem(row, 5, QTableWidgetItem(f"${current_value:.2f}"))
                
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
                self.portfolio_table.setItem(row, 8, QTableWidgetItem(f"{allocation:.1f}%"))
            
            self.status_bar.showMessage(f"Portfolio updated: {len(holdings)} holdings")
            
        except Exception as e:
            self.status_bar.showMessage(f"Error updating portfolio: {str(e)}")
    
    def export_portfolio(self):
        """Export portfolio to CSV"""
        try:
            portfolio_data = self.portfolio.get_portfolio_summary()
            
            if not portfolio_data['holdings']:
                QMessageBox.warning(self, "No Data", "No portfolio data to export")
                return
            
            filename, _ = QFileDialog.getSaveFileName(
                self, "Export Portfolio", "portfolio.csv",
                "CSV Files (*.csv);;All Files (*)"
            )
            
            if filename:
                # Prepare data for export
                export_data = []
                for holding in portfolio_data['holdings']:
                    export_data.append({
                        'coin': holding.get('name', ''),
                        'symbol': holding.get('symbol', ''),
                        'amount': holding.get('amount', 0),
                        'avg_cost': holding.get('avg_cost', 0),
                        'current_price': holding.get('current_price', 0),
                        'current_value': holding.get('current_value', 0),
                        'pnl_amount': holding.get('pnl_amount', 0),
                        'pnl_percent': holding.get('pnl_percent', 0),
                        'allocation': holding.get('allocation', 0),
                        'last_updated': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
                
                # Add summary row
                export_data.append({
                    'coin': 'TOTAL',
                    'symbol': '',
                    'amount': '',
                    'avg_cost': '',
                    'current_price': '',
                    'current_value': portfolio_data['total_value'],
                    'pnl_amount': portfolio_data['total_pnl'],
                    'pnl_percent': portfolio_data['total_pnl_percent'],
                    'allocation': 100.0,
                    'last_updated': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                
                df = pd.DataFrame(export_data)
                df.to_csv(filename, index=False)
                
                self.status_bar.showMessage(f"Portfolio exported to {filename}")
                QMessageBox.information(self, "Export Complete", 
                    f"Portfolio successfully exported to:\n{filename}")
                
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export portfolio: {str(e)}")
    
    def refresh_sentiment(self):
        """Refresh market sentiment data"""
        try:
            self.status_bar.showMessage("Fetching market sentiment...")
            
            sentiment_data = self.sentiment.get_market_sentiment()
            
            if not sentiment_data:
                self.status_bar.showMessage("No sentiment data available")
                return
            
            # Update Fear & Greed Index
            fgi_value = sentiment_data.get('fear_greed', {}).get('value', 0)
            fgi_class = sentiment_data.get('fear_greed', {}).get('classification', '')
            fgi_timestamp = sentiment_data.get('fear_greed', {}).get('timestamp', '')
            
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
            self.fgi_value_label.setStyleSheet(f"font-size: 32px; font-weight: bold; color: {color};")
            
            self.fgi_class_label.setText(fgi_class.upper())
            self.fgi_class_label.setStyleSheet(f"font-size: 18px; color: {color};")
            
            if fgi_timestamp:
                self.fgi_timestamp_label.setText(f"Last updated: {fgi_timestamp}")
            
            self.fgi_description.setText(description)
            
            # Update sentiment analysis text
            market_analysis = sentiment_data.get('market_analysis', {})
            gainers = market_analysis.get('gainers', 0)
            losers = market_analysis.get('losers', 0)
            neutral = market_analysis.get('neutral', 0)
            
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
                extreme_greed_pct = (market_analysis.get('extreme_gainers', 0) / total_coins * 100)
                extreme_fear_pct = (market_analysis.get('extreme_losers', 0) / total_coins * 100)
                
                self.extreme_greed_label.setText(f"Extreme Greed: {extreme_greed_pct:.1f}%")
                self.extreme_fear_label.setText(f"Extreme Fear: {extreme_fear_pct:.1f}%")
            
            self.status_bar.showMessage("Sentiment data updated")
            
        except Exception as e:
            self.status_bar.showMessage(f"Error loading sentiment: {str(e)}")
            QMessageBox.warning(self, "Error", f"Failed to load sentiment data: {str(e)}")


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle("Fusion")
    
    # Create and show main window
    window = CryptoTrackerApp()
    window.show()
    
    # Start event loop
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
       