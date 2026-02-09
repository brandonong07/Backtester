from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import numpy as np
import pandas as pd
from datetime import datetime
import yfinance as yf
import os.path
import sys
import matplotlib.pyplot as plt
import backtrader as bt

# Backtester Class
class Backtester:
    def __init__(self, data):
        self.data = data

    def engine(self, strategy):
        # Initialization
        cerebro = bt.Cerebro()
        cerebro.broker.setcommission(commission=0.001)  # Set the commission to 0.1%
        cerebro.broker.setcash(100000.0)

        # Convert DataFrame to Backtrader format

        data_feed = bt.feeds.PandasData(dataname=self.data)

        cerebro.adddata(data_feed)
        print("Data loaded successfully.")

        # Starting Value:
        print(f"Starting Portfolio Value: {cerebro.broker.getvalue():.2f}")
        
        cerebro.addstrategy(strategy)
        cerebro.run()

        # Ending Value:
        print(f"End Portfolio Value: {cerebro.broker.getvalue():.2f}")
        print("Backtesting completed successfully.")

# Strategy Class
class TestStrategy(bt.Strategy):

    def log(self, txt, dt=None):
        ''' Logging function for this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close
        self.order = None # Track pending orders
        StochasticFull = bt.indicators.StochasticFull(self.datas[0])
        self.stochastic = StochasticFull

    def next(self):
        # Simply log the closing price of the series from the reference
        self.log('Close, %.2f' % self.dataclose[0])

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log('BUY EXECUTED, %.2f' % order.executed.price)
            elif order.issell():
                self.log('SELL EXECUTED, %.2f' % order.executed.price)

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # Write down: no pending order
        self.order = None
    
    def next(self):
        self.log('Close, %.2f' % self.dataclose[0])
        
        if self.order:
            return
        if not self.position: # Not in the market   
            if self.stochastic.percK[0] < 20 and self.stochastic.percD[0] < 20: # Oversold condition
                self.log('BUY SIGNAL DETECTED, %.2f' % self.dataclose[0])
                self.buy()
        else:
            if self.stochastic.percK[0] > 80 and self.stochastic.percD[0] > 80: # Overbought condition
                self.log('SELL SIGNAL DETECTED, %.2f' % self.dataclose[0])
                self.sell()

# Main Function
def main():
    data = yf.download('AAPL', start='2020-01-01', end='2021-01-01')
    
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)
    
    backtester = Backtester(data)
    backtester.engine(strategy=TestStrategy)  # Replace None with your strategy class

if __name__ == "__main__": main()