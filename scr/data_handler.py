import yfinance as yf
import pandas as pd


class DataHandler:
    def __init__(self):
        """Initialize DataHandler"""
        pass

    def fetch_stock_data(self, ticker: str, period: str = "1y", interval: str = "1d"):
        """
        Fetch historical stock data using Yahoo Finance.

        :param ticker: Stock ticker symbol (e.g., 'AAPL')
        :param period: Time period (e.g., '1y', '6mo', '3mo')
        :param interval: Data interval (e.g., '1d', '1h', '5m')
        :return: DataFrame with stock data or an error message
        """
        try:
            stock = yf.Ticker(ticker)
            data = stock.history(period=period, interval=interval)

            # Check if data is empty (invalid ticker)
            if data.empty:
                raise ValueError(f"No data found for ticker '{ticker}'. Please check the symbol.")

            return data

        except Exception as e:
            return {"error": str(e)}


# Quick test
if __name__ == "__main__":
    dh = DataHandler()
    ticker = "AAPL"  # Try changing this to an invalid ticker (e.g., "INVALID123")
    result = dh.fetch_stock_data(ticker)
    print(result if isinstance(result, dict) else result.head())
