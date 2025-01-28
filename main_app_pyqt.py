import sys
import json
import csv
import datetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableView, QMessageBox, QPushButton, QLabel,
    QTabWidget, QGridLayout, QMenuBar, QAction,
    QStatusBar, QHeaderView, QComboBox, QLineEdit,
    QDoubleSpinBox, QListWidget, QDialog, QDialogButtonBox,
    QFileDialog, QInputDialog
)
from PyQt5.QtCore import Qt, QTimer, QSortFilterProxyModel, QThread, pyqtSignal
from PyQt5.QtGui import QStandardItemModel, QStandardItem
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from src.crypto_data_fetcher import CryptoDataFetcher
from src.price_predictor import PricePredictor

class DataFetcherThread(QThread):
    data_fetched = pyqtSignal(list)

    def run(self):
        data_fetcher = CryptoDataFetcher()
        data = data_fetcher.get_top_50_coins()
        self.data_fetched.emit(data)

class CryptoTrackerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Crypto Tracker")
        self.setGeometry(100, 100, 1200, 800)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.menu_bar = self.menuBar()
        file_menu = self.menu_bar.addMenu("File")
        
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        theme_menu = self.menu_bar.addMenu("Theme")
        light_theme_action = QAction("Light Theme", self)
        dark_theme_action = QAction("Dark Theme", self)
        light_theme_action.triggered.connect(lambda: self.set_theme("light"))
        dark_theme_action.triggered.connect(lambda: self.set_theme("dark"))
        theme_menu.addAction(light_theme_action)
        theme_menu.addAction(dark_theme_action)

        user_menu = self.menu_bar.addMenu("User")
        switch_user_action = QAction("Switch User", self)
        switch_user_action.triggered.connect(self.switch_user)
        user_menu.addAction(switch_user_action)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        self.tab_widget = QTabWidget()
        self.central_widget.setLayout(QVBoxLayout())
        self.central_widget.layout().addWidget(self.tab_widget)

        self.data_fetcher = CryptoDataFetcher()
        self.price_predictor = PricePredictor()
        self.portfolio = {}
        self.watchlist = set()
        self.alerts = {}
        self.currency_conversion_rates = {"USD": 1, "EUR": 0.85, "GBP": 0.75}
        self.current_currency = "USD"
        self.current_user = "default"

        self.setup_tabs()
        
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_market_table)
        self.update_timer.start(300000)  # Update every 5 minutes

        self.load_data()

    def setup_tabs(self):
        self.setup_market_tab()
        self.setup_portfolio_tab()
        self.setup_watchlist_tab()
        self.setup_comparison_tab()
        self.setup_visualization_tab()
        self.setup_prediction_tab()
        self.setup_historical_data_tab()

        self.update_market_table()

    def setup_market_tab(self):
        market_tab = QWidget()
        market_layout = QVBoxLayout()
        market_tab.setLayout(market_layout)
        
        label = QLabel("Market Overview")
        market_layout.addWidget(label)

        self.market_model = QStandardItemModel(0, 6)
        self.market_model.setHorizontalHeaderLabels(["Coin", "Price", "24h Change", "7d Change", "Market Cap", "Actions"])

        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setSourceModel(self.market_model)

        self.market_table = QTableView()
        self.market_table.setModel(self.proxy_model)
        self.market_table.setSortingEnabled(True)
        self.market_table.horizontalHeader().sectionClicked.connect(self.on_header_clicked)
        market_layout.addWidget(self.market_table)

        self.market_table.horizontalHeader().setStretchLastSection(True)
        self.market_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        filter_layout = QHBoxLayout()
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("Filter coins...")
        self.filter_input.textChanged.connect(self.filter_market_table)
        filter_layout.addWidget(self.filter_input)

        export_button = QPushButton("Export to CSV")
        export_button.clicked.connect(self.export_market_data)
        filter_layout.addWidget(export_button)

        self.advanced_filter_button = QPushButton("Advanced Filter")
        self.advanced_filter_button.clicked.connect(self.show_advanced_filter_dialog)
        filter_layout.addWidget(self.advanced_filter_button)

        self.currency_selector = QComboBox()
        self.currency_selector.addItems(self.currency_conversion_rates.keys())
        self.currency_selector.currentTextChanged.connect(self.change_currency)
        filter_layout.addWidget(self.currency_selector)

        market_layout.addLayout(filter_layout)

        self.tab_widget.addTab(market_tab, "Market Overview")

    def setup_portfolio_tab(self):
        portfolio_tab = QWidget()
        portfolio_layout = QVBoxLayout()
        portfolio_tab.setLayout(portfolio_layout)

        self.portfolio_model = QStandardItemModel(0, 4)
        self.portfolio_model.setHorizontalHeaderLabels(["Coin", "Amount", "Value", "Profit/Loss"])

        self.portfolio_table = QTableView()
        self.portfolio_table.setModel(self.portfolio_model)
        portfolio_layout.addWidget(self.portfolio_table)

        add_coin_layout = QHBoxLayout()
        self.portfolio_coin_selector = QComboBox()
        self.portfolio_amount_input = QDoubleSpinBox()
        self.portfolio_amount_input.setRange(0, 1000000)
        add_coin_button = QPushButton("Add to Portfolio")
        add_coin_button.clicked.connect(self.add_to_portfolio)

        add_coin_layout.addWidget(self.portfolio_coin_selector)
        add_coin_layout.addWidget(self.portfolio_amount_input)
        add_coin_layout.addWidget(add_coin_button)

        portfolio_layout.addLayout(add_coin_layout)

        self.tab_widget.addTab(portfolio_tab, "Portfolio")

    def setup_watchlist_tab(self):
        watchlist_tab = QWidget()
        watchlist_layout = QVBoxLayout()
        watchlist_tab.setLayout(watchlist_layout)

        self.watchlist_widget = QListWidget()
        watchlist_layout.addWidget(self.watchlist_widget)

        add_to_watchlist_layout = QHBoxLayout()
        self.watchlist_coin_selector = QComboBox()
        add_to_watchlist_button = QPushButton("Add to Watchlist")
        add_to_watchlist_button.clicked.connect(self.add_to_watchlist)

        add_to_watchlist_layout.addWidget(self.watchlist_coin_selector)
        add_to_watchlist_layout.addWidget(add_to_watchlist_button)

        watchlist_layout.addLayout(add_to_watchlist_layout)

        self.tab_widget.addTab(watchlist_tab, "Watchlist")

    def setup_comparison_tab(self):
        comparison_tab = QWidget()
        comparison_layout = QVBoxLayout()
        comparison_tab.setLayout(comparison_layout)

        self.comparison_coin1 = QComboBox()
        self.comparison_coin2 = QComboBox()
        compare_button = QPushButton("Compare")
        compare_button.clicked.connect(self.compare_coins)

        comparison_layout.addWidget(self.comparison_coin1)
        comparison_layout.addWidget(self.comparison_coin2)
        comparison_layout.addWidget(compare_button)

        self.comparison_result = QLabel()
        comparison_layout.addWidget(self.comparison_result)

        self.tab_widget.addTab(comparison_tab, "Coin Comparison")

    def setup_visualization_tab(self):
        visualization_tab = QWidget()
        visualization_layout = QVBoxLayout()
        visualization_tab.setLayout(visualization_layout)

        self.figure = plt.figure(figsize=(10, 6))
        self.canvas = FigureCanvas(self.figure)
        visualization_layout.addWidget(self.canvas)

        update_chart_button = QPushButton("Update Chart")
        update_chart_button.clicked.connect(self.update_chart)
        visualization_layout.addWidget(update_chart_button)

        self.tab_widget.addTab(visualization_tab, "Data Visualization")

    def setup_prediction_tab(self):
        prediction_tab = QWidget()
        prediction_layout = QVBoxLayout()
        prediction_tab.setLayout(prediction_layout)

        prediction_label = QLabel("Price Prediction")
        prediction_layout.addWidget(prediction_label)

        self.prediction_coin_selector = QComboBox()
        prediction_layout.addWidget(self.prediction_coin_selector)

        predict_button = QPushButton("Predict Price")
        predict_button.clicked.connect(self.predict_price)
        prediction_layout.addWidget(predict_button)

        self.prediction_result = QLineEdit()
        self.prediction_result.setReadOnly(True)
        prediction_layout.addWidget(self.prediction_result)

        self.tab_widget.addTab(prediction_tab, "Price Prediction")

    def setup_historical_data_tab(self):
        historical_data_tab = QWidget()
        historical_data_layout = QVBoxLayout()
        historical_data_tab.setLayout(historical_data_layout)

        self.historical_coin_selector = QComboBox()
        historical_data_layout.addWidget(self.historical_coin_selector)

        self.date_range_layout = QHBoxLayout()
        self.start_date_input = QLineEdit()
        self.start_date_input.setPlaceholderText("Start Date (YYYY-MM-DD)")
        self.end_date_input = QLineEdit()
        self.end_date_input.setPlaceholderText("End Date (YYYY-MM-DD)")
        self.date_range_layout.addWidget(self.start_date_input)
        self.date_range_layout.addWidget(self.end_date_input)
        historical_data_layout.addLayout(self.date_range_layout)

        self.historical_figure = plt.figure(figsize=(10, 6))
        self.historical_canvas = FigureCanvas(self.historical_figure)
        historical_data_layout.addWidget(self.historical_canvas)

        fetch_historical_data_button = QPushButton("Fetch Historical Data")
        fetch_historical_data_button.clicked.connect(self.fetch_historical_data)
        historical_data_layout.addWidget(fetch_historical_data_button)

        self.tab_widget.addTab(historical_data_tab, "Historical Data")

    def fetch_historical_data(self):
        coin = self.historical_coin_selector.currentText()
        start_date = self.start_date_input.text()
        end_date = self.end_date_input.text()

        # Dummy data for the sake of example
        dates = [datetime.date.today() - datetime.timedelta(days=i) for i in range(30)]
        prices = np.random.uniform(100, 500, size=30)

        self.historical_figure.clear()
        ax = self.historical_figure.add_subplot(111)
        ax.plot(dates, prices, marker='o', linestyle='-')
        ax.set_title(f'Historical Prices for {coin}')
        ax.set_xlabel('Date')
        ax.set_ylabel('Price')
        self.historical_canvas.draw()

    def update_market_table(self):
        self.data_fetcher_thread = DataFetcherThread()
        self.data_fetcher_thread.data_fetched.connect(self.on_data_fetched)
        self.data_fetcher_thread.start()

    def on_data_fetched(self, data):
        self.market_model.setRowCount(len(data))
        for row, coin in enumerate(data):
            self.market_model.setItem(row, 0, QStandardItem(coin['symbol'].upper()))
            self.market_model.setItem(row, 1, QStandardItem(f"${coin['current_price'] * self.currency_conversion_rates[self.current_currency]:.2f} {self.current_currency}"))
            self.market_model.setItem(row, 2, QStandardItem(f"{coin['price_change_percentage_24h']:.2f}%"))
            self.market_model.setItem(row, 3, QStandardItem(f"{coin['price_change_percentage_7d_in_currency']:.2f}%"))
            self.market_model.setItem(row, 4, QStandardItem(f"${coin['market_cap'] * self.currency_conversion_rates[self.current_currency]:,.0f} {self.current_currency}"))
            
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            add_to_portfolio_button = QPushButton("Add to Portfolio")
            add_to_watchlist_button = QPushButton("Add to Watchlist")
            set_alert_button = QPushButton("Set Alert")
            add_to_portfolio_button.clicked.connect(lambda _, c=coin['symbol']: self.add_to_portfolio_dialog(c))
            add_to_watchlist_button.clicked.connect(lambda _, c=coin['symbol']: self.add_to_watchlist(c))
            set_alert_button.clicked.connect(lambda _, c=coin['symbol']: self.show_set_alert_dialog(c))
            actions_layout.addWidget(add_to_portfolio_button)
            actions_layout.addWidget(add_to_watchlist_button)
            actions_layout.addWidget(set_alert_button)
            self.market_table.setIndexWidget(self.market_model.index(row, 5), actions_widget)
        
        self.status_bar.showMessage("Market data updated")
        self.update_coin_selectors(data)
        self.update_portfolio()
        self.update_watchlist()

    def update_coin_selectors(self, data):
        coin_symbols = [coin['symbol'].upper() for coin in data]
        self.portfolio_coin_selector.clear()
        self.portfolio_coin_selector.addItems(coin_symbols)
        self.watchlist_coin_selector.clear()
        self.watchlist_coin_selector.addItems(coin_symbols)
        self.comparison_coin1.clear()
        self.comparison_coin1.addItems(coin_symbols)
        self.comparison_coin2.clear()
        self.comparison_coin2.addItems(coin_symbols)
        self.prediction_coin_selector.clear()
        self.prediction_coin_selector.addItems(coin_symbols)
        self.historical_coin_selector.clear()
        self.historical_coin_selector.addItems(coin_symbols)

    def on_header_clicked(self, logical_index):
        if logical_index in [1, 2, 3, 4]:  # Numeric columns
            self.proxy_model.setSortRole(Qt.UserRole)
            for row in range(self.market_model.rowCount()):
                item = self.market_model.item(row, logical_index)
                item.setData(float(item.text().replace('$', '').replace('%', '').replace(',', '').replace(self.current_currency, '').strip()), Qt.UserRole)
        else:
            self.proxy_model.setSortRole(Qt.DisplayRole)
        
        self.market_table.sortByColumn(logical_index, self.market_table.horizontalHeader().sortIndicatorOrder())

    def filter_market_table(self):
        filter_text = self.filter_input.text().lower()
        for row in range(self.market_model.rowCount()):
            coin_name = self.market_model.item(row, 0).text().lower()
            self.market_table.setRowHidden(row, filter_text not in coin_name)

    def show_advanced_filter_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Advanced Filter")
        layout = QVBoxLayout()

        self.market_cap_filter_input = QLineEdit()
        self.market_cap_filter_input.setPlaceholderText("Market Cap >")
        layout.addWidget(self.market_cap_filter_input)

        self.price_filter_input = QLineEdit()
        self.price_filter_input.setPlaceholderText("Price <")
        layout.addWidget(self.price_filter_input)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)

        dialog.setLayout(layout)

        if dialog.exec_() == QDialog.Accepted:
            self.apply_advanced_filters()

    def apply_advanced_filters(self):
        market_cap_filter = self.market_cap_filter_input.text()
        price_filter = self.price_filter_input.text()

        for row in range(self.market_model.rowCount()):
            market_cap = float(self.market_model.item(row, 4).text().replace('$', '').replace(',', '').replace(self.current_currency, '').strip())
            price = float(self.market_model.item(row, 1).text().replace('$', '').replace(self.current_currency, '').strip())
            show_row = True

            if market_cap_filter and market_cap <= float(market_cap_filter):
                show_row = False
            if price_filter and price >= float(price_filter):
                show_row = False

            self.market_table.setRowHidden(row, not show_row)

    def add_to_portfolio_dialog(self, coin):
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Add {coin} to Portfolio")
        layout = QVBoxLayout()

        amount_input = QDoubleSpinBox()
        amount_input.setRange(0, 1000000)
        layout.addWidget(QLabel(f"Enter amount of {coin}:"))
        layout.addWidget(amount_input)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)

        dialog.setLayout(layout)

        if dialog.exec_() == QDialog.Accepted:
            amount = amount_input.value()
            self.add_to_portfolio(coin, amount)

    def add_to_portfolio(self, coin, amount):
        if coin in self.portfolio:
            self.portfolio[coin] += amount
        else:
            self.portfolio[coin] = amount
        self.update_portfolio()
        self.save_data()

    def update_portfolio(self):
        self.portfolio_model.setRowCount(0)
        total_value = 0
        for coin, amount in self.portfolio.items():
            price = self.get_coin_price(coin)
            if price:
                value = amount * price
                total_value += value
                row = [
                    QStandardItem(coin),
                    QStandardItem(f"{amount:.4f}"),
                    QStandardItem(f"${value:.2f} {self.current_currency}"),
                    QStandardItem("N/A")  # Profit/Loss placeholder
                ]
                self.portfolio_model.appendRow(row)
        
        self.status_bar.showMessage(f"Total Portfolio Value: ${total_value:.2f} {self.current_currency}")
        self.calculate_portfolio_performance()

    def calculate_portfolio_performance(self):
        total_invested = sum([self.portfolio[coin] * self.get_coin_purchase_price(coin) for coin in self.portfolio])
        total_value = sum([self.portfolio[coin] * self.get_coin_price(coin) for coin in self.portfolio])
        profit_loss = total_value - total_invested
        roi = (profit_loss / total_invested) * 100 if total_invested else 0
        self.status_bar.showMessage(f"Total Portfolio Value: ${total_value:.2f} {self.current_currency}, Profit/Loss: ${profit_loss:.2f}, ROI: {roi:.2f}%")

    def get_coin_purchase_price(self, coin):
        # Dummy purchase price for the sake of example
        return 100.0  # Replace with actual purchase price retrieval logic

    def add_to_watchlist(self, coin):
        if coin not in self.watchlist:
            self.watchlist.add(coin)
            self.update_watchlist()
            self.save_data()

        if coin not in self.alerts:
            self.alerts[coin] = None

    def update_watchlist(self):
        self.watchlist_widget.clear()
        for coin in sorted(self.watchlist):
            price = self.get_coin_price(coin)
            if price:
                self.watchlist_widget.addItem(f"{coin}: ${price:.2f} {self.current_currency}")

    def show_set_alert_dialog(self, coin):
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Set Alert for {coin}")
        layout = QVBoxLayout()

        self.alert_price_input = QLineEdit()
        self.alert_price_input.setPlaceholderText("Alert Price")
        layout.addWidget(self.alert_price_input)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(lambda: self.set_alert(coin, self.alert_price_input.text()))
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)

        dialog.setLayout(layout)
        dialog.exec_()

    def set_alert(self, coin, price):
        self.alerts[coin] = float(price)
        self.status_bar.showMessage(f"Alert set for {coin} at ${price} {self.current_currency}")

    def check_alerts(self):
        for coin, alert_price in self.alerts.items():
            if alert_price is not None:
                current_price = self.get_coin_price(coin)
                if current_price and current_price >= alert_price:
                    QMessageBox.information(self, "Price Alert", f"{coin} has reached ${alert_price} {self.current_currency}")
                    self.alerts[coin] = None

    def get_coin_price(self, coin):
        for row in range(self.market_model.rowCount()):
            if self.market_model.item(row, 0).text() == coin:
                return float(self.market_model.item(row, 1).text().replace('$', '').replace(self.current_currency, '').strip())
        return None

    def compare_coins(self):
        coin1 = self.comparison_coin1.currentText()
        coin2 = self.comparison_coin2.currentText()
        price1 = self.get_coin_price(coin1)
        price2 = self.get_coin_price(coin2)
        if price1 and price2:
            ratio = price1 / price2
            self.comparison_result.setText(f"1 {coin1} = {ratio:.4f} {coin2}")
        else:
            self.comparison_result.setText("Unable to compare. Make sure both coins are in the market data.")

    def update_chart(self):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        coins = [self.market_model.item(row, 0).text() for row in range(min(10, self.market_model.rowCount()))]
        market_caps = [float(self.market_model.item(row, 4).text().replace('$', '').replace(',', '').replace(self.current_currency, '').strip()) for row in range(min(10, self.market_model.rowCount()))]
        
        ax.pie(market_caps, labels=coins, autopct='%1.1f%%', startangle=90)
        ax.axis('equal')
        ax.set_title('Top 10 Cryptocurrencies by Market Cap')
        
        self.canvas.draw()

    def predict_price(self):
        selected_coin = self.prediction_coin_selector.currentText()
        historical_data = self.data_fetcher.get_historical_data(selected_coin, days=7)
        
        if historical_data:
            if len(historical_data) < 8:
                self.prediction_result.setText(f"Insufficient data for {selected_coin}. Need at least 8 data points.")
                return
            
            predicted_price, percentage_change = self.price_predictor.predict_next_price(np.array(historical_data))
            if predicted_price is not None:
                self.prediction_result.setText(f"Predicted price for {selected_coin}: ${predicted_price:.2f} {self.current_currency}\n"
                                               f"Percentage change: {percentage_change:.2f}%")
            else:
                self.prediction_result.setText(f"Unable to make prediction for {selected_coin}")
        else:
            self.prediction_result.setText(f"Unable to fetch historical data for {selected_coin}")

    def export_market_data(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Export Market Data", "", "CSV Files (*.csv)")
        if filename:
            with open(filename, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["Coin", "Price", "24h Change", "7d Change", "Market Cap"])
                for row in range(self.market_model.rowCount()):
                    writer.writerow([
                        self.market_model.item(row, 0).text(),
                        self.market_model.item(row, 1).text(),
                        self.market_model.item(row, 2).text(),
                        self.market_model.item(row, 3).text(),
                        self.market_model.item(row, 4).text()
                    ])
            self.status_bar.showMessage(f"Market data exported to {filename}")

    def set_theme(self, theme):
        if theme == "light":
            self.setStyleSheet("")
        elif theme == "dark":
            self.setStyleSheet("""
                QWidget { background-color: #2b2b2b; color: #ffffff; }
                QTableView { gridline-color: #3a3a3a; }
                QHeaderView::section { background-color: #3a3a3a; }
                QPushButton { background-color: #3a3a3a; border: 1px solid #5a5a5a; }
                QLineEdit, QComboBox, QDoubleSpinBox { background-color: #3a3a3a; border: 1px solid #5a5a5a; }
                QTabWidget::pane { border-top: 2px solid #5a5a5a; }
                QHeaderView { background-color: #3a3a3a; border: 1px solid #5a5a5a; }
                QHeaderView::section { background-color: #4a4a4a; border: 1px solid #5a5a5a; }
                QListWidget { background-color: #2b2b2b; border: 1px solid #5a5a5a; }
                QDialog { background-color: #2b2b2b; color: #ffffff; }
                QMessageBox { background-color: #2b2b2b; color: #ffffff; }
            """)

    def save_data(self):
        data = {
            "portfolio": self.portfolio,
            "watchlist": list(self.watchlist),
            "alerts": self.alerts,
            "current_currency": self.current_currency,
            "current_user": self.current_user
        }
        with open(f"{self.current_user}_crypto_tracker_data.json", "w") as f:
            json.dump(data, f)

    def load_data(self):
        try:
            with open(f"{self.current_user}_crypto_tracker_data.json", "r") as f:
                data = json.load(f)
                self.portfolio = data.get("portfolio", {})
                self.watchlist = set(data.get("watchlist", []))
                self.alerts = data.get("alerts", {})
                self.current_currency = data.get("current_currency", "USD")
                self.currency_selector.setCurrentText(self.current_currency)
        except FileNotFoundError:
            pass

    def closeEvent(self, event):
        self.save_data()
        self.update_timer.stop()
        super().closeEvent(event)

    def switch_user(self):
        username, ok = QInputDialog.getText(self, 'Switch User', 'Enter username:')
        if ok and username:
            self.current_user = username
            self.load_data()
            self.update_market_table()
            self.status_bar.showMessage(f"Switched to user: {username}")

    def change_currency(self, currency):
        self.current_currency = currency
        self.update_market_table()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CryptoTrackerApp()
    window.show()
    sys.exit(app.exec_()) 