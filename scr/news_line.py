import pandas as pd
import json
from newsdataapi import NewsDataApiClient
from newsapi import NewsApiClient
import os

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "config.json")


def load_api_keys(config_path=CONFIG_PATH):
    """Load API keys from a JSON config file."""
    try:
        with open(config_path, "r") as file:
            config = json.load(file)
            return config.get("newsdata_api_key"), config.get("newsapi_api_key")
    except FileNotFoundError:
        raise FileNotFoundError(f"Config file '{config_path}' not found.")
    except json.JSONDecodeError:
        raise ValueError(f"Error decoding '{config_path}'. Ensure it's valid JSON.")


# Get API keys securely
NEWSDATA_API_KEY, NEWSAPI_API_KEY = load_api_keys()


def get_news_from_newsdata(name: str, language: str = 'en') -> pd.DataFrame:
    """
    Fetch news from NewsData.io API.
    :param name: str Ticker name or keyword
    :param language: str Language filter (default: 'en')
    :return: pd.DataFrame with news results
    """
    if not NEWSDATA_API_KEY:
        raise ValueError("Missing NewsData.io API key. Check 'config.json'.")

    api = NewsDataApiClient(apikey=NEWSDATA_API_KEY)

    # Use latest_api() instead of deprecated news_api()
    response = api.latest_api(q=name, language=language)

    if "results" not in response or not response["results"]:
        raise ValueError(f"No news found for '{name}' on NewsData.io.")

    df = pd.DataFrame(response["results"])[["title", "link", "pubDate"]].rename(
        columns={"title": "Title", "link": "URL", "pubDate": "Time"}
    )

    df["Time"] = pd.to_datetime(df["Time"])
    df.set_index("Time", inplace=True)
    df.sort_index(ascending=False, inplace=True)
    return df.head(10)


def get_news_from_newsapi(name: str) -> pd.DataFrame:
    """
    Fetch news from NewsAPI.org.
    :param name: str Ticker name or keyword
    :return: pd.DataFrame with news results
    """
    if not NEWSAPI_API_KEY:
        raise ValueError("Missing NewsAPI API key. Check 'config.json'.")

    api = NewsApiClient(api_key=NEWSAPI_API_KEY)
    response = api.get_everything(q=name)

    if "articles" not in response or not response["articles"]:
        raise ValueError(f"No news found for '{name}' on NewsAPI.org.")

    df = pd.DataFrame(response["articles"])[["title", "url", "publishedAt"]].rename(
        columns={"title": "Title", "url": "URL", "publishedAt": "Time"}
    )

    df["Time"] = pd.to_datetime(df["Time"]).dt.tz_convert(None)
    df.set_index("Time", inplace=True)
    df.sort_index(ascending=False, inplace=True)
    return df.head(10)


# Quick test
if __name__ == "__main__":
    ticker = "AAPL"

    try:
        print("\nNews from NewsData.io:")
        print(get_news_from_newsdata(ticker))

        print("\nNews from NewsAPI.org:")
        print(get_news_from_newsapi(ticker))

    except ValueError as e:
        print("Error:", e)
