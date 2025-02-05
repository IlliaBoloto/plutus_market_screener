import numpy as np
import pandas as pd
from scr.data_handler import DataHandler


class MonteCarloSimulation:
    def __init__(self, ticker: str, period: str = "1y", interval: str = "1d"):
        """
        Initialize Monte Carlo Simulation with historical data.

        :param ticker: Stock ticker symbol (e.g., 'AAPL')
        :param period: Time period for historical data (e.g., '1y', '6mo', '3mo')
        :param interval: Data interval (e.g., '1d', '1h', '5m')
        """
        self.ticker = ticker
        self.period = period
        self.interval = interval
        self.data_handler = DataHandler()
        self.data = self._fetch_data()

    def _fetch_data(self):
        """Fetch historical stock data."""
        data = self.data_handler.fetch_stock_data(self.ticker, self.period, self.interval)
        if isinstance(data, dict) and "error" in data:
            raise ValueError(data["error"])
        return data

    def run_simulation(self, num_simulations: int = 1000, num_days: int = 30, mu: float = None, sigma: float = None):
        """
        Run Monte Carlo simulation for stock price movement.

        :param num_simulations: Number of simulated price paths
        :param num_days: Number of future days to simulate
        :param mu: Expected daily return (default: historical mean return)
        :param sigma: Volatility (default: historical standard deviation)
        :return: DataFrame with simulated price paths
        """
        if self.data is None or "Close" not in self.data.columns:
            raise ValueError("Historical data not available or missing 'close' column.")

        # Compute log returns
        log_returns = np.log(1 + self.data["Close"].pct_change().dropna())

        # Use historical mean and standard deviation if not provided
        mu = mu if mu is not None else log_returns.mean()
        sigma = sigma if sigma is not None else log_returns.std()

        # Get last closing price as starting point
        last_price = self.data["Close"].iloc[-1]

        # Monte Carlo Simulation
        price_paths = np.zeros((num_days, num_simulations))
        price_paths[0] = last_price

        for t in range(1, num_days):
            random_shocks = np.random.normal(mu, sigma, num_simulations)
            price_paths[t] = price_paths[t - 1] * np.exp(random_shocks)

        # Convert to DataFrame for analysis
        sim_df = pd.DataFrame(price_paths, index=range(1, num_days + 1))

        return sim_df


# Quick test
if __name__ == "__main__":
    ticker = "AAPL"
    simulator = MonteCarloSimulation(ticker, period="1y", interval="1d")
    simulated_prices = simulator.run_simulation(num_simulations=500, num_days=30)

    print(simulated_prices.head())  # Display the first few rows of the simulation
