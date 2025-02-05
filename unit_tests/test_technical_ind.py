import unittest
import numpy as np
import pandas as pd

from scr.technical_ind import TechnicalIndicators


class TechnicalIndicatorsTestCase(unittest.TestCase):
    def setUp(self):
        # Create dummy data with 50 days of "Close" prices ranging from 100 to 150.
        self.dates = pd.date_range("2020-01-01", periods=50, freq="D")
        self.df = pd.DataFrame({
            "Close": np.linspace(100, 150, 50)
        }, index=self.dates)
        # Create an instance of TechnicalIndicators.
        self.ti = TechnicalIndicators(self.df)

    def test_simple_moving_average(self):
        window = 14
        df_res = self.ti.simple_moving_average(window)
        sma_col = f"SMA_{window}"
        signal_col = f"Signal_SMA_{window}"
        # Check that the SMA and signal columns are added.
        self.assertIn(sma_col, df_res.columns)
        self.assertIn(signal_col, df_res.columns)
        # Find a row with a non-NaN SMA value.
        valid_idx = df_res[sma_col].dropna().index[0]
        close_val = df_res.at[valid_idx, "Close"]
        sma_val = df_res.at[valid_idx, sma_col]
        # For our increasing dummy data, expect Close > SMA.
        expected_signal = "Buy" if close_val > sma_val else "Sell"
        self.assertEqual(df_res.at[valid_idx, signal_col], expected_signal)

    def test_exponential_moving_average(self):
        window = 14
        df_res = self.ti.exponential_moving_average(window)
        ema_col = f"EMA_{window}"
        signal_col = f"Signal_EMA_{window}"
        self.assertIn(ema_col, df_res.columns)
        self.assertIn(signal_col, df_res.columns)

    def test_relative_strength_index(self):
        df_res = self.ti.relative_strength_index()
        self.assertIn("RSI", df_res.columns)
        self.assertIn("Signal_RSI", df_res.columns)
        # Check that RSI values (where calculated) are between 0 and 100.
        valid_rsi = df_res["RSI"].dropna()
        self.assertTrue((valid_rsi >= 0).all() and (valid_rsi <= 100).all())

    def test_macd(self):
        short_window = 12
        long_window = 26
        signal_window = 9
        df_res = self.ti.macd(short_window, long_window, signal_window)
        macd_col = f"MACD_{short_window}_{long_window}"
        macd_signal_col = f"MACD_Signal_{signal_window}"
        signal_col = f"Signal_MACD_{short_window}_{long_window}"
        self.assertIn(macd_col, df_res.columns)
        self.assertIn(macd_signal_col, df_res.columns)
        self.assertIn(signal_col, df_res.columns)

    def test_bollinger_bands(self):
        window = 20
        num_std_dev = 2
        df_res = self.ti.bollinger_bands(window, num_std_dev)
        mid_band = f"Bollinger_Mid_{window}"
        upper_band = f"Bollinger_Upper_{window}_{num_std_dev}"
        lower_band = f"Bollinger_Lower_{window}_{num_std_dev}"
        signal_col = f"Signal_Bollinger_{window}_{num_std_dev}"
        self.assertIn(mid_band, df_res.columns)
        self.assertIn(upper_band, df_res.columns)
        self.assertIn(lower_band, df_res.columns)
        self.assertIn(signal_col, df_res.columns)

    def test_missing_close_column(self):
        # Create a DataFrame without a 'Close' column.
        df_bad = pd.DataFrame({"Open": np.arange(10)})
        with self.assertRaises(ValueError):
            TechnicalIndicators(df_bad)


if __name__ == "__main__":
    unittest.main()
