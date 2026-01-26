import json
import os
from datetime import datetime
import numpy as np
import pandas as pd

class ImprovedPortfolioTracker:
    def __init__(self, user_id='default'):
        """
        Initialize portfolio tracker with advanced features.
        
        Args:
            user_id: Unique identifier for the user
        """
        self.user_id = user_id
        self.portfolio = {}
        self.transaction_history = []
        self.portfolio_file = f"portfolio_{user_id}.json"
        self.history_file = f"transactions_{user_id}.json"
        self.load_portfolio()
        self.load_transaction_history()
    
    def add_holding(self, symbol, amount, purchase_price, transaction_date=None, notes=''):
        """
        Add or update a holding in the portfolio.
        
        Args:
            symbol: Cryptocurrency symbol
            amount: Amount purchased
            purchase_price: Price at purchase
            transaction_date: Date of purchase (defaults to now)
            notes: Optional notes about the transaction
        """
        symbol = symbol.upper()
        transaction_date = transaction_date or datetime.now().isoformat()
        
        # Record transaction
        transaction = {
            'type': 'buy',
            'symbol': symbol,
            'amount': amount,
            'price': purchase_price,
            'date': transaction_date,
            'notes': notes,
            'total_cost': amount * purchase_price
        }
        self.transaction_history.append(transaction)
        
        # Update portfolio
        if symbol in self.portfolio:
            # Calculate weighted average purchase price
            existing = self.portfolio[symbol]
            total_amount = existing['amount'] + amount
            total_cost = (existing['amount'] * existing['average_purchase_price']) + (amount * purchase_price)
            avg_price = total_cost / total_amount
            
            self.portfolio[symbol] = {
                'amount': total_amount,
                'average_purchase_price': avg_price,
                'first_purchase_date': existing['first_purchase_date'],
                'last_updated': datetime.now().isoformat(),
                'transactions': existing.get('transactions', []) + [transaction],
                'current_price': None,
                'current_value': None,
                'profit_loss': None,
                'profit_loss_percentage': None,
                'total_invested': total_cost
            }
        else:
            self.portfolio[symbol] = {
                'amount': amount,
                'average_purchase_price': purchase_price,
                'first_purchase_date': transaction_date,
                'last_updated': datetime.now().isoformat(),
                'transactions': [transaction],
                'current_price': None,
                'current_value': None,
                'profit_loss': None,
                'profit_loss_percentage': None,
                'total_invested': amount * purchase_price
            }
        
        self.save_portfolio()
        self.save_transaction_history()
        return self.portfolio[symbol]
    
    def sell_holding(self, symbol, amount, sell_price, transaction_date=None, notes=''):
        """
        Sell a portion or all of a holding.
        
        Args:
            symbol: Cryptocurrency symbol
            amount: Amount to sell
            sell_price: Price at sale
            transaction_date: Date of sale
            notes: Optional notes
            
        Returns:
            Dictionary with sale details including realized profit/loss
        """
        symbol = symbol.upper()
        
        if symbol not in self.portfolio:
            raise ValueError(f"{symbol} not found in portfolio")
        
        if self.portfolio[symbol]['amount'] < amount:
            raise ValueError(f"Insufficient {symbol}. Have {self.portfolio[symbol]['amount']}, trying to sell {amount}")
        
        transaction_date = transaction_date or datetime.now().isoformat()
        
        # Calculate realized profit/loss
        avg_purchase_price = self.portfolio[symbol]['average_purchase_price']
        total_cost = amount * avg_purchase_price
        total_revenue = amount * sell_price
        realized_pl = total_revenue - total_cost
        realized_pl_pct = (realized_pl / total_cost) * 100
        
        # Record transaction
        transaction = {
            'type': 'sell',
            'symbol': symbol,
            'amount': amount,
            'price': sell_price,
            'date': transaction_date,
            'notes': notes,
            'total_revenue': total_revenue,
            'realized_profit_loss': realized_pl,
            'realized_pl_percentage': realized_pl_pct
        }
        self.transaction_history.append(transaction)
        
        # Update portfolio
        self.portfolio[symbol]['amount'] -= amount
        self.portfolio[symbol]['total_invested'] -= total_cost
        self.portfolio[symbol]['transactions'].append(transaction)
        self.portfolio[symbol]['last_updated'] = datetime.now().isoformat()
        
        # Remove if completely sold
        if self.portfolio[symbol]['amount'] <= 0:
            del self.portfolio[symbol]
        
        self.save_portfolio()
        self.save_transaction_history()
        
        return {
            'symbol': symbol,
            'amount_sold': amount,
            'sell_price': sell_price,
            'realized_pl': realized_pl,
            'realized_pl_percentage': realized_pl_pct
        }
    
    def update_portfolio_value(self, current_prices):
        """
        Update current values for all holdings.
        
        Args:
            current_prices: Dictionary mapping symbols to current prices
            
        Returns:
            Updated portfolio with current values
        """
        for symbol, details in self.portfolio.items():
            current_price = current_prices.get(symbol, 0)
            
            if current_price > 0:
                details['current_price'] = current_price
                details['current_value'] = details['amount'] * current_price
                details['profit_loss'] = details['current_value'] - details['total_invested']
                details['profit_loss_percentage'] = (
                    (details['profit_loss'] / details['total_invested']) * 100
                )
            
            details['last_updated'] = datetime.now().isoformat()
        
        self.save_portfolio()
        return self.portfolio
    
    def get_portfolio_summary(self):
        """
        Get comprehensive portfolio summary with performance metrics.
        
        Returns:
            Dictionary with portfolio statistics
        """
        if not self.portfolio:
            return {
                'total_holdings': 0,
                'total_invested': 0,
                'current_value': 0,
                'total_profit_loss': 0,
                'total_pl_percentage': 0,
                'best_performer': None,
                'worst_performer': None,
                'holdings': []
            }
        
        total_invested = sum(h['total_invested'] for h in self.portfolio.values())
        current_value = sum(h.get('current_value', 0) for h in self.portfolio.values())
        total_pl = current_value - total_invested
        total_pl_pct = (total_pl / total_invested * 100) if total_invested > 0 else 0
        
        # Find best and worst performers
        performers = [
            (symbol, details.get('profit_loss_percentage', 0))
            for symbol, details in self.portfolio.items()
            if details.get('current_value') is not None
        ]
        
        best_performer = max(performers, key=lambda x: x[1]) if performers else None
        worst_performer = min(performers, key=lambda x: x[1]) if performers else None
        
        # Calculate portfolio allocation
        holdings = []
        for symbol, details in self.portfolio.items():
            allocation = (details.get('current_value', 0) / current_value * 100) if current_value > 0 else 0
            holdings.append({
                'symbol': symbol,
                'amount': details['amount'],
                'avg_purchase_price': details['average_purchase_price'],
                'current_price': details.get('current_price'),
                'current_value': details.get('current_value'),
                'profit_loss': details.get('profit_loss'),
                'pl_percentage': details.get('profit_loss_percentage'),
                'allocation_percentage': allocation,
                'total_invested': details['total_invested']
            })
        
        return {
            'total_holdings': len(self.portfolio),
            'total_invested': total_invested,
            'current_value': current_value,
            'total_profit_loss': total_pl,
            'total_pl_percentage': total_pl_pct,
            'best_performer': best_performer,
            'worst_performer': worst_performer,
            'holdings': sorted(holdings, key=lambda x: x['current_value'] or 0, reverse=True)
        }
    
    def get_transaction_history(self, symbol=None, transaction_type=None, limit=None):
        """
        Get filtered transaction history.
        
        Args:
            symbol: Filter by symbol
            transaction_type: Filter by type ('buy' or 'sell')
            limit: Maximum number of transactions to return
            
        Returns:
            List of transactions
        """
        filtered = self.transaction_history
        
        if symbol:
            symbol = symbol.upper()
            filtered = [t for t in filtered if t['symbol'] == symbol]
        
        if transaction_type:
            filtered = [t for t in filtered if t['type'] == transaction_type]
        
        # Sort by date (most recent first)
        filtered = sorted(filtered, key=lambda x: x['date'], reverse=True)
        
        if limit:
            filtered = filtered[:limit]
        
        return filtered
    
    def calculate_realized_gains(self, symbol=None):
        """
        Calculate total realized gains/losses from sell transactions.
        
        Args:
            symbol: Calculate for specific symbol or all
            
        Returns:
            Dictionary with realized gains statistics
        """
        transactions = self.get_transaction_history(symbol=symbol, transaction_type='sell')
        
        if not transactions:
            return {
                'total_realized_pl': 0,
                'total_revenue': 0,
                'number_of_sales': 0,
                'average_pl_per_sale': 0,
                'win_rate': 0
            }
        
        total_realized_pl = sum(t.get('realized_profit_loss', 0) for t in transactions)
        total_revenue = sum(t.get('total_revenue', 0) for t in transactions)
        winning_trades = len([t for t in transactions if t.get('realized_profit_loss', 0) > 0])
        
        return {
            'total_realized_pl': total_realized_pl,
            'total_revenue': total_revenue,
            'number_of_sales': len(transactions),
            'average_pl_per_sale': total_realized_pl / len(transactions),
            'win_rate': (winning_trades / len(transactions) * 100) if transactions else 0
        }
    
    def get_portfolio_diversity_score(self):
        """
        Calculate portfolio diversity score (0-100).
        Higher score = more diversified.
        
        Returns:
            Diversity score
        """
        if not self.portfolio:
            return 0
        
        # Calculate Herfindahl-Hirschman Index (HHI)
        summary = self.get_portfolio_summary()
        allocations = [h['allocation_percentage'] / 100 for h in summary['holdings']]
        hhi = sum(a ** 2 for a in allocations)
        
        # Convert HHI to diversity score (0-100)
        # HHI ranges from 1/n (perfect diversity) to 1 (concentrated)
        n = len(self.portfolio)
        min_hhi = 1 / n
        diversity_score = ((1 - hhi) / (1 - min_hhi)) * 100 if n > 1 else 0
        
        return round(diversity_score, 2)
    
    def get_portfolio_risk_metrics(self, historical_prices_dict):
        """
        Calculate portfolio risk metrics.
        
        Args:
            historical_prices_dict: Dict mapping symbols to price arrays
            
        Returns:
            Dictionary with risk metrics
        """
        summary = self.get_portfolio_summary()
        
        if not summary['holdings']:
            return {}
        
        # Calculate portfolio volatility (weighted by allocation)
        weighted_volatility = 0
        for holding in summary['holdings']:
            symbol = holding['symbol']
            allocation = holding['allocation_percentage'] / 100
            
            if symbol in historical_prices_dict:
                prices = np.array(historical_prices_dict[symbol])
                returns = np.diff(prices) / prices[:-1]
                volatility = np.std(returns) * np.sqrt(365)  # Annualized
                weighted_volatility += allocation * volatility
        
        # Sharpe ratio (simplified - assumes 0% risk-free rate)
        if weighted_volatility > 0:
            sharpe = (summary['total_pl_percentage'] / 100) / weighted_volatility
        else:
            sharpe = 0
        
        return {
            'portfolio_volatility': weighted_volatility,
            'sharpe_ratio': sharpe,
            'diversity_score': self.get_portfolio_diversity_score(),
            'total_exposure': summary['current_value']
        }
    
    def remove_holding(self, symbol):
        """Remove a holding completely from portfolio."""
        symbol = symbol.upper()
        if symbol in self.portfolio:
            del self.portfolio[symbol]
            self.save_portfolio()
    
    def save_portfolio(self):
        """Save portfolio to JSON file."""
        try:
            with open(self.portfolio_file, 'w') as f:
                json.dump(self.portfolio, f, indent=2)
        except Exception as e:
            print(f"Error saving portfolio: {e}")
    
    def load_portfolio(self):
        """Load portfolio from JSON file."""
        try:
            if os.path.exists(self.portfolio_file):
                with open(self.portfolio_file, 'r') as f:
                    self.portfolio = json.load(f)
        except Exception as e:
            print(f"Error loading portfolio: {e}")
            self.portfolio = {}
    
    def save_transaction_history(self):
        """Save transaction history to JSON file."""
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.transaction_history, f, indent=2)
        except Exception as e:
            print(f"Error saving transaction history: {e}")
    
    def load_transaction_history(self):
        """Load transaction history from JSON file."""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r') as f:
                    self.transaction_history = json.load(f)
        except Exception as e:
            print(f"Error loading transaction history: {e}")
            self.transaction_history = []
    
    def export_to_csv(self, filename='portfolio_export.csv'):
        """Export portfolio to CSV file."""
        summary = self.get_portfolio_summary()
        df = pd.DataFrame(summary['holdings'])
        df.to_csv(filename, index=False)
        return filename
    
    def clear_portfolio(self):
        """Clear all holdings (with confirmation in UI)."""
        self.portfolio = {}
        self.save_portfolio()


