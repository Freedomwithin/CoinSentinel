import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

from src.api_handler import CryptoAPIHandler
from src.portfolio_tracker import PortfolioTracker
from src.sentiment_tracker import SentimentTracker
from src.price_predictor import PricePredictor
from src.notification_manager import NotificationManager

class CryptoTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Crypto Tracker")
        self.root.geometry("1400x900")

        # Initialize components
        self.api_handler = CryptoAPIHandler()
        self.portfolio_tracker = PortfolioTracker()
        self.sentiment_tracker = SentimentTracker()
        self.price_predictor = PricePredictor()
        self.notification_manager = NotificationManager()

        # Create notebook for tabs
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill='both')

        # Create tabs
        self.create_market_overview_tab()
        self.create_portfolio_tab()
        self.create_sentiment_tab()
        self.create_prediction_tab()
        self.create_alerts_tab()

    def create_market_overview_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Market Overview")
        
        # Fetch top coins
        try:
            top_coins = self.api_handler.get_top_coins()
            
            # Create Treeview with dynamic sorting
            columns = [
                'symbol', 
                'current_price', 
                'market_cap', 
                'price_change_percentage_24h'
            ]
            
            tree = ttk.Treeview(tab, columns=columns, show='headings')
            
            # Configure columns with sorting
            for col in columns:
                # Heading with custom sorting
                tree.heading(
                    col, 
                    text=col.replace('_', ' ').title(), 
                    command=lambda c=col: self.sort_treeview(tree, c, False)
                )
                tree.column(col, width=100, anchor='center')
            
            # Populate data
            for coin in top_coins:
                tree.insert('', 'end', values=[
                    coin.get('symbol', 'N/A').upper(), 
                    f"${coin.get('current_price', 'N/A'):.2f}", 
                    f"${coin.get('market_cap', 'N/A'):,.0f}", 
                    f"{coin.get('price_change_percentage_24h', 'N/A'):.2f}%"
                ])
            
            # Add scrollbar
            scrollbar = ttk.Scrollbar(tab, orient=tk.VERTICAL, command=tree.yview)
            tree.configure(yscroll=scrollbar.set)
            
            tree.pack(side=tk.LEFT, fill='both', expand=True)
            scrollbar.pack(side=tk.RIGHT, fill='y')
            
            # Search functionality
            search_frame = ttk.Frame(tab)
            search_frame.pack(fill='x', padx=10, pady=5)
            
            ttk.Label(search_frame, text="Search Coin:").pack(side=tk.LEFT)
            search_entry = ttk.Entry(search_frame, width=20)
            search_entry.pack(side=tk.LEFT, padx=5)
            
            def search_coins():
                search_term = search_entry.get().upper()
                
                # Clear current view
                for item in tree.get_children():
                    tree.delete(item)
                
                # Repopulate with filtered results
                for coin in top_coins:
                    if search_term in coin.get('symbol', '').upper():
                        tree.insert('', 'end', values=[
                            coin.get('symbol', 'N/A').upper(), 
                            f"${coin.get('current_price', 'N/A'):.2f}", 
                            f"${coin.get('market_cap', 'N/A'):,.0f}", 
                            f"{coin.get('price_change_percentage_24h', 'N/A'):.2f}%"
                        ])
            
            search_button = ttk.Button(search_frame, text="Search", command=search_coins)
            search_button.pack(side=tk.LEFT, padx=5)
            
            # Reset button
            def reset_view():
                # Clear current view
                for item in tree.get_children():
                    tree.delete(item)
                
                # Repopulate with all coins
                for coin in top_coins:
                    tree.insert('', 'end', values=[
                        coin.get('symbol', 'N/A').upper(), 
                        f"${coin.get('current_price', 'N/A'):.2f}", 
                        f"${coin.get('market_cap', 'N/A'):,.0f}", 
                        f"{coin.get('price_change_percentage_24h', 'N/A'):.2f}%"
                    ])
            
            reset_button = ttk.Button(search_frame, text="Reset", command=reset_view)
            reset_button.pack(side=tk.LEFT, padx=5)
        
        except Exception as e:
            error_label = ttk.Label(tab, text=f"Error loading market data: {str(e)}")
            error_label.pack(padx=10, pady=10)

    def sort_treeview(self, tree, col, reverse):
        """
        Sort treeview columns
        
        Args:
            tree (ttk.Treeview): Treeview to sort
            col (str): Column to sort
            reverse (bool): Sort direction
        """
        # Extract data
        data = [(tree.set(child, col), child) for child in tree.get_children('')]
        
        # Convert to appropriate type for sorting
        def convert_numeric(val):
            try:
                # Remove $ and % signs, convert to float
                return float(val.replace('$', '').replace('%', '').replace(',', ''))
            except ValueError:
                return val
        
        # Sort data
        data.sort(key=lambda x: convert_numeric(x[0]), reverse=reverse)
        
        # Rearrange items
        for index, (val, child) in enumerate(data):
            tree.move(child, '', index)
        
        # Toggle sort direction
        tree.heading(col, command=lambda: self.sort_treeview(tree, col, not reverse))

    def create_portfolio_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Portfolio")
        
        portfolio_frame = ttk.Frame(tab)
        portfolio_frame.pack(padx=10, pady=10, fill='both', expand=True)

        # Entry Fields
        entries = {}
        for label in ["Coin Symbol", "Amount", "Purchase Price"]:
            ttk.Label(portfolio_frame, text=label).pack()
            entry = ttk.Entry(portfolio_frame)
            entry.pack()
            entries[label.lower().replace(" ", "_")] = entry

        def add_holding():
            try:
                symbol = entries['coin_symbol'].get().upper()
                amount = float(entries['amount'].get())
                price = float(entries['purchase_price'].get())
                
                self.portfolio_tracker.add_holding(symbol, amount, price)
                messagebox.showinfo("Success", f"Added {amount} {symbol}")
                
                # Clear entries
                for entry in entries.values():
                    entry.delete(0, tk.END)
                
                refresh_portfolio()
            except ValueError:
                messagebox.showerror("Error", "Invalid input")

        ttk.Button(portfolio_frame, text="Add Holding", command=add_holding).pack(pady=10)

        # Portfolio Treeview
        columns = ['Symbol', 'Amount', 'Purchase Price', 'Current Value', 'Profit/Loss %']
        self.portfolio_tree = ttk.Treeview(portfolio_frame, columns=columns, show='headings')
        
        for col in columns:
            self.portfolio_tree.heading(col, text=col)
            self.portfolio_tree.column(col, width=100, anchor='center')
        
        self.portfolio_tree.pack(expand=True, fill='both')

        def refresh_portfolio():
            # Clear existing items
            for i in self.portfolio_tree.get_children():
                self.portfolio_tree.delete(i)
            
            # Fetch current prices
            top_coins = {coin['symbol'].upper(): coin['current_price'] 
                         for coin in self.api_handler.get_top_coins()}
            
            # Update and display portfolio
            updated_portfolio = self.portfolio_tracker.update_portfolio_value(top_coins)
            
            for symbol, details in updated_portfolio.items():
                self.portfolio_tree.insert('', 'end', values=[
                    symbol,
                    f"{details['amount']:.4f}",
                    f"${details['purchase_price']:.2f}",
                    f"${details['current_value']:.2f}",
                    f"{details['profit_loss_percentage']:.2f}%"
                ])

        ttk.Button(portfolio_frame, text="Refresh Portfolio", command=refresh_portfolio).pack(pady=10)

    def create_sentiment_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Sentiment")
        
        # Sentiment Symbol Entry
        ttk.Label(tab, text="Enter Crypto Symbol").pack()
        symbol_entry = ttk.Entry(tab)
        symbol_entry.pack()

        sentiment_display = tk.Text(tab, height=10, width=50)
        sentiment_display.pack(pady=10)

        def check_sentiment():
            symbol = symbol_entry.get().upper()
            sentiment = self.sentiment_tracker.get_crypto_sentiment(symbol)
            
            sentiment_display.delete(1.0, tk.END)
            if sentiment:
                sentiment_display.insert(tk.END, f"Sentiment for {symbol}:\n")
                sentiment_display.insert(tk.END, f"Positive Score: {sentiment['positive_score']}\n")
                sentiment_display.insert(tk.END, f"Negative Score: {sentiment['negative_score']}\n")
                sentiment_display.insert(tk.END, f"Overall Sentiment: {sentiment['overall_sentiment']}")
            else:
                sentiment_display.insert(tk.END, "Could not fetch sentiment")

        ttk.Button(tab, text="Check Sentiment", command=check_sentiment).pack()

    def create_prediction_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Price Prediction")
        
        # Coin ID mapping
        coin_id_map = {
            'BTC': 'bitcoin',
            'ETH': 'ethereum',
            'BNB': 'binancecoin',
            'DOGE': 'dogecoin',
            'XRP': 'ripple'
        }
        
        # Prediction Symbol Entry
        ttk.Label(tab, text="Enter Crypto Symbol").pack()
        symbol_entry = ttk.Entry(tab)
        symbol_entry.pack()

        prediction_display = tk.Text(tab, height=10, width=50)
        prediction_display.pack(pady=10)

        def predict_price():
            symbol = symbol_entry.get().upper()
            try:
                # Normalize symbol
                coin_id = coin_id_map.get(symbol, symbol.lower())
                
                # Fetch historical data
                historical_data = self.api_handler.get_historical_prices(
                    coin_id=coin_id,
                    days=30
                )
                
                # Extract prices
                prices = [price[1] for price in historical_data['prices']]
                
                # Validate price data
                if len(prices) < 30:
                    prediction_display.delete(1.0, tk.END)
                    prediction_display.insert(tk.END, f"Insufficient data for {symbol}")
                    return
                
                # Predict price using machine learning
                predicted_price = self.price_predictor.predict_next_price(np.array(prices))
                
                # Current price for context
                current_price = prices[-1]
                
                prediction_display.delete(1.0, tk.END)
                prediction_display.insert(tk.END, f"Prediction for {symbol}:\n")
                prediction_display.insert(tk.END, f"Current Price: ${current_price:.2f}\n")
                prediction_display.insert(tk.END, f"Predicted Next Price: ${predicted_price:.2f}\n")
                
                # Calculate percentage change
                change_percentage = ((predicted_price - current_price) / current_price) * 100
                prediction_display.insert(tk.END, f"Predicted Change: {change_percentage:.2f}%")
            
            except Exception as e:
                prediction_display.delete(1.0, tk.END)
                prediction_display.insert(tk.END, f"Prediction Error: {str(e)}")

        ttk.Button(tab, text="Predict Price", command=predict_price).pack()

    def create_alerts_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Alerts")
        
        # Alert Setup Widgets
        ttk.Label(tab, text="Cryptocurrency").pack()
        symbol_entry = ttk.Entry(tab)
        symbol_entry.pack()

        ttk.Label(tab, text="Price Threshold").pack()
        price_entry = ttk.Entry(tab)
        price_entry.pack()

        ttk.Label(tab, text="Alert Type").pack()
        alert_type = ttk.Combobox(tab, values=['Above', 'Below'])
        alert_type.pack()

        alerts_display = tk.Text(tab, height=10, width=50)
        alerts_display.pack(pady=10)

        def set_alert():
            symbol = symbol_entry.get().upper()
            try:
                price = float(price_entry.get())
                alert_type_val = alert_type.get()
                
                alerts_display.delete(1.0, tk.END)
                alerts_display.insert(tk.END, f"Alert Set:\n")
                alerts_display.insert(tk.END, f"Symbol: {symbol}\n")
                alerts_display.insert(tk.END, f"Price: ${price}\n")
                alerts_display.insert(tk.END, f"Type: {alert_type_val}")
                
                # Here you would typically save the alert or set up monitoring
                self.notification_manager.send_desktop_notification(
                    "Crypto Alert", 
                    f"Alert set for {symbol} at ${price}"
                )
            except ValueError:
                messagebox.showerror("Error", "Invalid input")

        ttk.Button(tab, text="Set Alert", command=set_alert).pack()

def main():
    root = tk.Tk()
    app = CryptoTrackerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()

