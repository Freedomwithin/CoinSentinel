# src/improved_sentiment_tracker.py

import requests
import json
import os
from datetime import datetime
from typing import Dict, Optional
import time


class SentimentTracker:
    def __init__(self, api_handler):
        self.api = api_handler
        self.cache_file = "data/sentiment_cache.json"
        self.cache_duration = 300  # 5 minutes cache
        os.makedirs("data", exist_ok=True)

    def get_fear_greed_index(self) -> Optional[Dict]:
        """Get Crypto Fear & Greed Index from Alternative.me API"""
        try:
            # Check cache first
            cache_data = self._load_cache()
            if (
                cache_data
                and time.time() - cache_data.get("timestamp", 0) < self.cache_duration
            ):
                return cache_data.get("fear_greed")

            # Fetch from API
            response = requests.get(
                "https://api.alternative.me/fng/", 
                params={"limit": 1, "format": "json"},
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                if data.get("data"):
                    fgi_data = data["data"][0]

                    result = {
                        "value": int(fgi_data["value"]),
                        "classification": fgi_data["value_classification"],
                        "timestamp": datetime.fromtimestamp(
                            int(fgi_data["timestamp"])
                        ).strftime("%Y-%m-%d %H:%M:%S"),
                    }

                    # Update cache
                    self._update_cache({"fear_greed": result})

                    return result

            return None

        except Exception as e:
            print(f"Error fetching Fear & Greed Index: {e}")
            return None

    def get_market_sentiment(self) -> Dict:
        """Get comprehensive market sentiment analysis"""
        try:
            # Get Fear & Greed Index
            fear_greed = self.get_fear_greed_index() or {
                "value": 50,
                "classification": "Neutral",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }

            # Get market data for analysis
            market_data = self._analyze_market_data()

            return {
                "fear_greed": fear_greed,
                "market_analysis": market_data,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            print(f"Error in market sentiment analysis: {e}")
            return {
                "fear_greed": {
                    "value": 50,
                    "classification": "Error",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                },
                "market_analysis": {},
                "timestamp": datetime.now().isoformat(),
            }

    def get_coin_sentiment(self, coin_id: str) -> Dict:
        """
        Get sentiment analysis for a specific coin
        
        Args:
            coin_id: CoinGecko coin ID
            
        Returns:
            Dictionary with positive, negative, and neutral sentiment percentages
        """
        try:
            # Use the API handler's get_coin_sentiment method
            sentiment = self.api.get_coin_sentiment(coin_id)
            return sentiment
            
        except Exception as e:
            print(f"Error getting coin sentiment for {coin_id}: {e}")
            # Return neutral sentiment on error
            return {
                "positive": 33.0,
                "negative": 33.0,
                "neutral": 34.0
            }

    def _analyze_market_data(self) -> Dict:
        """Analyze market data for sentiment indicators"""
        try:
            # Get top coins data
            coins = self.api.get_top_coins(limit=100)

            if not coins:
                return {}

            gainers = 0
            losers = 0
            neutral = 0
            extreme_gainers = 0
            extreme_losers = 0

            for coin in coins:
                change_24h = coin.get("price_change_percentage_24h", 0) or 0

                if change_24h > 5:
                    extreme_gainers += 1
                    gainers += 1
                elif change_24h > 1:
                    gainers += 1
                elif change_24h < -5:
                    extreme_losers += 1
                    losers += 1
                elif change_24h < -1:
                    losers += 1
                else:
                    neutral += 1

            # Calculate market momentum
            total_coins = len(coins)
            momentum_score = (gainers - losers) / total_coins if total_coins > 0 else 0

            # Determine sentiment based on momentum
            if momentum_score > 0.3:
                market_sentiment = "Strongly Bullish"
            elif momentum_score > 0.1:
                market_sentiment = "Bullish"
            elif momentum_score > -0.1:
                market_sentiment = "Neutral"
            elif momentum_score > -0.3:
                market_sentiment = "Bearish"
            else:
                market_sentiment = "Strongly Bearish"

            return {
                "gainers": gainers,
                "losers": losers,
                "neutral": neutral,
                "extreme_gainers": extreme_gainers,
                "extreme_losers": extreme_losers,
                "momentum_score": momentum_score,
                "market_sentiment": market_sentiment,
                "total_coins_analyzed": total_coins,
            }

        except Exception as e:
            print(f"Error analyzing market data: {e}")
            return {}

    def _load_cache(self) -> Optional[Dict]:
        """Load data from cache"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, "r") as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading cache: {e}")
        return None

    def _update_cache(self, data: Dict):
        """Update cache with new data"""
        try:
            cache_data = {"timestamp": time.time(), **data}

            with open(self.cache_file, "w") as f:
                json.dump(cache_data, f)
        except Exception as e:
            print(f"Error updating cache: {e}")
