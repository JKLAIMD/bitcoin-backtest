"""
Data fetching module for Bitcoin price data with minute-level support
"""
import yfinance as yf
import pandas as pd
import os
from src.config import DATA_SYMBOL, START_DATE, END_DATE, INTERVAL

def fetch_bitcoin_data():
    """
    Fetch Bitcoin price data from Yahoo Finance with specified interval
    Returns:
        pd.DataFrame: Bitcoin OHLCV data
    """
    print(f"Fetching {DATA_SYMBOL} data from {START_DATE} to {END_DATE} with {INTERVAL} interval")
    
    try:
        # For minute data, Yahoo Finance has limitations:
        # - 1m interval: max 7 days of data
        # - 2m interval: max 60 days of data  
        # - 5m, 15m, 30m, 60m, 90m: max 60 days of data
        # For longer periods, we need to use daily data or combine multiple requests
        
        if INTERVAL == '1m':
            # For 1-minute data, limit to last 7 days
            from datetime import datetime, timedelta
            end_date = datetime.now()
            start_date = end_date - timedelta(days=7)
            btc_data = yf.download(
                DATA_SYMBOL,
                start=start_date.strftime('%Y-%m-%d'),
                end=end_date.strftime('%Y-%m-%d'),
                interval=INTERVAL
            )
        elif INTERVAL in ['2m', '5m', '15m', '30m', '60m', '90m']:
            # For other minute intervals, limit to last 60 days
            from datetime import datetime, timedelta
            end_date = datetime.now()
            start_date = end_date - timedelta(days=60)
            btc_data = yf.download(
                DATA_SYMBOL,
                start=start_date.strftime('%Y-%m-%d'),
                end=end_date.strftime('%Y-%m-%d'),
                interval=INTERVAL
            )
        else:
            # For daily or higher intervals, use the configured dates
            btc_data = yf.download(
                DATA_SYMBOL,
                start=START_DATE,
                end=END_DATE,
                interval=INTERVAL
            )
        
        if btc_data.empty:
            raise ValueError("No data returned from Yahoo Finance")
            
        print(f"Successfully fetched {len(btc_data)} data points")
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

def load_data_from_csv(filename="data/btc_data.csv"):
    """
    Load data from CSV file
    """
    if os.path.exists(filename):
        return pd.read_csv(filename, index_col=0, parse_dates=True)
    return None

if __name__ == "__main__":
    data = fetch_bitcoin_data()
    if data is not None:
        save_data_to_csv(data)