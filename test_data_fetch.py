#!/usr/bin/env python3
"""
Test script to fetch minute-level Bitcoin data
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.data_fetcher import fetch_bitcoin_minute_data
from src.config import START_DATE, END_DATE

def main():
    print(f"Fetching minute-level BTC data from {START_DATE} to {END_DATE}")
    print("This may take a while due to Yahoo Finance rate limits...")
    
    data = fetch_bitcoin_minute_data()
    if data is not None:
        print(f"Successfully fetched {len(data)} minutes of data")
        print(f"Data shape: {data.shape}")
        print(f"Date range: {data.index[0]} to {data.index[-1]}")
        print(f"Columns: {list(data.columns)}")
        
        # Save to CSV
        os.makedirs('data', exist_ok=True)
        data.to_csv('data/btc_minute_data.csv')
        print("Data saved to data/btc_minute_data.csv")
    else:
        print("Failed to fetch data")

if __name__ == "__main__":
    main()