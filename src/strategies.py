"""
Bitcoin trading strategies module
"""
import backtrader as bt
import pandas as pd
from src.config import SMA_FAST, SMA_SLOW

class SMACrossStrategy(bt.Strategy):
    """
    Simple Moving Average Crossover Strategy
    Buy when fast SMA crosses above slow SMA
    Sell when fast SMA crosses below slow SMA
    """
    
    params = (
        ('fast_period', SMA_FAST),
        ('slow_period', SMA_SLOW),
        ('printlog', False),
    )
    
    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.data_close = self.datas[0].close
        
        # To keep track of pending orders and buy price/commission
        self.order = None
        self.buy_price = None
        self.buy_comm = None
        
        # Add a MovingAverageSimple indicator
        self.sma_fast = bt.indicators.SimpleMovingAverage(
            self.datas[0], period=self.params.fast_period)
        self.sma_slow = bt.indicators.SimpleMovingAverage(
            self.datas[0], period=self.params.slow_period)
            
        # Indicators for plotting
        bt.indicators.ExponentialMovingAverage(self.datas[0], period=21)
        bt.indicators.RSI(self.datas[0])
        
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return
            
        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm))
                     
                self.buy_price = order.executed.price
                self.buy_comm = order.executed.comm
            else:  # Sell
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))
                          
            self.bar_executed = len(self)
            
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')
            
        # Write down: no pending order
        self.order = None
        
    def notify_trade(self, trade):
        if not trade.isclosed:
            return
            
        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                 (trade.pnl, trade.pnlcomm))
                 
    def next(self):
        # Simply log the closing price of the series from the reference
        self.log('Close, %.2f' % self.data_close[0])
        
        # Check if an order is pending ... if yes, we cannot send a 2nd one
        if self.order:
            return
            
        # Check if we are in the market
        if not self.position:
            # Not yet ... we MIGHT BUY if ...
            if self.sma_fast[0] > self.sma_slow[0]:
                # BUY, BUY, BUY!!! (with all possible default parameters)
                self.log('BUY CREATE, %.2f' % self.data_close[0])
                
                # Keep track of the created order to avoid a 2nd order
                self.order = self.buy()
        else:
            # Already in the market ... we might sell
            if self.sma_fast[0] < self.sma_slow[0]:
                # SELL, SELL, SELL!!! (with all possible default parameters)
                self.log('SELL CREATE, %.2f' % self.data_close[0])
                
                # Keep track of the created order to avoid a 2nd order
                self.order = self.sell()
                
    def log(self, txt, dt=None, doprint=False):
        ''' Logging function fot this strategy'''
        if self.params.printlog or doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print('%s, %s' % (dt.isoformat(), txt))