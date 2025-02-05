import unittest
import numpy as np
import pandas as pd

from scr.simulations import MonteCarloSimulation
from scr.data_handler import DataHandler


# Dummy function to simulate fetching historical stock data.
def dummy_fetch_stock_data(self, ticker, period, interval):
    # Create 100 days of dummy data with a 'Close' column.
    dates = pd.date_range(start="2020-01-01", periods=100, freq="D")
    # Simulate an increasing trend: prices from 100 to 150.
    close_prices = np.linspace(100, 150, 100)
    return pd.DataFrame({"Close": close_prices}, index=dates)


class MonteCarloSimulationTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Monkey-patch DataHandler.fetch_stock_data so that it returns dummy data.
        DataHandler.fetch_stock_data = dummy_fetch_stock_data

    def test_run_simulation_returns_correct_shape(self):
        ticker = "DUMMY"
        simulator = MonteCarloSimulation(ticker, period="1y", interval="1d")
        # Run simulation with 500 simulations and 30 future days.
        sim_df = simulator.run_simulation(num_simulations=500, num_days=30)
        # Expect a DataFrame with 30 rows (days) and 500 columns (simulated paths)
        self.assertEqual(sim_df.shape, (30, 500), "Simulated DataFrame shape is incorrect.")

    def test_simulation_starts_with_last_close(self):
        ticker = "DUMMY"
        simulator = MonteCarloSimulation(ticker, period="1y", interval="1d")
        sim_df = simulator.run_simulation(num_simulations=500, num_days=30)

        # The dummy data has 100 rows; the last 'Close' value:
        dummy_data = simulator.data
        last_price = dummy_data["Close"].iloc[-1]

        # The simulation should start with the last closing price for all paths.
        np.testing.assert_allclose(
            sim_df.iloc[0].values,
            np.full(500, last_price),
            rtol=1e-5,
            err_msg="The first day of simulation does not match the last historical price."
        )

    def test_simulation_values_are_positive(self):
        ticker = "DUMMY"
        simulator = MonteCarloSimulation(ticker, period="1y", interval="1d")
        sim_df = simulator.run_simulation(num_simulations=500, num_days=30)
        self.assertTrue(np.all(sim_df.values > 0), "Some simulated prices are not positive.")


if __name__ == '__main__':
    unittest.main()
