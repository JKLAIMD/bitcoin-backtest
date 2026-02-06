"""
Data fetching module for Bitcoin price data
"""
import yfinance as yf
import pandas as pd
from src.config import DATA_SYMBOL, START_DATE, END_DATE

def fetch_bitcoin_data():
    """
    Fetch Bitcoin price data from Yahoo Finance
    Returns:
        pd.DataFrame: Bitcoin OHLCV data
    """
    print(f"Fetching {DATA_SYMBOL} data from {START_DATE} to {END_DATE}")
    
    try:
        btc_data = yf.download(
            DATA_SYMBOL,
            start=START_DATE,
            end=END_DATE,
            interval="1d"
        )
        
        if btc_data.empty:
            raise ValueError("No data returned from Yahoo Finance")
            
        print(f"Successfully fetched {len(btc_data)} days of data")
        return btc_data
        
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

def save_data_to_csv(data, filename="data/btc_data.csv"):
    """
    Save fetched data to CSV file
    """
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    data.to_csv(filename)
    print(f"Data saved to {filename}")

if __name__ == "__main__":
    import os
    data = fetch_bitcoin_data()
    if data is not None:
        save_data_to_csv(data)