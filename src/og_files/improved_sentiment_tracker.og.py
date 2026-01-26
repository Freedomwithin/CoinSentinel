import requests
from datetime import datetime, timedelta
import json
import os
from collections import Counter
import re

class ImprovedSentimentTracker:
    def __init__(self):
        """
        Initialize sentiment tracker with multiple data sources.
        """
        self.cache_file = "sentiment_cache.json"
        self.cache = self.load_cache()
        self.cache_duration = 3600  # 1 hour cache
        
        # Sentiment keywords for basic analysis
        self.positive_keywords = {
            'bullish', 'moon', 'rocket', 'pump', 'growth', 'surge', 'rally',
            'breakout', 'bullrun', 'gains', 'profit', 'buy', 'long', 'hold',
            'strong', 'uptrend', 'accumulate', 'adoption', 'partnership'
        }
        
        self.negative_keywords = {
            'bearish', 'crash', 'dump', 'drop', 'fall', 'decline', 'sell',
            'short', 'fear', 'panic', 'loss', 'scam', 'rug', 'dead',
            'weak', 'downtrend', 'resistance', 'bubble', 'regulation'
        }
    
    def get_fear_greed_index(self):
        """
        Get Crypto Fear & Greed Index from alternative.me.
        Range: 0-100 (0 = Extreme Fear, 100 = Extreme Greed)
        
        Returns:
            Dictionary with fear & greed data
        """
        cache_key = 'fear_greed_index'
        
        # Check cache
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]['data']
        
        try:
            response = requests.get('https://api.alternative.me/fng/', timeout=10)
            if response.status_code == 200:
                data = response.json()
                result = data.get('data', [{}])[0]
                
                # Add interpretation
                value = int(result.get('value', 50))
                result['interpretation'] = self._interpret_fear_greed(value)
                
                # Cache the result
                self._update_cache(cache_key, result)
                return result
        except Exception as e:
            print(f"Error fetching Fear & Greed Index: {e}")
        
        return None
    
    def get_fear_greed_history(self, days=30):
        """
        Get historical Fear & Greed Index data.
        
        Args:
            days: Number of days of historical data
            
        Returns:
            List of historical fear & greed values
        """
        try:
            url = f'https://api.alternative.me/fng/?limit={days}'
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                history = data.get('data', [])
                
                # Add interpretations
                for entry in history:
                    value = int(entry.get('value', 50))
                    entry['interpretation'] = self._interpret_fear_greed(value)
                
                return history
        except Exception as e:
            print(f"Error fetching Fear & Greed history: {e}")
        
        return []
    
    def _interpret_fear_greed(self, value):
        """
        Interpret Fear & Greed Index value.
        
        Args:
            value: Index value (0-100)
            
        Returns:
            Interpretation string
        """
        if value <= 20:
            return 'Extreme Fear'
        elif value <= 40:
            return 'Fear'
        elif value <= 60:
            return 'Neutral'
        elif value <= 80:
            return 'Greed'
        else:
            return 'Extreme Greed'
    
    def analyze_text_sentiment(self, text):
        """
        Analyze sentiment of text using keyword matching.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with sentiment analysis
        """
        text_lower = text.lower()
        words = set(re.findall(r'\w+', text_lower))
        
        positive_count = len(words & self.positive_keywords)
        negative_count = len(words & self.negative_keywords)
        total_keywords = positive_count + negative_count
        
        if total_keywords == 0:
            sentiment_score = 50  # Neutral
            sentiment = 'Neutral'
        else:
            # Calculate sentiment score (0-100)
            sentiment_score = (positive_count / total_keywords) * 100
            
            if sentiment_score >= 70:
                sentiment = 'Very Bullish'
            elif sentiment_score >= 55:
                sentiment = 'Bullish'
            elif sentiment_score >= 45:
                sentiment = 'Neutral'
            elif sentiment_score >= 30:
                sentiment = 'Bearish'
            else:
                sentiment = 'Very Bearish'
        
        return {
            'sentiment': sentiment,
            'score': sentiment_score,
            'positive_keywords_found': positive_count,
            'negative_keywords_found': negative_count,
            'confidence': total_keywords
        }
    
    def get_social_sentiment(self, coin_symbol):
        """
        Get aggregated social sentiment for a cryptocurrency.
        Note: This is a simplified version. In production, you'd use APIs like:
        - LunarCrush
        - Santiment
        - The TIE
        
        Args:
            coin_symbol: Cryptocurrency symbol
            
        Returns:
            Dictionary with social sentiment data
        """
        cache_key = f'social_sentiment_{coin_symbol.lower()}'
        
        # Check cache
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]['data']
        
        # This is a placeholder - you'd integrate with actual social sentiment APIs
        # For now, we'll return a structure showing what data could be available
        result = {
            'symbol': coin_symbol.upper(),
            'sentiment_score': None,
            'social_volume': None,
            'trending_score': None,
            'message': 'Social sentiment API integration required. Consider APIs like LunarCrush or Santiment.'
        }
        
        return result
    
    def get_market_sentiment_indicators(self, coin_data):
        """
        Calculate market-based sentiment indicators from price and volume data.
        
        Args:
            coin_data: Dictionary with price and volume data
            
        Returns:
            Dictionary with market sentiment indicators
        """
        indicators = {}
        
        # Price momentum sentiment
        if 'price_change_percentage_24h' in coin_data:
            price_change = coin_data['price_change_percentage_24h']
            if price_change > 10:
                indicators['price_momentum'] = 'Very Bullish'
            elif price_change > 3:
                indicators['price_momentum'] = 'Bullish'
            elif price_change > -3:
                indicators['price_momentum'] = 'Neutral'
            elif price_change > -10:
                indicators['price_momentum'] = 'Bearish'
            else:
                indicators['price_momentum'] = 'Very Bearish'
        
        # Volume sentiment
        if 'total_volume' in coin_data and 'market_cap' in coin_data:
            volume_to_mcap = coin_data['total_volume'] / coin_data['market_cap']
            if volume_to_mcap > 0.3:
                indicators['volume_sentiment'] = 'High Activity'
            elif volume_to_mcap > 0.1:
                indicators['volume_sentiment'] = 'Normal Activity'
            else:
                indicators['volume_sentiment'] = 'Low Activity'
        
        # Market cap rank sentiment (lower rank = more established)
        if 'market_cap_rank' in coin_data:
            rank = coin_data['market_cap_rank']
            if rank <= 10:
                indicators['establishment'] = 'Blue Chip'
            elif rank <= 50:
                indicators['establishment'] = 'Established'
            elif rank <= 100:
                indicators['establishment'] = 'Mid Cap'
            else:
                indicators['establishment'] = 'Small Cap'
        
        return indicators
    
    def get_overall_market_sentiment(self, market_data):
        """
        Calculate overall cryptocurrency market sentiment.
        
        Args:
            market_data: List of coin market data
            
        Returns:
            Dictionary with overall market sentiment
        """
        if not market_data:
            return {}
        
        # Calculate average 24h change
        price_changes = [
            coin.get('price_change_percentage_24h', 0)
            for coin in market_data
            if coin.get('price_change_percentage_24h') is not None
        ]
        
        avg_change = sum(price_changes) / len(price_changes) if price_changes else 0
        
        # Count gainers vs losers
        gainers = len([c for c in price_changes if c > 0])
        losers = len([c for c in price_changes if c < 0])
        neutral = len(price_changes) - gainers - losers
        
        # Determine market sentiment
        if avg_change > 3:
            market_sentiment = 'Very Bullish'
        elif avg_change > 1:
            market_sentiment = 'Bullish'
        elif avg_change > -1:
            market_sentiment = 'Neutral'
        elif avg_change > -3:
            market_sentiment = 'Bearish'
        else:
            market_sentiment = 'Very Bearish'
        
        # Get Fear & Greed Index
        fgi = self.get_fear_greed_index()
        
        return {
            'market_sentiment': market_sentiment,
            'average_24h_change': round(avg_change, 2),
            'gainers': gainers,
            'losers': losers,
            'neutral': neutral,
            'gainer_percentage': round((gainers / len(price_changes)) * 100, 1),
            'fear_greed_index': fgi.get('value') if fgi else None,
            'fear_greed_classification': fgi.get('value_classification') if fgi else None,
            'total_coins_analyzed': len(price_changes)
        }
    
    def get_sentiment_summary(self, coin_symbol, coin_data):
        """
        Get comprehensive sentiment summary for a coin.
        
        Args:
            coin_symbol: Cryptocurrency symbol
            coin_data: Market data for the coin
            
        Returns:
            Dictionary with complete sentiment analysis
        """
        summary = {
            'symbol': coin_symbol.upper(),
            'timestamp': datetime.now().isoformat(),
            'fear_greed_index': self.get_fear_greed_index(),
            'market_indicators': self.get_market_sentiment_indicators(coin_data),
            'social_sentiment': self.get_social_sentiment(coin_symbol)
        }
        
        # Calculate composite sentiment score
        scores = []
        
        # Add Fear & Greed score
        if summary['fear_greed_index']:
            scores.append(int(summary['fear_greed_index'].get('value', 50)))
        
        # Add price momentum score
        if 'price_change_percentage_24h' in coin_data:
            # Convert price change to 0-100 scale
            price_change = coin_data['price_change_percentage_24h']
            # Clamp between -50% and +50%, then scale to 0-100
            clamped = max(-50, min(50, price_change))
            price_score = (clamped + 50) * 1.0
            scores.append(price_score)
        
        if scores:
            summary['composite_sentiment_score'] = round(sum(scores) / len(scores), 1)
            summary['composite_sentiment'] = self._interpret_fear_greed(summary['composite_sentiment_score'])
        
        return summary
    
    def _is_cache_valid(self, key):
        """Check if cached data is still valid."""
        if key not in self.cache:
            return False
        
        cached_time = datetime.fromisoformat(self.cache[key]['timestamp'])
        age = (datetime.now() - cached_time).total_seconds()
        
        return age < self.cache_duration
    
    def _update_cache(self, key, data):
        """Update cache with new data."""
        self.cache[key] = {
            'timestamp': datetime.now().isoformat(),
            'data': data
        }
        self.save_cache()
    
    def save_cache(self):
        """Save cache to file."""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f, indent=2)
        except Exception as e:
            print(f"Error saving cache: {e}")
    
    def load_cache(self):
        """Load cache from file."""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading cache: {e}")
        return {}
    
    def clear_cache(self):
        """Clear sentiment cache."""
        self.cache = {}
        self.save_cache()


