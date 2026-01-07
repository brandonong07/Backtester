import numpy as np
import pandas as pd
from datetime import datetime
import yfinance as yf
import matplotlib.pyplot as plt


# Download data for SPY, QQQ, and AAPL
ETFs = yf.Tickers("SPY QQQ AAPL")
dfSPY = ETFs.tickers['SPY'].history(period="1y")[['Open', 'High', 'Low', 'Close', 'Volume']]
# dfQQQ = ETFs.tickers['QQQ'].history(period="1y")[['Open', 'High', 'Low', 'Close', 'Volume']]
# dfAAPL = ETFs.tickers['AAPL'].history(period="1y")[['Open', 'High', 'Low', 'Close', 'Volume']]

# 20 & 50 day Moving Average SPY
dfSPY['MA20'] = dfSPY['Close'].rolling(window=20, min_periods=1).mean()
dfSPY['MA50'] = dfSPY['Close'].rolling(window=50, min_periods=1).mean()

# Trading Signals
dfSPY['Signal'] = 0.0
dfSPY["Signal"][20:] = np.where(dfSPY['MA20'][20:] > dfSPY['MA50'][20:], 1.0, 0.0)

# Trading Orders
dfSPY["Position"] = dfSPY["Signal"].diff()

# Plotting Results
plt.figure(figsize=(14, 7))
plt.plot(dfSPY['Close'], label="Close Price")
plt.plot(dfSPY['MA20'], label="20-Day MA")
plt.plot(dfSPY['MA50'], label="50-Day MA")
plt.legend()

# Buy Signals
plt.plot(dfSPY[dfSPY['Position'] == 1].index, 
         dfSPY['MA20'][dfSPY['Position'] == 1], 
         '^', markersize=10, color='g', label='Buy Signal')

# Sell Signals
plt.plot(dfSPY[dfSPY['Position'] == -1].index, 
         dfSPY['MA20'][dfSPY['Position'] == -1],
         'v', markersize=10, color='r', label='Sell Signal')

# Whole Graph
plt.title(f'SPY Moving Average Crossover Strategy')
plt.legend(loc='best')
plt.show()
