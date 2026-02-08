# FIX FOR YOUR ADVANCED PRICE PREDICTOR
# Add this method to your api_handler.py (EnhancedCryptoAPIHandler class)

def get_comprehensive_coin_data(self, coin_id, days=90):
    """
    Get comprehensive data in the format expected by AdvancedPricePredictor
    
    Returns:
        Dictionary with 'prices' key containing [(timestamp_ms, price), ...] tuples
    """
    try:
        print(f"\n{'='*60}")
        print(f"FETCHING COMPREHENSIVE DATA FOR: {coin_id}")
        print(f"Days: {days}")
        print(f"{'='*60}")
        
        # Rate limit
        if hasattr(self, '_rate_limit'):
            self._rate_limit()
        else:
            import time
            time.sleep(1)
        
        # Get market chart from CoinGecko
        market_chart = self.cg.get_coin_market_chart_by_id(
            id=coin_id,
            vs_currency='usd',
            days=days
        )
        
        if not market_chart or 'prices' not in market_chart:
            print("❌ No market data received")
            return None
        
        # CoinGecko returns prices as [[timestamp_ms, price], ...]
        prices = market_chart['prices']
        
        print(f"✓ Received {len(prices)} price points")
        
        # Your predictor expects the data in this exact format
        result = {
            'prices': prices,  # Already in [(timestamp, price), ...] format
            'market_caps': market_chart.get('market_caps', []),
            'total_volumes': market_chart.get('total_volumes', [])
        }
        
        print(f"✓ Data prepared successfully")
        print(f"  Price range: ${min(p[1] for p in prices):.2f} - ${max(p[1] for p in prices):.2f}")
        print(f"  Date range: {len(prices)} data points over {days} days")
        print(f"{'='*60}\n")
        
        return result
        
    except Exception as e:
        print(f"❌ Error in get_comprehensive_coin_data: {e}")
        import traceback
        traceback.print_exc()
        return None


# Also add this helper method for rate limiting if it doesn't exist
def _rate_limit(self):
    """Simple rate limiting"""
    import time
    current_time = time.time()
    
    if not hasattr(self, 'last_request_time'):
        self.last_request_time = 0
    
    time_since_last = current_time - self.last_request_time
    
    if time_since_last < 1.5:  # 1.5 seconds between requests
        time.sleep(1.5 - time_since_last)
    
    self.last_request_time = time.time()


print("""
====================================================================
FIX FOR YOUR ADVANCED PRICE PREDICTOR
====================================================================

YOUR PREDICTOR CALLS:
  data = self.api.get_comprehensive_coin_data(coin_id, days=90)

YOUR API HANDLER NEEDS THIS METHOD!

STEP 1: Add to api_handler.py
------------------------------
Copy the get_comprehensive_coin_data method above into your
EnhancedCryptoAPIHandler class.

Also add the _rate_limit method if you don't have it.

STEP 2: Test
------------
Run a prediction. You should see console output like:

============================================================
FETCHING COMPREHENSIVE DATA FOR: bitcoin
Days: 90
============================================================
✓ Received 720 price points
✓ Data prepared successfully
  Price range: $43,250.00 - $48,500.00
  Date range: 720 data points over 90 days
============================================================

STEP 3: Verify Results
----------------------
Instead of seeing:
  "AI Model warming up. Using basic trend fallback."

You should see:
  "Model projects an upward move of 2.34%."
  "MACD indicates Positive momentum."
  "RSI shows Overbought: Potential correction soon."

The is_fallback field should be False.

====================================================================
""")
