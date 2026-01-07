import numpy as np
import pandas as pd
from datetime import datetime
import yfinance as yf
import matplotlib.pyplot as plt

class Backtester:
    short = None
    long = None

    
    def __init__(self, ticker, start_date, end_date):
        self.ticker = ticker
        self.data = self.load_data(ticker,start_date, end_date)
    
    def load_data(self, ticker, start, end):
        data = yf.download(ticker, start=start, end=end)
        return data
    
    def moving_average(self, short_length, long_length):
        self.short = short_length
        self.long = long_length

        self.data['MA_short'] = self.data['Close'].rolling(window=self.short, min_periods=1).mean()
        self.data['MA_long'] = self.data['Close'].rolling(window=self.long, min_periods=1).mean()

    def calculate_metrics(self):   
        
        pass

    def plot_results(self):
        self.data['Signal'] = 0.0
        self.data['Signal'][self.short:] = np.where(self.data['MA_short'][self.short:] 
                                                    > self.data['MA_long'][self.short:], 1.0, 0.0)
        self.data['Position'] = self.data['Signal'].diff()
        
        plt.figure(figsize=(14, 7))
        plt.plot(self.data['Close'], label="Close Price")
        plt.plot(self.data['MA_short'], label="Short-Term MA")
        plt.plot(self.data['MA_long'], label="Long-Term MA")

        # Buy Signals and Sell Signals
        plt.plot(self.data[self.data['Position'] == 1].index, 
                 self.data['MA_short'][self.data['Position'] == 1], 
                 '^', markersize=10, color='g', label='buy')
        
        plt.plot(self.data[self.data['Position'] == -1].index, 
                 self.data['MA_short'][self.data['Position'] == -1],
                    'v', markersize=10, color='r', label='sell')
        
        # Whole Graph
        plt.title(f'{self.ticker} Moving Average Crossover Strategy')
        plt.legend(loc='best')
        plt.show()


# Usage
bt = Backtester('SPY', '2023-01-01', '2024-01-01')
bt.moving_average(short_length=20, long_length=50)
bt.plot_results()
bt.portfolio_results()
