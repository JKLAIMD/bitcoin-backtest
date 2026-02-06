#!/usr/bin/env python3
"""
Basic test script to verify dependencies and data fetching
"""
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import yfinance as yf
    print("✓ yfinance imported successfully")
    
    import pandas as pd
    print("✓ pandas imported successfully")
    
    import numpy as np
    print("✓ numpy imported successfully")
    
    # Test data fetching
    print("Fetching BTC minute data...")
    btc = yf.Ticker("BTC-USD")
    
    # Get last 7 days of 1-minute data
    hist = btc.history(period="7d", interval="1m")
    print(f"✓ Fetched {len(hist)} minutes of data")
    print(f"Data shape: {hist.shape}")
    print(f"Columns: {list(hist.columns)}")
    print(f"Date range: {hist.index[0]} to {hist.index[-1]}")
    
    # Save to CSV
    hist.to_csv("data/btc_minute_data.csv")
    print("✓ Data saved to data/btc_minute_data.csv")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()