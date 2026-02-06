#!/usr/bin/env python3
"""
Run minute-level Bitcoin backtest with persistent results
"""
import os
import sys
import pandas as pd
from datetime import datetime, timedelta
from src.backtester import BitcoinBacktester
from src.config import START_DATE, END_DATE

def main():
    """Main function to run minute-level backtest"""
    print("🚀 Starting Minute-Level Bitcoin Backtest")
    print(f"Data range: {START_DATE} to {END_DATE}")
    print("-" * 50)
    
    try:
        # Create output directories
        os.makedirs('results', exist_ok=True)
        os.makedirs('plots', exist_ok=True)
        
        # Create backtester instance
        from src.strategies import SMACrossStrategy
        backtester = BitcoinBacktester(strategy_class=SMACrossStrategy)
        
        # Setup components
        backtester.setup_data()
        backtester.setup_strategy()
        backtester.setup_broker()
        backtester.add_analyzers()
        
        # Run backtest
        print("Running backtest...")
        results, final_value = backtester.run_backtest(plot=True)
        
        # Save detailed results
        strat = results[0]
        trades_analyzer = strat.analyzers.trades.get_analysis()
        
        # Extract trade data
        trade_data = []
        if hasattr(trades_analyzer, 'total') and trades_analyzer.total.total > 0:
            # This is simplified - in practice you'd need to track individual trades
            trade_data.append({
                'total_trades': trades_analyzer.total.total,
                'won_trades': trades_analyzer.won.total,
                'lost_trades': trades_analyzer.lost.total,
                'final_portfolio_value': final_value,
                'total_return_pct': (final_value / backtester.cerebro.broker.startingcash - 1) * 100
            })
            
            # Save trade summary
            df_trades = pd.DataFrame(trade_data)
            df_trades.to_csv('results/trade_summary.csv', index=False)
            print(f"✅ Trade summary saved to results/trade_summary.csv")
        
        # Save portfolio value over time
        # Note: Backtrader doesn't directly expose this, but we can get it from the strategy
        portfolio_values = []
        # This would require modifying the strategy to log portfolio values
        
        print("\n🎉 Backtest completed successfully!")
        print(f"Final Portfolio Value: ${final_value:.2f}")
        print(f"Results saved in 'results/' and 'plots/' directories")
        
    except Exception as e:
        print(f"❌ Error during backtest: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()