# Example usage
if __name__ == "__main__":
    tracker = ImprovedSentimentTracker()
    
    # Get Fear & Greed Index
    print("=== Fear & Greed Index ===")
    fgi = tracker.get_fear_greed_index()
    if fgi:
        print(f"Value: {fgi.get('value')}")
        print(f"Classification: {fgi.get('value_classification')}")
        print(f"Interpretation: {fgi.get('interpretation')}")
    
    # Analyze text sentiment
    print("\n=== Text Sentiment Analysis ===")
    sample_text = "Bitcoin is showing strong bullish momentum with a major breakout above resistance!"
    sentiment = tracker.analyze_text_sentiment(sample_text)
    print(f"Text: {sample_text}")
    print(f"Sentiment: {sentiment['sentiment']} (Score: {sentiment['score']:.1f})")
    
    # Market indicators
    print("\n=== Market Sentiment Indicators ===")
    sample_coin_data = {
        'price_change_percentage_24h': 5.2,
        'total_volume': 50000000000,
        'market_cap': 800000000000,
        'market_cap_rank': 1
    }
    indicators = tracker.get_market_sentiment_indicators(sample_coin_data)
    for key, value in indicators.items():
        print(f"{key}: {value}")
    
    # Overall market sentiment
    print("\n=== Overall Market Sentiment ===")
    sample_market = [
        {'price_change_percentage_24h': 2.5},
        {'price_change_percentage_24h': -1.2},
        {'price_change_percentage_24h': 4.3},
        {'price_change_percentage_24h': 1.8},
        {'price_change_percentage_24h': -0.5},
    ]
    market_sentiment = tracker.get_overall_market_sentiment(sample_market)
    print(f"Market Sentiment: {market_sentiment['market_sentiment']}")
    print(f"Avg 24h Change: {market_sentiment['average_24h_change']}%")
    print(f"Gainers: {market_sentiment['gainers']} ({market_sentiment['gainer_percentage']}%)")
    print(f"Losers: {market_sentiment['losers']}")import requests
