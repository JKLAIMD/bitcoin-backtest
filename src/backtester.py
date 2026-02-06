"""
Bitcoin backtesting main module
"""
import backtrader as bt
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import os
from src.config import INITIAL_CASH, COMMISSION, STAKE_SIZE
from src.strategies import SMACrossStrategy
from src.data_fetcher import fetch_bitcoin_data

class BitcoinBacktester:
    """
    Main backtesting class for Bitcoin strategies
    """
    
    def __init__(self, strategy_class=SMACrossStrategy):
        self.strategy_class = strategy_class
        self.cerebro = bt.Cerebro()
        self.data = None
        
    def setup_data(self, data=None):
        """Setup data feed for backtesting"""
        if data is None:
            data = fetch_bitcoin_data()
            
        if data is None:
            raise ValueError("No data available for backtesting")
            
        self.data = data
        
        # Convert to Backtrader format
        data_feed = bt.feeds.PandasData(dataname=data)
        self.cerebro.adddata(data_feed)
        
    def setup_strategy(self, **kwargs):
        """Setup strategy with parameters"""
        self.cerebro.addstrategy(self.strategy_class, **kwargs)
        
    def setup_broker(self):
        """Setup broker with initial cash and commission"""
        self.cerebro.broker.setcash(INITIAL_CASH)
        self.cerebro.broker.setcommission(commission=COMMISSION)
        self.cerebro.addsizer(bt.sizers.PercentSizer, percents=STAKE_SIZE * 100)
        
    def add_analyzers(self):
        """Add performance analyzers"""
        self.cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
        self.cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
        self.cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
        self.cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
        
    def run_backtest(self, plot=False):
        """Run the backtest"""
        print(f'Starting Portfolio Value: {self.cerebro.broker.getvalue():.2f}')
        
        # Run backtest
        results = self.cerebro.run()
        strat = results[0]
        
        final_value = self.cerebro.broker.getvalue()
        print(f'Final Portfolio Value: {final_value:.2f}')
        print(f'Total Return: {(final_value / INITIAL_CASH - 1) * 100:.2f}%')
        
        # Print analyzer results
        self.print_analyzer_results(strat)
        
        if plot:
            self.plot_results()
            
        return results, final_value
        
    def print_analyzer_results(self, strat):
        """Print analyzer results"""
        print('\n=== PERFORMANCE METRICS ===')
        
        # Sharpe Ratio
        sharpe = strat.analyzers.sharpe.get_analysis()
        if sharpe:
            print(f'Sharpe Ratio: {sharpe.get("sharperatio", "N/A")}')
            
        # Drawdown
        drawdown = strat.analyzers.drawdown.get_analysis()
        if drawdown:
            print(f'Max Drawdown: {drawdown.max.drawdown:.2f}%')
            print(f'Max Drawdown Duration: {drawdown.max.len} days')
            
        # Returns
        returns = strat.analyzers.returns.get_analysis()
        if returns:
            print(f'Annual Return: {returns.get("rtot", 0) * 100:.2f}%')
            
        # Trade Analysis
        trades = strat.analyzers.trades.get_analysis()
        if trades.total.total > 0:
            print(f'Total Trades: {trades.total.total}')
            print(f'Winning Trades: {trades.won.total}')
            print(f'Losing Trades: {trades.lost.total}')
            
    def plot_results(self):
        """Plot backtest results"""
        os.makedirs('plots', exist_ok=True)
        fig = self.cerebro.plot(style='candlestick')[0][0]
        fig.savefig('plots/backtest_results.png')
        plt.close(fig)
        print('Plot saved to plots/backtest_results.png')

def main():
    """Main function to run backtest"""
    try:
        # Create backtester instance
        backtester = BitcoinBacktester()
        
        # Setup components
        backtester.setup_data()
        backtester.setup_strategy()
        backtester.setup_broker()
        backtester.add_analyzers()
        
        # Run backtest
        results, final_value = backtester.run_backtest(plot=True)
        
        print('\nBacktest completed successfully!')
        
    except Exception as e:
        print(f'Error during backtest: {e}')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()