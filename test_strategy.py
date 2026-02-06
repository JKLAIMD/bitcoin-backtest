#!/usr/bin/env python3
"""
Simple test script for the Bitcoin backtesting strategy
"""
from src.backtester import BitcoinBacktester

def test_backtester_initialization():
    """Test if backtester can be initialized"""
    try:
        backtester = BitcoinBacktester()
        print("✓ Backtester initialized successfully")
        return True
    except Exception as e:
        print(f"✗ Backtester initialization failed: {e}")
        return False

def test_config_import():
    """Test if config can be imported"""
    try:
        from src.config import DATA_SYMBOL, SMA_FAST, SMA_SLOW
        print(f"✓ Config imported: {DATA_SYMBOL}, SMA({SMA_FAST}, {SMA_SLOW})")
        return True
    except Exception as e:
        print(f"✗ Config import failed: {e}")
        return False

if __name__ == "__main__":
    print("Running basic tests...")
    
    success = True
    success &= test_config_import()
    success &= test_backtester_initialization()
    
    if success:
        print("\n✓ All basic tests passed!")
        print("The project structure is ready for development.")
    else:
        print("\n✗ Some tests failed. Please check the errors above.")