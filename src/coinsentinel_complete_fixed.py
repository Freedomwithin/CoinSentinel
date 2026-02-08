# CRITICAL FIXES FOR COINSENTINEL
# 1. Full market table with all columns (not fallback)
# 2. Working ML predictions (not always fallback)
# 3. Proper data fetching and display

# This file contains the critical fixes to add to your existing coinsentinel_merged_3.py
# Replace the ImprovedMarketTab class with this version

"""
IMPROVED MARKET TAB - WITH FULL COLUMNS
Replace lines ~685-754 in your current file with this version
"""

class ImprovedMarketTab_Fixed(QWidget):
    """Enhanced market overview with ALL columns visible"""

    def __init__(self, api_handler):
        super().__init__()
        self.api = api_handler
        self.coins_data = []
        self.auto_refresh_enabled = False
        
        # Apply global stylesheet
        self.setStyleSheet(GLOBAL_STYLESHEET)
        
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
        header.setStyleSheet("""
            font-size: 24px;
            font-weight: 800;
            color: #ffffff;
            margin-bottom: 10px;
        """)
        layout.addWidget(header)

        # Controls
        controls_layout = QHBoxLayout()
        
        # Search
        controls_layout.addWidget(QLabel("🔍 Search:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Type coin name or symbol...")
        self.search_input.textChanged.connect(self.filter_coins)
        self.search_input.setMinimumWidth(200)
        controls_layout.addWidget(self.search_input)

        controls_layout.addSpacing(20)

        # Limit
        controls_layout.addWidget(QLabel("Show:"))
        self.limit_combo = QComboBox()
        self.limit_combo.addItems(["Top 10", "Top 20", "Top 50", "Top 100"])
        self.limit_combo.currentTextChanged.connect(self.load_coins)
        controls_layout.addWidget(self.limit_combo)

        # Currency
        controls_layout.addWidget(QLabel("Currency:"))
        self.currency_combo = QComboBox()
        self.currency_combo.addItems(["USD", "EUR", "GBP"])
        self.currency_combo.currentTextChanged.connect(self.load_coins)
        controls_layout.addWidget(self.currency_combo)

        controls_layout.addSpacing(20)

        # Refresh button
        self.refresh_btn = QPushButton("🔄 Refresh Data")
        self.refresh_btn.clicked.connect(self.load_coins)
        controls_layout.addWidget(self.refresh_btn)
        
        # Auto-refresh toggle
        self.auto_refresh_btn = QPushButton("⏸️ Auto-Refresh: OFF")
        self.auto_refresh_btn.clicked.connect(self.toggle_auto_refresh)
        controls_layout.addWidget(self.auto_refresh_btn)

        controls_layout.addStretch()
        layout.addLayout(controls_layout)

        # Status
        self.status_label = QLabel("⏳ Loading cryptocurrency data...")
        self.status_label.setStyleSheet("color: #94a3b8; font-weight: 600; margin: 5px;")
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
        """Load coins with FULL data - not fallback"""
        try:
            self.refresh_btn.setEnabled(False)
            self.refresh_btn.setText("Loading...")
            self.status_label.setText("⏳ Fetching live data from CoinGecko...")

            limit = int(self.limit_combo.currentText().split()[1])
            currency = self.currency_combo.currentText().lower()

            print(f"Fetching {limit} coins in {currency}...")
            
            # Get full market data
            coins = self.api.get_top_coins(limit=limit, vs_currency=currency)

            if coins and len(coins) > 0:
                print(f"✓ Received {len(coins)} coins with data")
                self.coins_data = coins
                self.update_table_with_full_data()
                self.status_label.setText(f"✅ Live data loaded: {len(coins)} coins")
            else:
                print("✗ No data received from API")
                self.status_label.setText("⚠️ No data returned from API - Check connection")

        except Exception as e:
            print(f"Error loading coins: {e}")
            import traceback
            traceback.print_exc()
            self.status_label.setText(f"⚠️ Error: {str(e)[:100]}")
        finally:
            self.refresh_btn.setText("🔄 Refresh Data")
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
            self.auto_refresh_btn.setStyleSheet("""
                QPushButton {
                    padding: 8px 15px;
                    background-color: #10b981;
                    color: white;
                    border-radius: 8px;
                    font-weight: 700;
                }
            """)
            self.refresh_timer.start()
            self.status_label.setText("✅ Auto-refresh enabled (updates every 60s)")
        else:
            self.auto_refresh_btn.setText("⏸️ Auto-Refresh: OFF")
            self.auto_refresh_btn.setStyleSheet("""
                QPushButton {
                    padding: 8px 15px;
                    background-color: #64748b;
                    color: white;
                    border-radius: 8px;
                    font-weight: 700;
                }
            """)
            self.refresh_timer.stop()
            self.status_label.setText("⏸️ Auto-refresh disabled")


"""
CRITICAL FIX FOR API HANDLER
Add this method to your EnhancedCryptoAPIHandler class
This ensures we request the percentage change data
"""

def get_top_coins_FIXED(self, limit=100, vs_currency="usd"):
    """Get top cryptocurrencies with ALL data fields"""
    try:
        self._rate_limit() if hasattr(self, '_rate_limit') else time.sleep(1)
        
        print(f"API: Requesting {limit} coins...")
        
        # CRITICAL: Request percentage changes for 1h, 24h, and 7d
        coins = self.cg.get_coins_markets(
            vs_currency=vs_currency,
            order="market_cap_desc",
            per_page=limit,
            page=1,
            sparkline=False,
            price_change_percentage="1h,24h,7d"  # THIS IS THE KEY!
        )
        
        print(f"API: Received {len(coins) if coins else 0} coins")
        
        # Verify we have the data
        if coins and len(coins) > 0:
            sample = coins[0]
            has_1h = 'price_change_percentage_1h_in_currency' in sample
            has_24h = 'price_change_percentage_24h_in_currency' in sample
            has_7d = 'price_change_percentage_7d_in_currency' in sample
            print(f"API: Data check - 1h: {has_1h}, 24h: {has_24h}, 7d: {has_7d}")
        
        return coins
        
    except Exception as e:
        print(f"API Error in get_top_coins: {e}")
        import traceback
        traceback.print_exc()
        return []


print("""
====================================================================
COINSENTINEL FIXES LOADED
====================================================================

TO APPLY THESE FIXES TO YOUR MAIN FILE:

1. MARKET TAB FIX (Full Columns):
   - Replace your ImprovedMarketTab class (around line 685-754)
   - With the ImprovedMarketTab_Fixed class above

2. API HANDLER FIX (Get all data):
   - In your api_handler.py file
   - Replace get_top_coins method with get_top_coins_FIXED above
   - This ensures you get 1h, 24h, and 7d percentage changes

3. PREDICTOR FIX (Stop fallback):
   - See next file for prediction fixes
   
The market tab will now show ALL columns with real data!
====================================================================
""")
