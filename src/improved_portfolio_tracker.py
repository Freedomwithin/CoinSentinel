# src/portfolio_tracker.py

import json
import os
from datetime import datetime
from typing import Dict, List, Optional


class PortfolioTracker:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)

        self.transactions_file = os.path.join(data_dir, "transactions.json")
        self.transactions = self.load_transactions()
        self.holdings = self.calculate_holdings()

    def load_transactions(self) -> List[Dict]:
        if os.path.exists(self.transactions_file):
            try:
                with open(self.transactions_file, "r") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading transactions: {e}")
                return []
        return []

    def save_transactions(self):
        try:
            with open(self.transactions_file, "w") as f:
                json.dump(self.transactions, f, indent=2)
        except Exception as e:
            print(f"Error saving transactions: {e}")

    def add_transaction(self, data: Dict):
        transaction = {
            "id": len(self.transactions) + 1,
            "coin_id": data["coin"],
            "coin_name": data.get("coin_name", ""),
            "type": data["type"].lower(),
            "amount": data["amount"],
            "price": data["price"],
            "date": data["date"] or datetime.now().strftime("%Y-%m-%d"),
            "timestamp": datetime.now().isoformat(),
        }
        self.transactions.append(transaction)
        self.save_transactions()
        self.holdings = self.calculate_holdings()
        return transaction

    def calculate_holdings(self) -> Dict[str, Dict]:
        holdings = {}

        for transaction in self.transactions:
            coin_id = transaction["coin_id"]
            coin_name = transaction["coin_name"]
            txn_type = transaction["type"]
            amount = transaction["amount"]
            price = transaction["price"]

            if coin_id not in holdings:
                holdings[coin_id] = {
                    "coin_id": coin_id,
                    "name": coin_name,
                    "total_amount": 0,
                    "total_cost": 0,
                    "transactions": [],
                }

            if txn_type == "buy":
                holdings[coin_id]["total_amount"] += amount
                holdings[coin_id]["total_cost"] += amount * price
                holdings[coin_id]["transactions"].append(transaction)
            elif txn_type == "sell":
                holdings[coin_id]["total_amount"] = max(
                    0, holdings[coin_id]["total_amount"] - amount
                )
                if holdings[coin_id]["total_amount"] == 0:
                    holdings[coin_id]["total_cost"] = 0
                holdings[coin_id]["transactions"].append(transaction)

        holdings = {k: v for k, v in holdings.items() if v["total_amount"] > 0}
        return holdings

    def get_holdings(self) -> Dict[str, Dict]:
        return {
            coin_id: {
                "amount": holding["total_amount"],
                "avg_price": (
                    holding["total_cost"] / holding["total_amount"]
                    if holding["total_amount"] > 0
                    else 0
                ),
            }
            for coin_id, holding in self.holdings.items()
        }

    def get_portfolio_summary(self, current_prices: Dict = None) -> Dict:
        holdings_list = []
        total_value = 0
        total_cost = 0

        for coin_id, holding in self.holdings.items():
            amount = holding["total_amount"]
            avg_cost = holding["total_cost"] / amount if amount > 0 else 0

            current_price = current_prices.get(coin_id, 0) if current_prices else 0
            current_value = amount * current_price
            cost_basis = amount * avg_cost
            pnl_amount = current_value - cost_basis
            pnl_percent = (pnl_amount / cost_basis * 100) if cost_basis > 0 else 0

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

        for holding in holdings_list:
            holding["allocation"] = (
                (holding["current_value"] / total_value * 100) if total_value > 0 else 0
            )

        total_pnl = total_value - total_cost
        total_pnl_percent = (total_pnl / total_cost * 100) if total_cost > 0 else 0

        diversity_score = self.calculate_diversity_score(holdings_list)
        risk_level = self.assess_risk_level(holdings_list)

        return {
            "holdings": holdings_list,
            "total_value": total_value,
            "total_cost": total_cost,
            "total_pnl": total_pnl,
            "total_pnl_percent": total_pnl_percent,
            "daily_change": 0,
            "daily_change_percent": 0,
            "diversity_score": diversity_score,
            "risk_level": risk_level,
            "coin_count": len(holdings_list),
        }

    def calculate_diversity_score(self, holdings: List[Dict]) -> int:
        if not holdings:
            return 0

        allocations = [h["allocation"] for h in holdings]

        if len(allocations) == 1:
            return 20

        hhi = sum([(alloc / 100) ** 2 for alloc in allocations])
        diversity_score = max(0, min(100, 100 - (hhi * 100)))
        return int(diversity_score)

    def assess_risk_level(self, holdings: List[Dict]) -> str:
        if not holdings:
            return "Low"

        volatility_scores = []

        for holding in holdings:
            allocation = holding["allocation"]
            if holding["symbol"] in ["BTC", "ETH"]:
                volatility = 0.7
            else:
                volatility = 1.0

            weighted_volatility = allocation * volatility
            volatility_scores.append(weighted_volatility)

        avg_volatility = sum(volatility_scores) / len(volatility_scores)

        if avg_volatility < 0.5:
            return "Low"
        elif avg_volatility < 0.8:
            return "Medium"
        else:
            return "High"
