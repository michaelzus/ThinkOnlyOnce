"""Search tools for news and sentiment analysis."""

from ddgs import DDGS
from langchain_core.tools import tool

from think_only_once.models import NewsData


@tool
def search_stock_news(ticker: str) -> NewsData:
    """Search for recent news about a stock.

    Args:
        ticker: Stock ticker symbol (e.g., NVDA, AAPL, MSFT).

    Returns:
        NewsData with headlines, snippets, and the search query used.
    """
    query = f"{ticker} stock news"

    try:
        with DDGS() as ddgs:
            results = list(ddgs.news(query, max_results=8))

        headlines: list[str] = []
        snippets: list[str] = []
        for r in results:
            title = (r.get("title") or "").strip()
            body = (r.get("body") or "").strip()
            source = (r.get("source") or "").strip()
            date = (r.get("date") or "").strip()

            if title:
                meta_parts = [p for p in (source, date) if p]
                meta = f" ({', '.join(meta_parts)})" if meta_parts else ""
                headlines.append(f"{title}{meta}")

            if body:
                cleaned = " ".join(body.split())
                snippets.append(cleaned[:280])

        return NewsData(headlines=headlines, snippets=snippets, search_query=query)
    except Exception:
        # Graceful degradation
        return NewsData(headlines=[], snippets=[], search_query=query)
