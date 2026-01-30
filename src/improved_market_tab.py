from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QComboBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QBrush, QColor


class ImprovedMarketTab(QWidget):
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
            print("Fetched coins:", coins)

            if coins and len(coins) > 0:
                self.coins_data = coins
                self.update_table_with_real_data()
                self.status_label.setText(f"✅ Live data loaded: {len(coins)} coins")
            else:
                self.status_label.setText("⚠️ No data returned from API")
                self.show_sample_data()
        except Exception as e:
            print("Error loading coins:", e)
            self.status_label.setText(f"⚠️ Error: {str(e)[:50]}... - Using sample data")
            self.show_sample_data()
        finally:
            self.refresh_btn.setText("🔄 Refresh Data")
            self.refresh_btn.setEnabled(True)
            self.table.repaint()
            self.layout().update()

    def update_table_with_real_data(self):
        if not self.coins_data:
            print("No coins data to update table")
            return

        self.table.setRowCount(len(self.coins_data))

        for row, coin in enumerate(self.coins_data):
            rank = coin.get("market_cap_rank", row + 1)
            name = coin.get("name", "Unknown")
            symbol = coin.get("symbol", "").upper()
            price = coin.get("current_price", 0)
            change_24h = coin.get("price_change_percentage_24h_in_currency", 0)
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
        print("Table updated")

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
        print("Sample data loaded")

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
