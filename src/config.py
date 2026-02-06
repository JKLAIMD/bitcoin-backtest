"""
Configuration module for Bitcoin backtesting with minute-level data
"""
import os
from datetime import datetime, timedelta

# Data configuration
DATA_SYMBOL = "BTC-USD"
# For minute data, we need to limit the date range due to API restrictions
START_DATE = (datetime.now() - timedelta(days=60)).strftime("%Y-%m-%d")  # Last 60 days for minute data
END_DATE = datetime.now().strftime("%Y-%m-%d")

# Data interval options: "1m", "5m", "15m", "30m", "1h", "1d"
INTERVAL = "5m"  # 5-minute intervals

# Strategy parameters
SMA_FAST = 20
SMA_SLOW = 50
RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30
INITIAL_CASH = 10000.0

# Backtesting parameters
COMMISSION = 0.001  # 0.1% commission
STAKE_SIZE = 0.95   # Use 95% of available cash

# Output configuration
OUTPUT_DIR = "results"
PLOT_FILE = "backtest_results.png"
CSV_FILE = "backtest_results.csv"