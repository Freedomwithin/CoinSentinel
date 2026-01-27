# run.py
#!/usr/bin/env python3
"""
CoinSentinel - Advanced Cryptocurrency Tracking & Analysis
Main entry point for the application.
"""

import sys
import os
import traceback

def setup_environment():
    """Setup the Python environment for the application."""
    # Add src directory to Python path
    src_path = os.path.join(os.path.dirname(__file__), 'src')
    if src_path not in sys.path:
        sys.path.insert(0, src_path)
    
    # Verify Python version
    if sys.version_info < (3, 8):
        print("Error: CoinSentinel requires Python 3.8 or higher")
        print(f"Current version: {sys.version}")
        sys.exit(1)
    
    # Map PyPI package names to importable module names
    required_packages = {
        "PyQt5": "PyQt5",
        "pandas": "pandas",
        "numpy": "numpy",
        "scikit-learn": "sklearn",       # PyPI name -> import name
        "matplotlib": "matplotlib",
        "plyer": "plyer",
        "pycoingecko": "pycoingecko"
    }

    missing_packages = []
    for pkg_name, import_name in required_packages.items():
        try:
            __import__(import_name)
        except ImportError:
            missing_packages.append(pkg_name)
    
    if missing_packages:
        print(f"Error: Missing required packages: {', '.join(missing_packages)}")
        print("\nPlease install requirements:")
        print("  pip install -r requirements.txt")
        sys.exit(1)

if __name__ == "__main__":
    setup_environment()
    
    # Import and run the main application
    try:
        from src.main_app_pyqt import main
        main()
    except Exception as e:
        print(f"Error starting CoinSentinel: {e}")
        traceback.print_exc()
        sys.exit(1)
