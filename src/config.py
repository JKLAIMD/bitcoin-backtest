"""
Configuration module for Bitcoin backtesting
"""
import os
from datetime import datetime, timedelta

# Data configuration
DATA_SYMBOL = "BTC-USD"
START_DATE = "2020-01-01"
END_DATE = datetime.now().strftime("%Y-%m-%d")

# Strategy parameters
SMA_FAST = 20
SMA_SLOW = 50
INITIAL_CASH = 10000.0

# Backtesting parameters
COMMISSION = 0.001  # 0.1% commission
STAKE_SIZE = 0.95   # Use 95% of available cash