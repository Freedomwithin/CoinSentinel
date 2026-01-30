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
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; margin: 10px; color: #2c3e50;")
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
        self.fgi_value_label.setStyleSheet("font-size: 48px; font-weight: bold; margin: 10px;")
        
        self.fgi_class_label = QLabel("")
        self.fgi_class_label.setStyleSheet("font-size: 24px; font-weight: bold; margin: 10px;")
        
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
            (75, 100, "Extreme Greed", "#2ecc71")
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
        self.fgi_timestamp.setStyleSheet("color: #7f8c8d; font-size: 11px; margin: 5px;")
        
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
        self.gainers_losers_chart.setStyleSheet("border: 1px solid #ddd; background-color: white;")
        layout.addWidget(self.gainers_losers_chart, 0, 0, 2, 1)
        
        # Market statistics
        stats_widget = QWidget()
        stats_layout = QVBoxLayout()
        
        self.gainers_count = QLabel("Gainers (24h): 0")
        self.gainers_count.setStyleSheet("font-size: 14px; font-weight: bold; color: #27ae60;")
        
        self.losers_count = QLabel("Losers (24h): 0")
        self.losers_count.setStyleSheet("font-size: 14px; font-weight: bold; color: #e74c3c;")
        
        self.neutral_count = QLabel("Neutral (24h): 0")
        self.neutral_count.setStyleSheet("font-size: 14px; font-weight: bold; color: #7f8c8d;")
        
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
        """Create analysis and recommendations panel"""
        panel = QGroupBox("Market Analysis & Trading Recommendations")
        layout = QVBoxLayout()
        
        self.analysis_text = QTextEdit()
        self.analysis_text.setReadOnly(True)
        self.analysis_text.setMinimumHeight(200)
        self.analysis_text.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 1px solid #ddd;
                border-radius: 3px;
                padding: 10px;
                font-size: 13px;
                line-height: 1.4;
            }
        """)
        
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
            fgi = sentiment_data.get('fear_greed', {})
            fgi_value = fgi.get('value', 50)
            fgi_class = fgi.get('classification', 'Neutral')
            
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
            self.fgi_value_label.setStyleSheet(f"""
                font-size: 48px; 
                font-weight: bold; 
                margin: 10px; 
                color: {color};
                background-color: {bg_color};
                padding: 10px;
                border-radius: 5px;
            """)
            
            self.fgi_class_label.setText(fgi_class.upper())
            self.fgi_class_label.setStyleSheet(f"font-size: 24px; font-weight: bold; margin: 10px; color: {color};")
            
            # Update description
            descriptions = {
                'extreme fear': "Investors are extremely fearful. This could indicate a buying opportunity for long-term investors.",
                'fear': "Market sentiment is fearful. Consider cautious accumulation.",
                'neutral': "Market sentiment is balanced. Good time for strategic entries.",
                'greed': "Investors are becoming greedy. Consider taking some profits.",
                'extreme greed': "Market is extremely greedy. High risk of correction. Consider reducing exposure."
            }
            
            self.fgi_description.setText(descriptions.get(fgi_class.lower(), 
                f"Fear & Greed Index at {fgi_value}/100 indicating {fgi_class} sentiment."))
            
            timestamp = fgi.get('timestamp', '')
            if timestamp:
                self.fgi_timestamp.setText(f"Last updated: {timestamp}")
            
            # Update market indicators
            market_analysis = sentiment_data.get('market_analysis', {})
            
            # Social sentiment (simulated)
            social_score = market_analysis.get('social_sentiment', 50)
            social_text = self.get_sentiment_text(social_score)
            self.social_sentiment_label.setText(social_text)
            self.set_sentiment_color(self.social_sentiment_label, social_score)
            
            # Market momentum
            momentum = market_analysis.get('momentum', 50)
            momentum_text = self.get_momentum_text(momentum)
            self.momentum_label.setText(momentum_text)
            self.set_sentiment_color(self.momentum_label, momentum)
            
            # Volume trend
            volume_trend = market_analysis.get('volume_trend', 50)
            volume_text = self.get_trend_text(volume_trend)
            self.volume_trend_label.setText(volume_text)
            self.set_sentiment_color(self.volume_trend_label, volume_trend)
            
            # Volatility
            volatility = market_analysis.get('volatility', 50)
            volatility_text = self.get_volatility_text(volatility)
            self.volatility_label.setText(volatility_text)
            self.set_sentiment_color(self.volatility_label, volatility, inverse=True)
            
            # Update market statistics
            gainers = market_analysis.get('gainers', 0)
            losers = market_analysis.get('losers', 0)
            neutral = market_analysis.get('neutral', 0)
            extreme = market_analysis.get('extreme_moves', 0)
            
            self.gainers_count.setText(f"Gainers (24h): {gainers}")
            self.losers_count.setText(f"Losers (24h): {losers}")
            self.neutral_count.setText(f"Neutral (24h): {neutral}")
            self.extreme_moves.setText(f"Extreme Moves (>10%): {extreme}")
            
            # Update top coins
            top_gainers = market_analysis.get('top_gainers', [])
            top_losers = market_analysis.get('top_losers', [])
            
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
        else:
            return "Very Low ⚪"
    
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
            categories = ['Gainers', 'Losers', 'Neutral']
            values = [gainers, losers, neutral]
            colors = ['#27ae60', '#e74c3c', '#95a5a6']
            
            # Create bar chart
            bars = ax.bar(categories, values, color=colors, alpha=0.8)
            
            # Add value labels
            for bar, value in zip(bars, values):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{value}', ha='center', va='bottom',
                       fontsize=10, fontweight='bold')
            
##Note to le chat to a.i these may need to be fixed

            # Format chart
            ax.set_ylabel('Count', fontsize=9)
            ax.set_title('Market Distribution (24h)', fontsize=10, fontweight='bold')
            ax.grid(True, alpha=0.3, linestyle='--', axis='y')
            
            # Remove top and right spines
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            
            # Tight layout
            fig.tight_layout()
            
            # Save to buffer
            from io import BytesIO
            buf = BytesIO()
            fig.savefig(buf, format='png', dpi=100, bbox_inches='tight')
            buf.seek(0)
            
            # Create QPixmap from buffer
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
        fgi = sentiment_data.get('fear_greed', {})
        market_analysis = sentiment_data.get('market_analysis', {})
        
        fgi_value = fgi.get('value', 50)
        fgi_class = fgi.get('classification', 'neutral')
        
        gainers = market_analysis.get('gainers', 0)
        losers = market_analysis.get('losers', 0)
        neutral = market_analysis.get('neutral', 0)
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
        analysis += f"Current phase: {self.get_market_phase(fgi_value, gainer_percentage)}\n"
        analysis += "Typical cycle: Fear → Neutral → Greed → Extreme Greed → Correction\n"
        
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
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; margin: 10px; color: #2c3e50;")
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
        self.holdings_table.setHorizontalHeaderLabels([
            "Coin", "Symbol", "Amount", "Avg Cost", "Current Price", 
            "Current Value", "P/L ($)", "P/L (%)", "Allocation %", "Actions"
        ])
        
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
        self.transaction_table.setHorizontalHeaderLabels([
            "Date", "Type", "Coin", "Amount", "Price", "Total", "Status"
        ])
        
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
        self.total_value_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
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
        self.quick_add_button.setStyleSheet("""
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
        """)
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
                name = coin.get('name', 'Unknown')
                symbol = coin.get('symbol', '').upper()
                price = coin.get('current_price', 0)
                
                item_text = f"{name} ({symbol}) - ${price:,.4f}"
                item = QListWidgetItem(item_text)
                item.setData(Qt.UserRole, coin['id'])
                self.coin_list.addItem(item)
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load market coins: {str(e)}")
    
    def search_coins(self):
        """Filter coins based on search"""
        search_text = self.search_input.text().lower()
        
        if not search_text:
            self.load_market_coins()
            return
        
        self.coin_list.clear()
        
        for coin in self.coins_data:
            name = coin.get('name', '').lower()
            symbol = coin.get('symbol', '').lower()
            
            if search_text in name or search_text in symbol:
                item_text = f"{coin['name']} ({coin['symbol'].upper()}) - ${coin['current_price']:,.4f}"
                item = QListWidgetItem(item_text)
                item.setData(Qt.UserRole, coin['id'])
                self.coin_list.addItem(item)
    
    def select_coin(self, item):
        """Select coin from list and open transaction dialog"""
        coin_id = item.data(Qt.UserRole)
        
        # Find coin data
        coin_data = None
        for coin in self.coins_data:
            if coin['id'] == coin_id:
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
        
        info_layout.addRow("Coin:", QLabel(coin_data['name']))
        info_layout.addRow("Symbol:", QLabel(coin_data['symbol'].upper()))
        info_layout.addRow("Current Price:", QLabel(f"${coin_data['current_price']:,.4f}"))
        
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
        price_input.setValue(coin_data['current_price'])
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
                    coin_id=coin_data['id'],
                    coin_name=coin_data['name'],
                    transaction_type=type_combo.currentText().lower(),
                    amount=amount_input.value(),
                    price=price_input.value(),
                    date=date_input.text()
                )
                
                QMessageBox.information(self, "Success", 
                    f"Added {amount_input.value()} {coin_data['symbol'].upper()} to portfolio!")
                
                self.refresh_portfolio()
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to add transaction: {str(e)}")        

## Part 3 to merge in the right spot note to le chat

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
        self.tabs.addTab(EnhancedPredictionTab(self.api, self.predictor), "AI Predictions")
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