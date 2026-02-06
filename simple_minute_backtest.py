#!/usr/bin/env python3
"""
Simple Bitcoin minute-level backtesting script
Minimal dependencies: only yfinance, pandas, matplotlib
"""

import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from datetime import datetime, timedelta

def fetch_bitcoin_minute_data(period_days=7):
    """
    Fetch Bitcoin minute-level data from Yahoo Finance
    Note: Yahoo Finance provides up to 7 days of 1-minute data
    """
    print(f"Fetching {period_days} days of Bitcoin minute data...")
    
    # Yahoo Finance limits: max 7 days for 1-minute intervals
    end_date = datetime.now()
    start_date = end_date - timedelta(days=period_days)
    
    try:
        # Fetch BTC-USD data with 1-minute interval
        btc_data = yf.download(
            "BTC-USD",
            start=start_date,
            end=end_date,
            interval="1m",
            auto_adjust=True
        )
        
        if btc_data.empty:
            print("No data returned")
            return None
            
        print(f"Fetched {len(btc_data)} minutes of data")
        return btc_data
        
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

def simple_sma_strategy(data, fast_period=20, slow_period=50):
    """
    Simple SMA crossover strategy
    """
    # Calculate SMAs
    data['SMA_Fast'] = data['Close'].rolling(window=fast_period).mean()
    data['SMA_Slow'] = data['Close'].rolling(window=slow_period).mean()
    
    # Generate signals
    data['Signal'] = 0
    data['Signal'][fast_period:] = np.where(
        data['SMA_Fast'][fast_period:] > data['SMA_Slow'][fast_period:], 1, 0
    )
    
    # Generate positions
    data['Position'] = data['Signal'].diff()
    
    return data

def calculate_returns(data, initial_capital=10000):
    """
    Calculate strategy returns
    """
    # Calculate daily returns
    data['Returns'] = data['Close'].pct_change()
    data['Strategy_Returns'] = data['Returns'] * data['Signal'].shift(1)
    
    # Calculate cumulative returns
    data['Cumulative_Returns'] = (1 + data['Returns']).cumprod()
    data['Cumulative_Strategy_Returns'] = (1 + data['Strategy_Returns']).cumprod()
    
    # Calculate portfolio value
    data['Portfolio_Value'] = initial_capital * data['Cumulative_Strategy_Returns']
    
    return data

def save_results(data, output_dir='results'):
    """
    Save results to CSV and generate plots
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Save raw data with signals
    csv_path = os.path.join(output_dir, 'bitcoin_backtest_results.csv')
    data.to_csv(csv_path)
    print(f"Results saved to {csv_path}")
    
    # Generate plot
    plt.figure(figsize=(15, 10))
    
    # Price and SMAs
    plt.subplot(2, 1, 1)
    plt.plot(data.index, data['Close'], label='BTC Price', alpha=0.7)
    plt.plot(data.index, data['SMA_Fast'], label=f'SMA {20}', alpha=0.8)
    plt.plot(data.index, data['SMA_Slow'], label=f'SMA {50}', alpha=0.8)
    
    # Buy signals
    buy_signals = data[data['Position'] == 1]
    plt.scatter(buy_signals.index, buy_signals['Close'], 
                color='green', marker='^', s=100, label='Buy')
    
    # Sell signals  
    sell_signals = data[data['Position'] == -1]
    plt.scatter(sell_signals.index, sell_signals['Close'], 
                color='red', marker='v', s=100, label='Sell')
    
    plt.title('Bitcoin Minute-Level SMA Crossover Strategy')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Portfolio value
    plt.subplot(2, 1, 2)
    plt.plot(data.index, data['Portfolio_Value'], label='Portfolio Value', color='blue')
    plt.title('Portfolio Value Over Time')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plot_path = os.path.join(output_dir, 'backtest_results.png')
    plt.savefig(plot_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Plot saved to {plot_path}")

def main():
    """
    Main backtesting function
    """
    print("Starting Bitcoin minute-level backtest...")
    
    # Fetch data
    data = fetch_bitcoin_minute_data(period_days=7)
    if data is None:
        print("Failed to fetch data")
        return
    
    # Apply strategy
    data = simple_sma_strategy(data)
    
    # Calculate returns
    data = calculate_returns(data)
    
    # Save results
    save_results(data)
    
    # Print summary statistics
    total_return = (data['Portfolio_Value'].iloc[-1] / 10000 - 1) * 100
    buy_trades = len(data[data['Position'] == 1])
    sell_trades = len(data[data['Position'] == -1])
    
    print("\n=== BACKTEST SUMMARY ===")
    print(f"Total Return: {total_return:.2f}%")
    print(f"Number of Buy Signals: {buy_trades}")
    print(f"Number of Sell Signals: {sell_trades}")
    print(f"Final Portfolio Value: ${data['Portfolio_Value'].iloc[-1]:.2f}")
    print("Backtest completed successfully!")

if __name__ == "__main__":
    main()