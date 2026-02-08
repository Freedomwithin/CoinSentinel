# src/improved_portfolio_tracker.py

import json
import os
from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd
import numpy as np


class PortfolioTracker:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)

        self.transactions_file = os.path.join(data_dir, "transactions.json")
        self.portfolio_file = os.path.join(data_dir, "portfolio.json")

        self.transactions = self.load_transactions()
        self.holdings = self.calculate_holdings()

    def load_transactions(self) -> List[Dict]:
        """Load transactions from file"""
        if os.path.exists(self.transactions_file):
            try:
                with open(self.transactions_file, "r") as f:
                    return json.load(f)
            except:
                return []
        return []

    def save_transactions(self):
        """Save transactions to file"""
        try:
            with open(self.transactions_file, "w") as f:
                json.dump(self.transactions, f, indent=2)
        except Exception as e:
            print(f"Error saving transactions: {e}")

    def add_transaction(self, data: Dict):
        """
        Add a new transaction from dialog data
        
        Args:
            data: Dictionary with keys: coin, type, amount, price, date
        """
        # Extract coin_id from data
        coin_id = data.get("coin", "")
        
        transaction = {
            "id": len(self.transactions) + 1,
            "coin_id": coin_id,
            "coin_name": coin_id,  # Will be updated when we fetch coin info
            "type": data.get("type", "buy").lower(),
            "amount": data.get("amount", 0),
            "price": data.get("price", 0),
            "date": data.get("date", datetime.now().strftime("%Y-%m-%d")),
            "timestamp": datetime.now().isoformat(),
        }

        self.transactions.append(transaction)
        self.save_transactions()
        self.holdings = self.calculate_holdings()

        return transaction

    def get_holdings(self) -> Dict[str, Dict]:
        """
        Get current holdings
        
        Returns:
            Dictionary mapping coin_id to holding info with 'amount' and 'avg_price'
        """
        return self.holdings

    def calculate_holdings(self) -> Dict[str, Dict]:
        """Calculate current holdings from transactions"""
        holdings = {}

        for transaction in self.transactions:
            coin_id = transaction["coin_id"]
            coin_name = transaction.get("coin_name", coin_id)
            txn_type = transaction["type"]
            amount = transaction["amount"]
            price = transaction["price"]

            if coin_id not in holdings:
                holdings[coin_id] = {
                    "coin_id": coin_id,
                    "name": coin_name,
                    "amount": 0,  # Changed from total_amount to amount
                    "total_cost": 0,
                    "avg_price": 0,  # Added avg_price field
                    "transactions": [],
                }

            if txn_type == "buy":
                holdings[coin_id]["amount"] += amount
                holdings[coin_id]["total_cost"] += amount * price
                holdings[coin_id]["transactions"].append(transaction)
            elif txn_type == "sell":
                # For simplicity, we use FIFO method
                holdings[coin_id]["amount"] = max(
                    0, holdings[coin_id]["amount"] - amount
                )
                if holdings[coin_id]["amount"] == 0:
                    holdings[coin_id]["total_cost"] = 0
                else:
                    # Adjust cost proportionally
                    holdings[coin_id]["total_cost"] = max(
                        0, holdings[coin_id]["total_cost"] - (amount * price)
                    )
                holdings[coin_id]["transactions"].append(transaction)

        # Calculate average price for each holding
        for coin_id in holdings:
            amount = holdings[coin_id]["amount"]
            total_cost = holdings[coin_id]["total_cost"]
            holdings[coin_id]["avg_price"] = total_cost / amount if amount > 0 else 0

        # Remove coins with zero holdings
        holdings = {k: v for k, v in holdings.items() if v["amount"] > 0}

        return holdings

    def get_portfolio_summary(self, current_prices: Dict = None) -> Dict:
        """Get portfolio summary with current values"""
        holdings_list = []
        total_value = 0
        total_cost = 0

        for coin_id, holding in self.holdings.items():
            amount = holding["amount"]
            avg_cost = holding.get("avg_price", 0)

            # Get current price (would come from API in real use)
            current_price = current_prices.get(coin_id, 0) if current_prices else 0
            current_value = amount * current_price
            cost_basis = amount * avg_cost
            pnl_amount = current_value - cost_basis
            pnl_percent = (pnl_amount / cost_basis * 100) if cost_basis > 0 else 0

            # Extract symbol from coin name
            symbol = (
                holding["name"].split()[0].upper()
                if holding["name"]
                else coin_id.upper()
            )

            holdings_list.append(
                {
                    "coin_id": coin_id,
                    "name": holding["name"],
                    "symbol": symbol,
                    "amount": amount,
                    "avg_cost": avg_cost,
                    "current_price": current_price,
                    "current_value": current_value,
                    "cost_basis": cost_basis,
                    "pnl_amount": pnl_amount,
                    "pnl_percent": pnl_percent,
                }
            )

            total_value += current_value
            total_cost += cost_basis

        # Calculate allocations
        for holding in holdings_list:
            holding["allocation"] = (
                (holding["current_value"] / total_value * 100) if total_value > 0 else 0
            )

        # Calculate total P/L
        total_pnl = total_value - total_cost
        total_pnl_percent = (total_pnl / total_cost * 100) if total_cost > 0 else 0

        # Calculate diversity score (simplified)
        diversity_score = self.calculate_diversity_score(holdings_list)

        # Calculate risk score
        risk_level = self.assess_risk_level(holdings_list)

        return {
            "holdings": holdings_list,
            "total_value": total_value,
            "total_cost": total_cost,
            "total_pnl": total_pnl,
            "total_pnl_percent": total_pnl_percent,
            "daily_change": 0,  # Would need historical data
            "daily_change_percent": 0,
            "diversity_score": diversity_score,
            "risk_level": risk_level,
            "coin_count": len(holdings_list),
        }

    def calculate_diversity_score(self, holdings: List[Dict]) -> int:
        """Calculate portfolio diversity score (0-100)"""
        if not holdings:
            return 0

        # Simple diversity calculation based on allocation distribution
        allocations = [h["allocation"] for h in holdings]

        if len(allocations) == 1:
            return 20  # Very concentrated

        # Calculate Herfindahl-Hirschman Index (HHI)
        hhi = sum([(alloc / 100) ** 2 for alloc in allocations])

        # Convert HHI to diversity score (0-100)
        # Lower HHI = more diverse
        diversity_score = max(0, min(100, 100 - (hhi * 100)))

        return int(diversity_score)

    def assess_risk_level(self, holdings: List[Dict]) -> str:
        """Assess portfolio risk level"""
        if not holdings:
            return "Low"

        # Simple risk assessment
        volatility_scores = []

        for holding in holdings:
            allocation = holding["allocation"]
            # Assume different risk levels for different coins
            # In reality, this would use historical volatility data
            if holding["symbol"] in ["BTC", "ETH"]:
                volatility = 0.7  # Lower volatility for major coins
            else:
                volatility = 1.0  # Higher volatility for altcoins

            weighted_volatility = allocation * volatility
            volatility_scores.append(weighted_volatility)

        avg_volatility = sum(volatility_scores) / len(volatility_scores)

        if avg_volatility < 0.5:
            return "Low"
        elif avg_volatility < 0.8:
            return "Medium"
        else:
            return "High"
