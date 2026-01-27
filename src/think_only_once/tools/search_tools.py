"""Search tools for news and sentiment analysis."""

import re

from langchain_community.tools import DuckDuckGoSearchResults
from langchain_core.tools import tool

from think_only_once.models import NewsData


def _parse_search_results(raw_results: str) -> tuple[list[str], list[str]]:
    """Parse DuckDuckGo search results into headlines and snippets.

    Args:
        raw_results: Raw string output from DuckDuckGo search.

    Returns:
        Tuple of (headlines, snippets) lists.
    """
    headlines: list[str] = []
    snippets: list[str] = []

    # DuckDuckGo returns results in format: [snippet: ..., title: ..., link: ...], ...
    title_pattern = r"title:\s*([^,\]]+)"
    snippet_pattern = r"snippet:\s*([^,\]]+)"

    titles = re.findall(title_pattern, raw_results)
    snippet_matches = re.findall(snippet_pattern, raw_results)

    headlines = [t.strip() for t in titles if t.strip()]
    snippets = [s.strip() for s in snippet_matches if s.strip()]

    return headlines, snippets


@tool
def search_stock_news(ticker: str) -> NewsData:
    """Search for recent news about a stock.

    Args:
        ticker: Stock ticker symbol (e.g., NVDA, AAPL, MSFT).

    Returns:
        NewsData with headlines, snippets, and the search query used.
    """
    search = DuckDuckGoSearchResults(num_results=10)
    query = f"{ticker} stock news latest"
    raw_results = search.invoke(query)

    headlines, snippets = _parse_search_results(raw_results)

    return NewsData(
        headlines=headlines,
        snippets=snippets,
        search_query=query,
    )
