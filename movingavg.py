import numpy as np
import pandas as pd
from datetime import datetime
import yfinance as yf
import matplotlib.pyplot as plt
import backtrader as bt

class Backtester:
    def __init__(self, data):
        self.data = data
        