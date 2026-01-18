class PortfolioTracker:
    def __init__(self):
        self.portfolio = {}
    
    def add_holding(self, symbol, amount, purchase_price):
        self.portfolio[symbol] = {
            'amount': amount,
            'purchase_price': purchase_price,
            'current_value': None,
            'profit_loss_percentage': None
        }
    
    def update_portfolio_value(self, current_prices):
        for symbol, details in self.portfolio.items():
            current_price = current_prices.get(symbol, 0)
            details['current_value'] = details['amount'] * current_price
            details['profit_loss_percentage'] = (
                (current_price - details['purchase_price']) / 
                details['purchase_price'] * 100
            )
        return self.portfolio