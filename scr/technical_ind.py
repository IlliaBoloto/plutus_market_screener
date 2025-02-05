import pandas as pd
import numpy as np


class TechnicalIndicators:
    def __init__(self, data: pd.DataFrame):
        """
        Initialize with stock price data.
        :param data: DataFrame with stock price data (must include 'Close' column)
        """
        if "Close" not in data.columns:
            raise ValueError("Data must contain a 'Close' price column.")
        self.data = data.copy()

    def simple_moving_average(self, window: int = 14):
        """Calculate Simple Moving Average (SMA)."""
        col_name = f"SMA_{window}"
        self.data[col_name] = self.data["Close"].rolling(window=window).mean()

        # Generate Signal
        signal_col = f"Signal_SMA_{window}"
        self.data[signal_col] = np.where(self.data["Close"] > self.data[col_name], "Buy", "Sell")
        return self.data

    def exponential_moving_average(self, window: int = 14):
        """Calculate Exponential Moving Average (EMA)."""
        col_name = f"EMA_{window}"
        self.data[col_name] = self.data["Close"].ewm(span=window, adjust=False).mean()

        # Generate Signal
        signal_col = f"Signal_EMA_{window}"
        self.data[signal_col] = np.where(self.data["Close"] > self.data[col_name], "Buy", "Sell")
        return self.data

    def relative_strength_index(self, window: int = 14):
        """Calculate Relative Strength Index (RSI)."""
        delta = self.data["Close"].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()

        rs = gain / loss
        self.data["RSI"] = 100 - (100 / (1 + rs))

        # Generate Signal
        self.data["Signal_RSI"] = np.where(
            self.data["RSI"] < 30, "Strong Buy",
            np.where(self.data["RSI"] < 40, "Buy",
                     np.where(self.data["RSI"] > 70, "Strong Sell",
                              np.where(self.data["RSI"] > 60, "Sell", "Hold"))))

        return self.data

    def macd(self, short_window: int = 12, long_window: int = 26, signal_window: int = 9):
        """Calculate Moving Average Convergence Divergence (MACD)."""
        macd_col = f"MACD_{short_window}_{long_window}"
        macd_signal_col = f"MACD_Signal_{signal_window}"

        short_ema = self.data["Close"].ewm(span=short_window, adjust=False).mean()
        long_ema = self.data["Close"].ewm(span=long_window, adjust=False).mean()
        self.data[macd_col] = short_ema - long_ema
        self.data[macd_signal_col] = self.data[macd_col].ewm(span=signal_window, adjust=False).mean()

        # Generate Signal
        signal_col = f"Signal_MACD_{short_window}_{long_window}"
        self.data[signal_col] = np.where(
            self.data[macd_col] > self.data[macd_signal_col], "Buy",
            "Sell"
        )

        return self.data

    def bollinger_bands(self, window: int = 20, num_std_dev: int = 2):
        """Calculate Bollinger Bands."""
        mid_band_col = f"Bollinger_Mid_{window}"
        upper_band_col = f"Bollinger_Upper_{window}_{num_std_dev}"
        lower_band_col = f"Bollinger_Lower_{window}_{num_std_dev}"

        rolling_mean = self.data["Close"].rolling(window=window).mean()
        rolling_std = self.data["Close"].rolling(window=window).std()

        self.data[mid_band_col] = rolling_mean
        self.data[upper_band_col] = rolling_mean + (rolling_std * num_std_dev)
        self.data[lower_band_col] = rolling_mean - (rolling_std * num_std_dev)

        # Generate Signal
        signal_col = f"Signal_Bollinger_{window}_{num_std_dev}"
        self.data[signal_col] = np.where(
            self.data["Close"] < self.data[lower_band_col], "Strong Buy",
            np.where(self.data["Close"] > self.data[upper_band_col], "Strong Sell", "Hold")
        )

        return self.data


# Quick test
if __name__ == "__main__":
    from scr.data_handler import DataHandler

    dh = DataHandler()
    df = dh.fetch_stock_data("AAPL", period="3mo")

    if isinstance(df, pd.DataFrame):
        ti = TechnicalIndicators(df)
        df = ti.simple_moving_average(14)
        df = ti.exponential_moving_average(14)
        df = ti.relative_strength_index()
        df = ti.macd()
        df = ti.bollinger_bands()

        signal_cols = [col for col in df.columns if col.startswith("Signal")]
        print(df.tail()[["Close"] + signal_cols])
    else:
        print("Error:", df)
