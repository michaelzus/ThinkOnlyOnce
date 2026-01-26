"""Search tools for news and sentiment analysis."""

from langchain_community.tools import DuckDuckGoSearchResults
from langchain_core.tools import tool


@tool
def search_stock_news(ticker: str) -> str:
    """Search for recent news about a stock.

    Args:
        ticker: Stock ticker symbol (e.g., NVDA, AAPL, MSFT).

    Returns:
        Recent news headlines and snippets about the stock.
    """
    search = DuckDuckGoSearchResults(num_results=5)
    query = f"{ticker} stock news latest"
    return search.invoke(query)