from datetime import datetime, timedelta
import json
import os
from collections import Counter
import re

class ImprovedSentimentTracker:
    def __init__(self):
        """
        Initialize sentiment tracker with multiple data sources.
        """
        self.cache_file = "sentiment_cache.json"
        self.cache = self.load_cache()
        self.cache_duration = 3600  # 1 hour cache
        
        # Sentiment keywords for basic analysis
        self.positive_keywords = {
            'bullish', 'moon', 'rocket', 'pump', 'growth', 'surge', 'rally',
            'breakout', 'bullrun', 'gains', 'profit', 'buy', 'long', 'hold',
            'strong', 'uptrend', 'accumulate', 'adoption', 'partnership'
        }
        
        self.negative_keywords = {
            'bearish', 'crash', 'dump', 'drop', 'fall', 'decline', 'sell',
            'short', 'fear', 'panic', 'loss', 'scam', 'rug', 'dead',
            'weak', 'downtrend', 'resistance', 'bubble', 'regulation'
        }
    
    def get_fear_greed_index(self):
        """
        Get Crypto Fear & Greed Index from alternative.me.
        Range: 0-100 (0 = Extreme Fear, 100 = Extreme Greed)
        
        Returns:
            Dictionary with fear & greed data
        """
        cache_key = 'fear_greed_index'
        
        # Check cache
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]['data']
        
        try:
            response = requests.get('https://api.alternative.me/fng/', timeout=10)
            if response.status_code == 200:
                data = response.json()
                result = data.get('data', [{}])[0]
                
                # Add interpretation
                value = int(result.get('value', 50))
                result['interpretation'] = self._interpret_fear_greed(value)
                
                # Cache the result
                self._update_cache(cache_key, result)
                return result
        except Exception as e:
            print(f"Error fetching Fear & Greed Index: {e}")
        
        return None
    
    def get_fear_greed_history(self, days=30):
        """
        Get historical Fear & Greed Index data.
        
        Args:
            days: Number of days of historical data
            
        Returns:
            List of historical fear & greed values
        """
        try:
            url = f'https://api.alternative.me/fng/?limit={days}'
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                history = data.get('data', [])
                
                # Add interpretations
                for entry in history:
                    value = int(entry.get('value', 50))
                    entry['interpretation'] = self._interpret_fear_greed(value)
                
                return history
        except Exception as e:
            print(f"Error fetching Fear & Greed history: {e}")
        
        return []
    
    def _interpret_fear_greed(self, value):
        """
        Interpret Fear & Greed Index value.
        
        Args:
            value: Index value (0-100)
            
        Returns:
            Interpretation string
        """
        if value <= 20:
            return 'Extreme Fear'
        elif value <= 40:
            return 'Fear'
        elif value <= 60:
            return 'Neutral'
        elif value <= 80:
            return 'Greed'
        else:
            return 'Extreme Greed'
    
    def analyze_text_sentiment(self, text):
        """
        Analyze sentiment of text using keyword matching.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with sentiment analysis
        """
        text_lower = text.lower()
        words = set(re.findall(r'\w+', text_lower))
        
        positive_count = len(words & self.positive_keywords)
        negative_count = len(words & self.negative_keywords)
        total_keywords = positive_count + negative_count
        
        if total_keywords == 0:
            sentiment_score = 50  # Neutral
            sentiment = 'Neutral'
        else:
            # Calculate sentiment score (0-100)
            sentiment_score = (positive_count / total_keywords) * 100
            
            if sentiment_score >= 70:
                sentiment = 'Very Bullish'
            elif sentiment_score >= 55:
                sentiment = 'Bullish'
            elif sentiment_score >= 45:
                sentiment = 'Neutral'
            elif sentiment_score >= 30:
                sentiment = 'Bearish'
            else:
                sentiment = 'Very Bearish'
        
        return {
            'sentiment': sentiment,
            'score': sentiment_score,
            'positive_keywords_found': positive_count,
            'negative_keywords_found': negative_count,
            'confidence': total_keywords
        }
    
    def get_social_sentiment(self, coin_symbol):
        """
        Get aggregated social sentiment for a cryptocurrency.
        Note: This is a simplified version. In production, you'd use APIs like:
        - LunarCrush
        - Santiment
        - The TIE
        
        Args:
            coin_symbol: Cryptocurrency symbol
            
        Returns:
            Dictionary with social sentiment data
        """
        cache_key = f'social_sentiment_{coin_symbol.lower()}'
        
        # Check cache
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]['data']
        
        # This is a placeholder - you'd integrate with actual social sentiment APIs
        # For now, we'll return a structure showing what data could be available
        result = {
            'symbol': coin_symbol.upper(),
            'sentiment_score': None,
            'social_volume': None,
            'trending_score': None,
            'message': 'Social sentiment API integration required. Consider APIs like LunarCrush or Santiment.'
        }
        
        return result
    
    def get_market_sentiment_indicators(self, coin_data):
        """
        Calculate market-based sentiment indicators from price and volume data.
        
        Args:
            coin_data: Dictionary with price and volume data
            
        Returns:
            Dictionary with market sentiment indicators
        """
        indicators = {}
        
        # Price momentum sentiment
        if 'price_change_percentage_24h' in coin_data:
            price_change = coin_data['price_change_percentage_24h']
            if price_change > 10:
                indicators['price_momentum'] = 'Very Bullish'
            elif price_change > 3:
                indicators['price_momentum'] = 'Bullish'
            elif price_change > -3:
                indicators['price_momentum'] = 'Neutral'
            elif price_change > -10:
                indicators['price_momentum'] = 'Bearish'
            else:
                indicators['price_momentum'] = 'Very Bearish'
        
        # Volume sentiment
        if 'total_volume' in coin_data and 'market_cap' in coin_data:
            volume_to_mcap = coin_data['total_volume'] / coin_data['market_cap']
            if volume_to_mcap > 0.3:
                indicators['volume_sentiment'] = 'High Activity'
            elif volume_to_mcap > 0.1:
                indicators['volume_sentiment'] = 'Normal Activity'
            else:
                indicators['volume_sentiment'] = 'Low Activity'
        
        # Market cap rank sentiment (lower rank = more established)
        if 'market_cap_rank' in coin_data:
            rank = coin_data['market_cap_rank']
            if rank <= 10:
                indicators['establishment'] = 'Blue Chip'
            elif rank <= 50:
                indicators['establishment'] = 'Established'
            elif rank <= 100:
                indicators['establishment'] = 'Mid Cap'
            else:
                indicators['establishment'] = 'Small Cap'
        
        return indicators
    
    def get_overall_market_sentiment(self, market_data):
        """
        Calculate overall cryptocurrency market sentiment.
        
        Args:
            market_data: List of coin market data
            
        Returns:
            Dictionary with overall market sentiment
        """
        if not market_data:
            return {}
        
        # Calculate average 24h change
        price_changes = [
            coin.get('price_change_percentage_24h', 0)
            for coin in market_data
            if coin.get('price_change_percentage_24h') is not None
        ]
        
        avg_change = sum(price_changes) / len(price_changes) if price_changes else 0
        
        # Count gainers vs losers
        gainers = len([c for c in price_changes if c > 0])
        losers = len([c for c in price_changes if c < 0])
        neutral = len(price_changes) - gainers - losers
        
        # Determine market sentiment
        if avg_change > 3:
            market_sentiment = 'Very Bullish'
        elif avg_change > 1:
            market_sentiment = 'Bullish'
        elif avg_change > -1:
            market_sentiment = 'Neutral'
        elif avg_change > -3:
            market_sentiment = 'Bearish'
        else:
            market_sentiment = 'Very Bearish'
        
        # Get Fear & Greed Index
        fgi = self.get_fear_greed_index()
        
        return {
            'market_sentiment': market_sentiment,
            'average_24h_change': round(avg_change, 2),
            'gainers': gainers,
            'losers': losers,
            'neutral': neutral,
            'gainer_percentage': round((gainers / len(price_changes)) * 100, 1),
            'fear_greed_index': fgi.get('value') if fgi else None,
            'fear_greed_classification': fgi.get('value_classification') if fgi else None,
            'total_coins_analyzed': len(price_changes)
        }
    
    def get_sentiment_summary(self, coin_symbol, coin_data):
        """
        Get comprehensive sentiment summary for a coin.
        
        Args:
            coin_symbol: Cryptocurrency symbol
            coin_data: Market data for the coin
            
        Returns:
            Dictionary with complete sentiment analysis
        """
        summary = {
            'symbol': coin_symbol.upper(),
            'timestamp': datetime.now().isoformat(),
            'fear_greed_index': self.get_fear_greed_index(),
            'market_indicators': self.get_market_sentiment_indicators(coin_data),
            'social_sentiment': self.get_social_sentiment(coin_symbol)
        }
        
        # Calculate composite sentiment score
        scores = []
        
        # Add Fear & Greed score
        if summary['fear_greed_index']:
            scores.append(int(summary['fear_greed_index'].get('value', 50)))
        
        # Add price momentum score
        if 'price_change_percentage_24h' in coin_data:
            # Convert price change to 0-100 scale
            price_change = coin_data['price_change_percentage_24h']
            # Clamp between -50% and +50%, then scale to 0-100
            clamped = max(-50, min(50, price_change))
            price_score = (clamped + 50) * 1.0
            scores.append(price_score)
        
        if scores:
            summary['composite_sentiment_score'] = round(sum(scores) / len(scores), 1)
            summary['composite_sentiment'] = self._interpret_fear_greed(summary['composite_sentiment_score'])
        
        return summary
    
    def _is_cache_valid(self, key):
        """Check if cached data is still valid."""
        if key not in self.cache:
            return False
        
        cached_time = datetime.fromisoformat(self.cache[key]['timestamp'])
        age = (datetime.now() - cached_time).total_seconds()
        
        return age < self.cache_duration
    
    def _update_cache(self, key, data):
        """Update cache with new data."""
        self.cache[key] = {
            'timestamp': datetime.now().isoformat(),
            'data': data
        }
        self.save_cache()
    
    def save_cache(self):
        """Save cache to file."""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f, indent=2)
        except Exception as e:
            print(f"Error saving cache: {e}")
    
    def load_cache(self):
        """Load cache from file."""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading cache: {e}")
        return {}
    
    def clear_cache(self):
        """Clear sentiment cache."""
        self.cache = {}
        self.save_cache()