# Example usage
if __name__ == "__main__":
    # Create portfolio tracker
    tracker = ImprovedPortfolioTracker(user_id='demo_user')
    
    # Add some holdings
    tracker.add_holding('BTC', 0.5, 42000, notes='Initial investment')
    tracker.add_holding('ETH', 10, 2200, notes='Diversification')
    tracker.add_holding('SOL', 50, 95, notes='High risk play')
    
    # Simulate current prices
    current_prices = {
        'BTC': 45000,
        'ETH': 2500,
        'SOL': 110
    }
    
    # Update portfolio values
    tracker.update_portfolio_value(current_prices)
    
    # Get summary
    summary = tracker.get_portfolio_summary()
    print("\n=== Portfolio Summary ===")
    print(f"Total Invested: ${summary['total_invested']:,.2f}")
    print(f"Current Value: ${summary['current_value']:,.2f}")
    print(f"Total P/L: ${summary['total_profit_loss']:+,.2f} ({summary['total_pl_percentage']:+.2f}%)")
    print(f"Diversity Score: {tracker.get_portfolio_diversity_score():.1f}/100")
    
    if summary['best_performer']:
        print(f"\nBest Performer: {summary['best_performer'][0]} ({summary['best_performer'][1]:+.2f}%)")
    if summary['worst_performer']:
        print(f"Worst Performer: {summary['worst_performer'][0]} ({summary['worst_performer'][1]:+.2f}%)")
    
    print("\n=== Holdings ===")
    for holding in summary['holdings']:
        print(f"{holding['symbol']}: {holding['amount']:.4f} @ ${holding['current_price']:,.2f} "
              f"= ${holding['current_value']:,.2f} ({holding['pl_percentage']:+.2f}%)")
    
    # Sell some holdings
    print("\n=== Selling 5 ETH ===")
    sale = tracker.sell_holding('ETH', 5, 2600)
    print(f"Realized P/L: ${sale['realized_pl']:+,.2f} ({sale['realized_pl_percentage']:+.2f}%)")
    
    # Transaction history
    print("\n=== Recent Transactions ===")
    for tx in tracker.get_transaction_history(limit=5):
        print(f"{tx['date'][:10]} - {tx['type'].upper()} {tx['amount']} {tx['symbol']} @ ${tx['price']:,.2f}")