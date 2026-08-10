# Libraries
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as mpl

# 1. Data Download and Cleaning
def get_OHLCV(ticker="SPY", start_date="2020-01-01", end_date="2026-07-09"):
    # Ticker Data
    data = yf.download(ticker, start=start_date, end=end_date)
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)
    
    data = data.dropna().drop_duplicates().copy()
    data = data.sort_index()
    
    return data

# 2. Indicators Calculation & Signal Generation
def calculate_indicators(df):
    # Calculating 50 and 200 day SMA
    
    df["SMA_50"] = df["Close"].rolling(window=50).mean()
    df["SMA_200"] = df["Close"].rolling(window=200).mean()

    df["Bullish_Crossover"] = (
        (df["SMA_50"] > df["SMA_200"]) &
        (df["SMA_50"].shift(1) <= df["SMA_200"].shift(1))
    )

    df["Bearish_Crossover"] = (
        (df["SMA_50"] < df["SMA_200"]) &
        (df["SMA_50"].shift(1) >= df["SMA_200"].shift(1))
    )

    df["Signal"] = 0
    df.loc[df["Bullish_Crossover"], "Signal"] = 1
    df.loc[df["Bearish_Crossover"], "Signal"] = -1
    
    return df

# 3. Portfolio Simulation & Benchmarking
def simulate_portfolio(df, initial_capital=100000, commission = 0.001):
    in_pos = False
    shares = 0
    cash = initial_capital
    portfolio_values = []
    trade_count = 0
    total_commissions = 0
    
    for index, row in df.iterrows():
        if row["Signal"] == 1 and not in_pos:
            shares = cash // (row["Close"] * (1 + commission))
            cash -= shares * (row["Close"] * (1 + commission))
            total_commissions += shares * (row["Close"] * commission)
            in_pos = True
            trade_count += 1

        elif row["Signal"] == -1 and in_pos:
            cash += shares * (row["Close"] * (1 - commission))
            total_commissions += shares * (row["Close"] * commission)
            in_pos = False 
            shares = 0
            trade_count += 1
        
        portfolio_value = cash+shares * row["Close"]
        portfolio_values.append(portfolio_value)
    
    df["Portfolio Value"] = portfolio_values
    final_value = cash + shares * df.iloc[-1]["Close"]
    print(f"Remaining Cash: ${cash:.2f}")
    print(f"Shares Held: {shares}")
    print(f"Total Commissions: ${total_commissions:.2f}")
    print(f"Final Portfolio Value: ${final_value:.2f}")
    print(f"Total Trades: {trade_count}")
    print(f"Percentage Change: {((final_value - initial_capital) / initial_capital) * 100:.2f}%")
    return df

def buy_and_hold(df, initial_capital=100000, commission = 0.001):
    shares = initial_capital // (df.iloc[0]["Close"] * (1 + commission))
    cash = initial_capital - (shares * df.iloc[0]["Close"] * (1 + commission))
    df["Buy and Hold Value"] = shares * df["Close"] + cash
    return df

def metrics(df):
    # Total return
    total_return = (df["Portfolio Value"].iloc[-1] / df["Portfolio Value"].iloc[0]) - 1

    # CAGR
    CAGR = (df["Portfolio Value"].iloc[-1] / df["Portfolio Value"].iloc[0]) ** (1 / ((df.index[-1] - df.index[0]).days / 365.25)) - 1
    
    # Sharpe Ratio
    daily_returns = df["Portfolio Value"].pct_change().dropna()
    
    annualized_rfr = 0.039 # later can be implemented to use treasury bills from FRED API
    daily_rfr = (1+annualized_rfr) ** (1/252) - 1
    
    
    excess_returns = daily_returns - daily_rfr
    # this calculates the numerator of sharpe ratio, which is return of portfolio - risk-free rate
    # the denominator is the standard deviation of the excess returns, which is a measure of risk
    
    sharpe = (
        excess_returns.mean() / excess_returns.std() * (252 ** 0.5)
    )
    # the reason why sqrt(252) is because there are 252 days in a year 
    
    
    # Volatility -> how much the portfolio value fluctuates over time, measured by standard deviation of daily returns
    volatility = df["Portfolio Value"].pct_change().std() * (252 ** 0.5)

    # Max Drawdown
    rolling_max = df["Portfolio Value"].cummax()
    drawdown = df["Portfolio Value"] / rolling_max - 1
    max_drawdown = drawdown.min()
    
    print(f"Total Return: {total_return * 100:.2f}%")
    print(f"CAGR: {CAGR * 100:.2f}%")
    print(f"Sharpe Ratio: {sharpe:.2f}")
    print(f"Max Drawdown: {max_drawdown * 100:.2f}%")
    print(f"Volatility: {volatility * 100:.2f}%")
    
    metrics = [total_return, CAGR, sharpe, max_drawdown, volatility]
    return metrics

'''
1. Total return
2. CAGR
3. Volatility
4. Sharpe ratio
5. Max drawdown
'''

def main():
    df = get_OHLCV()

    df = calculate_indicators(df)
    
    df = simulate_portfolio(df)
    df = buy_and_hold(df)
    
    metrics(df)
    
    # Comparison between Buy & Hold vs. Moving Average Strategy
    mpl.plot(df.index, df["Portfolio Value"], label="Moving Average Strategy")
    mpl.plot(df.index, df["Buy and Hold Value"], label="Buy and Hold Strategy")
    mpl.title("Portfolio Value Comparison")
    mpl.xlabel("Date")
    mpl.ylabel("Portfolio Value ($)")
    mpl.legend()
    mpl.show()
    
    
if __name__ == "__main__":
    main()