# Example usage
if __name__ == "__main__":
    tracker = ImprovedSentimentTracker()
    
    # Get Fear & Greed Index
    print("=== Fear & Greed Index ===")
    fgi = tracker.get_fear_greed_index()
    if fgi:
        print(f"Value: {fgi.get('value')}")
        print(f"Classification: {fgi.get('value_classification')}")
        print(f"Interpretation: {fgi.get('interpretation')}")
    
    # Analyze text sentiment
    print("\n=== Text Sentiment Analysis ===")
    sample_text = "Bitcoin is showing strong bullish momentum with a major breakout above resistance!"
    sentiment = tracker.analyze_text_sentiment(sample_text)
    print(f"Text: {sample_text}")
    print(f"Sentiment: {sentiment['sentiment']} (Score: {sentiment['score']:.1f})")
    
    # Market indicators
    print("\n=== Market Sentiment Indicators ===")
    sample_coin_data = {
        'price_change_percentage_24h': 5.2,
        'total_volume': 50000000000,
        'market_cap': 800000000000,
        'market_cap_rank': 1
    }
    indicators = tracker.get_market_sentiment_indicators(sample_coin_data)
    for key, value in indicators.items():
        print(f"{key}: {value}")
    
    # Overall market sentiment
    print("\n=== Overall Market Sentiment ===")
    sample_market = [
        {'price_change_percentage_24h': 2.5},
        {'price_change_percentage_24h': -1.2},
        {'price_change_percentage_24h': 4.3},
        {'price_change_percentage_24h': 1.8},
        {'price_change_percentage_24h': -0.5},
    ]
    market_sentiment = tracker.get_overall_market_sentiment(sample_market)
    print(f"Market Sentiment: {market_sentiment['market_sentiment']}")
    print(f"Avg 24h Change: {market_sentiment['average_24h_change']}%")
    print(f"Gainers: {market_sentiment['gainers']} ({market_sentiment['gainer_percentage']}%)")
    print(f"Losers: {market_sentiment['losers']}")