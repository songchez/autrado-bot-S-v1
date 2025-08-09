# backtesting_bot.py

import yfinance as yf
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import sys
import os

# 상위 디렉토리의 strategies 모듈을 import하기 위해 경로 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies import TrendFollowing


# 호환성을 위해 유지 (제거 예정)
class TrendFollowing_Legacy(Strategy):
    short_ma = 50  # Default short moving average period
    long_ma = 200  # Default long moving average period

    def init(self):
        self.ma_short = self.I(lambda x: pd.Series(x).rolling(self.short_ma).mean(), self.data.Close)
        self.ma_long = self.I(lambda x: pd.Series(x).rolling(self.long_ma).mean(), self.data.Close)

    def next(self):
        if crossover(self.ma_short, self.ma_long):
            self.buy()
        elif crossover(self.ma_long, self.ma_short):
            self.sell()


class BacktestingBot:
    def __init__(self):
        self.stats = None
        self.trades = None

    def run_backtest(self, ticker="AAPL", start_date="2010-01-01", end_date="2023-12-31", 
                    short_ma=50, long_ma=200, cash=10000, commission=0.002):
        try:
            TrendFollowing.short_ma = short_ma
            TrendFollowing.long_ma = long_ma

            print(f"Downloading data for {ticker} from {start_date} to {end_date}...")
            data = yf.download(ticker, start=start_date, end=end_date)
            if data.empty:
                raise ValueError("No data downloaded. Check ticker and dates.")
            
            # Fix MultiIndex columns issue
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.droplevel(1)

            print("Running backtest...")
            bt = Backtest(data, TrendFollowing, cash=cash, commission=commission)
            self.stats = bt.run()
            self.trades = self.stats["_trades"] if "_trades" in self.stats else None

            self.display_results()
            self.visualize_returns()
            return self.stats

        except Exception as e:
            print(f"Error: {e}")
            return None

    def display_results(self):
        if self.stats is None:
            return
            
        print("\n" + "="*50)
        print("BACKTEST RESULTS")
        print("="*50)
        print(f"Total Return: {self.stats['Return [%]']:.2f}%")
        print(f"Win Rate: {self.stats['Win Rate [%]']:.2f}%")
        print(f"Max Drawdown: {self.stats['Max. Drawdown [%]']:.2f}%")
        print(f"Number of Trades: {self.stats['# Trades']}")
        print(f"Sharpe Ratio: {self.stats['Sharpe Ratio']:.2f}")
        print("="*50)

    def visualize_returns(self):
        if self.trades is not None and not self.trades.empty:
            returns = self.trades["ReturnPct"] * 100
            plt.figure(figsize=(10, 6))
            plt.hist(returns, bins=20, edgecolor="black", alpha=0.7)
            plt.title("Trade Returns Distribution")
            plt.xlabel("Return (%)")
            plt.ylabel("Frequency")
            plt.grid(True, alpha=0.3)
            plt.savefig("trade_returns_distribution.png", dpi=300, bbox_inches='tight')
            print("Chart saved as 'trade_returns_distribution.png'")
            plt.close()

    def save_results(self, filename="backtest_results.txt"):
        if self.stats is None:
            print("No results to save.")
            return
            
        with open(filename, "w") as f:
            f.write(str(self.stats))
        print(f"Results saved to {filename}")


def main():
    bot = BacktestingBot()
    
    print("Stock Backtesting Bot")
    print("="*30)
    
    ticker = input("Enter stock ticker (default: AAPL): ").strip() or "AAPL"
    start_date = input("Enter start date (YYYY-MM-DD, default: 2010-01-01): ").strip() or "2010-01-01"
    end_date = input("Enter end date (YYYY-MM-DD, default: 2023-12-31): ").strip() or "2023-12-31"
    
    try:
        short_ma = int(input("Enter short MA period (default: 50): ").strip() or "50")
        long_ma = int(input("Enter long MA period (default: 200): ").strip() or "200")
    except ValueError:
        short_ma, long_ma = 50, 200
        print("Using default MA periods: 50, 200")
    
    stats = bot.run_backtest(ticker, start_date, end_date, short_ma, long_ma)
    
    if stats is not None:
        save_option = input("\nSave results to file? (y/n): ").strip().lower()
        if save_option == 'y':
            bot.save_results()


if __name__ == "__main__":
    print("Running test with default parameters...")
    bot = BacktestingBot()
    stats = bot.run_backtest()
    if stats is not None:
        print("Test completed successfully!")
        bot.save_results("test_results.txt")
