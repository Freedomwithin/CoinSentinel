#!/bin/bash

# Navigate to the project directory
cd "/Users/useername/CoinSentinel" || exit

# Activate the virtual environment
source venv/bin/activate

# Update pip & Install Dependencies 
pip install --update pip 
pip install -r requirements.txt

# Run the Python script
python main_app_pyqt.py

