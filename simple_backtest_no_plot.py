#!/usr/bin/env python3
"""
Simple Bitcoin SMA Crossover Backtest (No Plotting)
Generates CSV results only
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime

def calculate_sma(data, period):
    """Calculate Simple Moving Average"""
    return data['price'].rolling(window=period).mean()

def sma_crossover_strategy(data, fast_period=10, slow_period=20, initial_capital=10000):
    """
    Simple Moving Average Crossover Strategy
    Buy when fast SMA crosses above slow SMA
    Sell when fast SMA crosses below slow SMA
    """
    df = data.copy()
    
    # Calculate SMAs
    df['SMA_Fast'] = calculate_sma(df, fast_period)
    df['SMA_Slow'] = calculate_sma(df, slow_period)
    
    # Generate signals
    df['Signal'] = 0
    df['Signal'][fast_period:] = np.where(
        df['SMA_Fast'][fast_period:] > df['SMA_Slow'][fast_period:], 1, 0
    )
    
    # Generate positions (1 for long, 0 for no position)
    df['Position'] = df['Signal'].diff()
    
    # Initialize variables
    cash = initial_capital
    btc_held = 0
    portfolio_value = []
    trades = []
    
    print(f"Starting backtest with ${initial_capital:,.2f}")
    
    for i, row in df.iterrows():
        current_price = row['price']
        
        # Check for buy signal (position = 1)
        if row['Position'] == 1 and cash > 0:
            # Buy BTC
            btc_to_buy = cash / current_price
            btc_held += btc_to_buy
            cash = 0
            trades.append({
                'date': row['date'],
                'action': 'BUY',
                'price': current_price,
                'btc_amount': btc_to_buy,
                'cash_remaining': cash
            })
            print(f"BUY at {row['date']}: ${current_price:,.2f}, BTC: {btc_to_buy:.6f}")
            
        # Check for sell signal (position = -1)
        elif row['Position'] == -1 and btc_held > 0:
            # Sell BTC
            cash_received = btc_held * current_price
            cash += cash_received
            trades.append({
                'date': row['date'],
                'action': 'SELL',
                'price': current_price,
                'btc_amount': btc_held,
                'cash_remaining': cash
            })
            print(f"SELL at {row['date']}: ${current_price:,.2f}, Cash: ${cash:,.2f}")
            btc_held = 0
            
        # Calculate portfolio value
        current_value = cash + (btc_held * current_price)
        portfolio_value.append(current_value)
    
    df['Portfolio_Value'] = portfolio_value
    
    # Calculate performance metrics
    final_value = portfolio_value[-1]
    total_return = (final_value / initial_capital - 1) * 100
    buy_and_hold_value = initial_capital * (df['price'].iloc[-1] / df['price'].iloc[0])
    buy_and_hold_return = (buy_and_hold_value / initial_capital - 1) * 100
    
    print(f"\n=== BACKTEST RESULTS ===")
    print(f"Initial Capital: ${initial_capital:,.2f}")
    print(f"Final Value: ${final_value:,.2f}")
    print(f"Total Return: {total_return:.2f}%")
    print(f"Buy & Hold Return: {buy_and_hold_return:.2f}%")
    print(f"Number of Trades: {len(trades)}")
    
    # Save results to CSV
    os.makedirs('results', exist_ok=True)
    
    # Save portfolio values
    portfolio_df = df[['date', 'price', 'Portfolio_Value']].copy()
    portfolio_df.to_csv('results/portfolio_values.csv', index=False)
    print(f"Portfolio values saved to results/portfolio_values.csv")
    
    # Save trade log
    if trades:
        trades_df = pd.DataFrame(trades)
        trades_df.to_csv('results/trade_log.csv', index=False)
        print(f"Trade log saved to results/trade_log.csv")
    
    # Save strategy signals
    signals_df = df[['date', 'price', 'SMA_Fast', 'SMA_Slow', 'Signal']].copy()
    signals_df.to_csv('results/strategy_signals.csv', index=False)
    print(f"Strategy signals saved to results/strategy_signals.csv")
    
    return {
        'final_value': final_value,
        'total_return': total_return,
        'buy_and_hold_return': buy_and_hold_return,
        'num_trades': len(trades)
    }

def main():
    """Main function to run the backtest"""
    print("Starting Bitcoin SMA Crossover Backtest...")
    
    # Load data
    data_file = 'data/btc_daily.csv'
    if not os.path.exists(data_file):
        print(f"Error: {data_file} not found!")
        return
    
    df = pd.read_csv(data_file)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date').reset_index(drop=True)
    
    print(f"Loaded data from {data_file}")
    print(f"Data shape: {df.shape}")
    print(f"Date range: {df['date'].min()} to {df['date'].max()}")
    
    # Run backtest
    results = sma_crossover_strategy(df, fast_period=5, slow_period=15)
    
    print("\nBacktest completed successfully!")

if __name__ == "__main__":
    main()