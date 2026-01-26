# src/main_app_pyqt.py

import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QPushButton, QComboBox, QHBoxLayout, QLabel,
    QHeaderView, QStatusBar, QTabWidget
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QBrush, QColor
from api_handler import ImprovedCryptoAPIHandler  # Your enhanced API handler


class CryptoTrackerApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # ----------------------------
        # Basic setup
        # ----------------------------
        self.setWindowTitle("CoinSentinel - Crypto Tracker")
        self.setGeometry(50, 50, 1200, 700)

        self.api = ImprovedCryptoAPIHandler()
        self.watchlist = []
        self.current_currency = "usd"

        # ----------------------------
        # Central widget and tabs
        # ----------------------------
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # ----------------------------
        # Tab 1: Top Coins
        # ----------------------------
        self.top_coins_table = QTableWidget()
        self.top_coins_table.setColumnCount(8)
        self.top_coins_table.setHorizontalHeaderLabels([
            "Coin", "Price", "1h %", "24h %", "7d %", "Volume", "Market Cap", "Predicted Price"
        ])
        self.top_coins_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.tabs.addTab(self.top_coins_table, "Top Coins")

        # ----------------------------
        # Tab 2: Watchlist
        # ----------------------------
        self.watchlist_table = QTableWidget()
        self.watchlist_table.setColumnCount(8)
        self.watchlist_table.setHorizontalHeaderLabels([
            "Coin", "Price", "1h %", "24h %", "7d %", "Volume", "Market Cap", "Predicted Price"
        ])
        self.watchlist_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabs.addTab(self.watchlist_table, "Watchlist")

        # ----------------------------
        # Controls
        # ----------------------------
        control_layout = QHBoxLayout()

        self.currency_selector = QComboBox()
        self.currency_selector.addItems(['usd', 'eur', 'gbp', 'jpy'])
        self.currency_selector.currentTextChanged.connect(self.change_currency)
        control_layout.addWidget(QLabel("Currency:"))
        control_layout.addWidget(self.currency_selector)

        layout.addLayout(control_layout)

        # ----------------------------
        # Status bar
        # ----------------------------
        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Fetching top coins...")

        # ----------------------------
        # Timer for auto-refresh
        # ----------------------------
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh_all)
        self.timer.start(15000)  # Refresh every 15 seconds

        # ----------------------------
        # Initial load
        # ----------------------------
        self.load_top_coins()

    # ----------------------------
    # Currency change
    # ----------------------------
    def change_currency(self, currency):
        self.current_currency = currency.lower()
        self.refresh_all()

    # ----------------------------
    # Load top coins
    # ----------------------------
    def load_top_coins(self):
        """Fetch top 50 coins and populate table."""
        self.status_bar.showMessage("Fetching top 50 coins...")
        top_coins_data = self.api.get_top_coins(limit=50, vs_currency=self.current_currency)
        self.top_coins = top_coins_data  # Keep full data for refresh
        self.populate_table(self.top_coins_table, top_coins_data)

    # ----------------------------
    # Refresh both tables
    # ----------------------------
    def refresh_all(self):
        """Refresh top coins and watchlist prices."""
        try:
            # Refresh Top Coins
            if hasattr(self, "top_coins"):
                coin_ids = [coin['id'] for coin in self.top_coins]
                prices = self.api.get_coin_price(coin_ids, self.current_currency)
                self.populate_table(self.top_coins_table, self.top_coins, prices)

            # Refresh Watchlist
            if self.watchlist:
                watchlist_prices = self.api.batch_get_prices(self.watchlist, self.current_currency)
                self.populate_watchlist_table(watchlist_prices)

            self.status_bar.showMessage("Prices updated")
        except Exception as e:
            self.status_bar.showMessage(f"Error refreshing: {e}")

    # ----------------------------
    # Populate tables
    # ----------------------------
    def populate_table(self, table, coins, prices_dict=None):
        table.setRowCount(len(coins))
        for row, coin in enumerate(coins):
            coin_id = coin.get('id', '')
            symbol = coin.get('symbol', '').upper()
            
            # Get price
            price = 0
            if not prices_dict:
                price = coin.get('current_price', 0)
            else:
                price_data = prices_dict.get(coin_id, {})
                if isinstance(price_data, dict):
                    price = price_data.get(self.current_currency, 0)
                elif isinstance(price_data, (int, float)):
                    price = price_data
                else:
                    price = coin.get('current_price', 0)
            
            # Get price changes with None handling
            change_1h = coin.get('price_change_percentage_1h_in_currency', 0)
            change_24h = coin.get('price_change_percentage_24h', 0)
            change_7d = coin.get('price_change_percentage_7d_in_currency', 0)
            
            # Convert None to 0 for formatting
            if change_1h is None:
                change_1h = 0
            if change_24h is None:
                change_24h = 0
            if change_7d is None:
                change_7d = 0
            
            # Get volume and market cap
            volume = coin.get('total_volume', 0)
            market_cap = coin.get('market_cap', 0)
            predicted_price = price * 1.01  # Placeholder ML

            # Fill table
            table.setItem(row, 0, QTableWidgetItem(symbol))
            table.setItem(row, 1, QTableWidgetItem(f"{price:,.2f}" if price else "N/A"))

            # Format percentage changes with safe formatting
            item_1h = QTableWidgetItem(f"{change_1h:+.2f}%" if change_1h is not None else "N/A")
            if change_1h is not None:
                item_1h.setForeground(QBrush(QColor('green') if change_1h >= 0 else QColor('red')))
            table.setItem(row, 2, item_1h)

            item_24h = QTableWidgetItem(f"{change_24h:+.2f}%" if change_24h is not None else "N/A")
            if change_24h is not None:
                item_24h.setForeground(QBrush(QColor('green') if change_24h >= 0 else QColor('red')))
            table.setItem(row, 3, item_24h)

            item_7d = QTableWidgetItem(f"{change_7d:+.2f}%" if change_7d is not None else "N/A")
            if change_7d is not None:
                item_7d.setForeground(QBrush(QColor('green') if change_7d >= 0 else QColor('red')))
            table.setItem(row, 4, item_7d)

            table.setItem(row, 5, QTableWidgetItem(f"{volume:,.0f}" if volume else "N/A"))
            table.setItem(row, 6, QTableWidgetItem(f"{market_cap:,.0f}" if market_cap else "N/A"))
            table.setItem(row, 7, QTableWidgetItem(f"{predicted_price:,.2f}" if predicted_price else "N/A"))

    def populate_watchlist_table(self, prices):
        table = self.watchlist_table
        table.setRowCount(len(self.watchlist))
        for row, coin in enumerate(self.watchlist):
            data = prices.get(coin, {})
            price = data.get(self.current_currency, 0)
            
            # Get price changes with None handling
            change_1h = data.get(f"{self.current_currency}_1h_change", 0)
            change_24h = data.get(f"{self.current_currency}_24h_change", 0)
            change_7d = data.get(f"{self.current_currency}_7d_change", 0)
            
            # Convert None to 0 for formatting
            if change_1h is None:
                change_1h = 0
            if change_24h is None:
                change_24h = 0
            if change_7d is None:
                change_7d = 0
            
            volume = data.get(f"{self.current_currency}_24h_vol", 0)
            market_cap = data.get(f"{self.current_currency}_market_cap", 0)
            predicted_price = price * 1.01

            table.setItem(row, 0, QTableWidgetItem(coin))
            table.setItem(row, 1, QTableWidgetItem(f"{price:,.2f}" if price else "N/A"))

            item_1h = QTableWidgetItem(f"{change_1h:+.2f}%" if change_1h is not None else "N/A")
            if change_1h is not None:
                item_1h.setForeground(QBrush(QColor('green') if change_1h >= 0 else QColor('red')))
            table.setItem(row, 2, item_1h)

            item_24h = QTableWidgetItem(f"{change_24h:+.2f}%" if change_24h is not None else "N/A")
            if change_24h is not None:
                item_24h.setForeground(QBrush(QColor('green') if change_24h >= 0 else QColor('red')))
            table.setItem(row, 3, item_24h)

            item_7d = QTableWidgetItem(f"{change_7d:+.2f}%" if change_7d is not None else "N/A")
            if change_7d is not None:
                item_7d.setForeground(QBrush(QColor('green') if change_7d >= 0 else QColor('red')))
            table.setItem(row, 4, item_7d)

            table.setItem(row, 5, QTableWidgetItem(f"{volume:,.0f}" if volume else "N/A"))
            table.setItem(row, 6, QTableWidgetItem(f"{market_cap:,.0f}" if market_cap else "N/A"))
            table.setItem(row, 7, QTableWidgetItem(f"{predicted_price:,.2f}" if predicted_price else "N/A"))


# ----------------------------
# Main entry
# ----------------------------
def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = CryptoTrackerApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()