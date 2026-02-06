"""
Bitcoin backtesting main module - Updated for minute data
"""
import backtrader as bt
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import os
import numpy as np
from src.config import INITIAL_CASH, COMMISSION, STAKE_SIZE, DATA_INTERVAL
from src.strategies import SMACrossStrategy
from src.data_fetcher import fetch_bitcoin_data

class BitcoinBacktester:
    """
    Main backtesting class for Bitcoin strategies with minute data support
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
        
    def run_backtest(self, plot=False, save_results=True):
        """Run the backtest"""
        print(f'Starting Portfolio Value: {self.cerebro.broker.getvalue():.2f}')
        
        # Run backtest
        results = self.cerebro.run()
        strat = results[0]
        
        final_value = self.cerebro.broker.getvalue()
        print(f'Final Portfolio Value: {final_value:.2f}')
        print(f'Total Return: {(final_value / INITIAL_CASH - 1) * 100:.2f}%')
        
        # Print analyzer results
        metrics = self.print_analyzer_results(strat)
        
        if save_results:
            self.save_results_to_csv(metrics, strat)
            
        if plot:
            self.plot_results()
            
        return results, final_value, metrics
        
    def print_analyzer_results(self, strat):
        """Print analyzer results and return metrics dict"""
        metrics = {}
        print('\n=== PERFORMANCE METRICS ===')
        
        # Sharpe Ratio
        sharpe = strat.analyzers.sharpe.get_analysis()
        if sharpe and 'sharperatio' in sharpe:
            sharpe_ratio = sharpe['sharperatio']
            metrics['sharpe_ratio'] = sharpe_ratio if sharpe_ratio else 0
            print(f'Sharpe Ratio: {metrics["sharpe_ratio"]:.4f}')
        else:
            metrics['sharpe_ratio'] = 0
            print('Sharpe Ratio: N/A')
            
        # Drawdown
        drawdown = strat.analyzers.drawdown.get_analysis()
        if drawdown and hasattr(drawdown, 'max'):
            metrics['max_drawdown'] = drawdown.max.drawdown
            metrics['max_drawdown_duration'] = drawdown.max.len
            print(f'Max Drawdown: {metrics["max_drawdown"]:.2f}%')
            print(f'Max Drawdown Duration: {metrics["max_drawdown_duration"]} periods')
        else:
            metrics['max_drawdown'] = 0
            metrics['max_drawdown_duration'] = 0
            
        # Returns
        returns = strat.analyzers.returns.get_analysis()
        if returns and 'rtot' in returns:
            metrics['total_return'] = returns['rtot']
            print(f'Total Return: {metrics["total_return"] * 100:.2f}%')
        else:
            metrics['total_return'] = 0
            
        # Trade Analysis
        trades = strat.analyzers.trades.get_analysis()
        if hasattr(trades, 'total') and trades.total.total > 0:
            metrics['total_trades'] = trades.total.total
            metrics['winning_trades'] = trades.won.total
            metrics['losing_trades'] = trades.lost.total
            metrics['win_rate'] = trades.won.total / trades.total.total if trades.total.total > 0 else 0
            print(f'Total Trades: {metrics["total_trades"]}')
            print(f'Winning Trades: {metrics["winning_trades"]}')
            print(f'Losing Trades: {metrics["losing_trades"]}')
            print(f'Win Rate: {metrics["win_rate"] * 100:.2f}%')
        else:
            metrics['total_trades'] = 0
            metrics['winning_trades'] = 0
            metrics['losing_trades'] = 0
            metrics['win_rate'] = 0
            
        return metrics
        
    def save_results_to_csv(self, metrics, strat):
        """Save backtest results to CSV files"""
        os.makedirs('results', exist_ok=True)
        
        # Save performance metrics
        metrics_df = pd.DataFrame([metrics])
        metrics_df.to_csv('results/performance_metrics.csv', index=False)
        print('Performance metrics saved to results/performance_metrics.csv')
        
        # Save trade history if available
        try:
            # Get equity curve
            equity_curve = []
            for i, value in enumerate(strat.broker.values):
                if i < len(strat.data.datetime.array):
                    dt = bt.num2date(strat.data.datetime.array[i])
                    equity_curve.append({'datetime': dt, 'equity': value})
            
            if equity_curve:
                equity_df = pd.DataFrame(equity_curve)
                equity_df.to_csv('results/equity_curve.csv', index=False)
                print('Equity curve saved to results/equity_curve.csv')
        except Exception as e:
            print(f'Could not save equity curve: {e}')
            
    def plot_results(self):
        """Plot backtest results"""
        os.makedirs('plots', exist_ok=True)
        try:
            figs = self.cerebro.plot(style='candlestick', volume=False)
            if figs:
                fig = figs[0][0]
                fig.savefig('plots/backtest_results.png', dpi=150, bbox_inches='tight')
                plt.close(fig)
                print('Plot saved to plots/backtest_results.png')
        except Exception as e:
            print(f'Could not generate plot: {e}')

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
        results, final_value, metrics = backtester.run_backtest(plot=True, save_results=True)
        
        print('\nBacktest completed successfully!')
        print(f'Results saved to results/ directory')
        print(f'Plot saved to plots/ directory')
        
    except Exception as e:
        print(f'Error during backtest: {e}')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()