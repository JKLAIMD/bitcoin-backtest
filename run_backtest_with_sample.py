#!/usr/bin/env python3
"""
Bitcoin backtest using sample data
This script demonstrates the complete workflow with persistent CSV and image output
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
from datetime import datetime, timedelta

def create_sample_data():
    """Create sample Bitcoin minute data for demonstration"""
    # Create 30 days of hourly data (simulating minute data for demo)
    dates = pd.date_range(start='2026-01-01', end='2026-01-30', freq='1H')
    np.random.seed(42)
    
    # Generate realistic price movements
    base_price = 45000
    returns = np.random.normal(0, 0.02, len(dates))  # 2% daily volatility
    prices = [base_price]
    
    for r in returns[1:]:
        new_price = prices[-1] * (1 + r)
        prices.append(new_price)
    
    # Create OHLC data
    open_prices = prices[:-1]
    close_prices = prices[1:]
    high_prices = [max(o, c) * (1 + abs(np.random.normal(0, 0.005))) for o, c in zip(open_prices, close_prices)]
    low_prices = [min(o, c) * (1 - abs(np.random.normal(0, 0.005))) for o, c in zip(open_prices, close_prices)]
    volume = np.random.exponential(1000, len(open_prices))
    
    df = pd.DataFrame({
        'timestamp': dates[:-1],
        'open': open_prices,
        'high': high_prices,
        'low': low_prices,
        'close': close_prices,
        'volume': volume
    })
    
    return df

def sma_crossover_strategy(data, fast_period=20, slow_period=50):
    """Simple SMA crossover strategy"""
    df = data.copy()
    df['sma_fast'] = df['close'].rolling(window=fast_period).mean()
    df['sma_slow'] = df['close'].rolling(window=slow_period).mean()
    
    # Generate signals
    df['signal'] = 0
    df['signal'][fast_period:] = np.where(
        df['sma_fast'][fast_period:] > df['sma_slow'][fast_period:], 1, 0
    )
    
    # Generate positions
    df['position'] = df['signal'].diff()
    
    return df

def backtest_strategy(data, initial_capital=10000):
    """Run backtest and calculate performance metrics"""
    df = data.copy()
    
    # Calculate returns
    df['returns'] = df['close'].pct_change()
    df['strategy_returns'] = df['signal'].shift(1) * df['returns']
    
    # Calculate equity curve
    df['cumulative_returns'] = (1 + df['strategy_returns']).cumprod()
    df['equity'] = initial_capital * df['cumulative_returns']
    
    # Performance metrics
    total_return = df['equity'].iloc[-1] / initial_capital - 1
    sharpe_ratio = df['strategy_returns'].mean() / df['strategy_returns'].std() * np.sqrt(252*24)  # hourly data
    
    max_drawdown = (df['equity'] / df['equity'].cummax() - 1).min()
    
    results = {
        'total_return': total_return,
        'sharpe_ratio': sharpe_ratio,
        'max_drawdown': max_drawdown,
        'final_equity': df['equity'].iloc[-1],
        'initial_capital': initial_capital
    }
    
    return df, results

def plot_results(data, results, filename='plots/backtest_results.png'):
    """Create plots and save to file"""
    os.makedirs('plots', exist_ok=True)
    
    fig, axes = plt.subplots(2, 1, figsize=(12, 10))
    
    # Price and SMAs
    axes[0].plot(data['timestamp'], data['close'], label='Price', alpha=0.7)
    axes[0].plot(data['timestamp'], data['sma_fast'], label='SMA Fast (20)', alpha=0.8)
    axes[0].plot(data['timestamp'], data['sma_slow'], label='SMA Slow (50)', alpha=0.8)
    
    # Buy signals
    buy_signals = data[data['position'] == 1]
    if not buy_signals.empty:
        axes[0].scatter(buy_signals['timestamp'], buy_signals['close'], 
                       color='green', marker='^', s=100, label='Buy')
    
    # Sell signals  
    sell_signals = data[data['position'] == -1]
    if not sell_signals.empty:
        axes[0].scatter(sell_signals['timestamp'], sell_signals['close'], 
                       color='red', marker='v', s=100, label='Sell')
    
    axes[0].set_title('Bitcoin Price with SMA Crossover Strategy')
    axes[0].set_ylabel('Price (USD)')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    # Equity curve
    axes[1].plot(data['timestamp'], data['equity'], label='Strategy Equity', color='blue')
    axes[1].axhline(y=results['initial_capital'], color='black', linestyle='--', alpha=0.5, label='Initial Capital')
    axes[1].set_title(f'Equity Curve (Total Return: {results["total_return"]:.2%})')
    axes[1].set_ylabel('Equity (USD)')
    axes[1].set_xlabel('Date')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"Plot saved to {filename}")

def save_results_to_csv(data, results, filename='results/backtest_results.csv'):
    """Save detailed results to CSV"""
    os.makedirs('results', exist_ok=True)
    
    # Save trading signals and equity
    output_df = data[['timestamp', 'open', 'high', 'low', 'close', 'volume', 
                     'sma_fast', 'sma_slow', 'signal', 'position', 'equity']].copy()
    output_df.to_csv(filename, index=False)
    
    # Save summary metrics
    summary_file = 'results/backtest_summary.csv'
    summary_df = pd.DataFrame([results])
    summary_df.to_csv(summary_file, index=False)
    
    print(f"Detailed results saved to {filename}")
    print(f"Summary saved to {summary_file}")

def main():
    """Main execution function"""
    print("Starting Bitcoin SMA Crossover Backtest...")
    
    # Load or create data
    data_file = 'data/btc_daily.csv'
    if os.path.exists(data_file):
        print(f"Loading data from {data_file}")
        df = pd.read_csv(data_file)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
    else:
        print("Creating sample data for demonstration")
        df = create_sample_data()
        os.makedirs('data', exist_ok=True)
        df.to_csv(data_file, index=False)
        print(f"Sample data saved to {data_file}")
    
    print(f"Data shape: {df.shape}")
    print(f"Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")
    
    # Apply strategy
    print("Applying SMA crossover strategy...")
    strategy_df = sma_crossover_strategy(df)
    
    # Run backtest
    print("Running backtest...")
    backtest_df, results = backtest_strategy(strategy_df)
    
    # Display results
    print("\n=== BACKTEST RESULTS ===")
    print(f"Initial Capital: ${results['initial_capital']:,.2f}")
    print(f"Final Equity: ${results['final_equity']:,.2f}")
    print(f"Total Return: {results['total_return']:.2%}")
    print(f"Sharpe Ratio: {results['sharpe_ratio']:.2f}")
    print(f"Max Drawdown: {results['max_drawdown']:.2%}")
    
    # Save outputs
    plot_results(backtest_df, results)
    save_results_to_csv(backtest_df, results)
    
    print("\nBacktest completed successfully!")
    print("Check the 'plots/' and 'results/' directories for outputs.")

if __name__ == "__main__":
    main()