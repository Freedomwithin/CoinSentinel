#!/usr/bin/env python3
"""
CoinSentinel - Main entry point
"""

import sys
import os
import traceback
from pathlib import Path

# Add src directory to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

try:
    from main_app_pyqt import main
    
    if __name__ == "__main__":
        print("=" * 60)
        print("CoinSentinel AI - Advanced Cryptocurrency Tracker")
        print("=" * 60)
        print("Starting application...")
        
        # Create data directory if it doesn't exist
        data_dir = Path(__file__).parent / "data"
        data_dir.mkdir(exist_ok=True)
        
        main()
        
except Exception as e:
    print(f"\nError starting CoinSentinel: {e}")
    print("\nTraceback:")
    traceback.print_exc()
    
    print("\nTroubleshooting tips:")
    print("1. Make sure all dependencies are installed: pip install -r requirements.txt")
    print("2. Check your internet connection")
    print("3. Verify API keys if using premium features")
    
    input("\nPress Enter to exit...")