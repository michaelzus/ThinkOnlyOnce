"""Macro market tools for market-wide risk assessment.

Provides market indices data (SPY, VIX, sector ETFs), Fear & Greed Index,
and geopolitical news search.
"""

import requests
import yfinance as yf
from ddgs import DDGS
from langchain_core.tools import tool

from think_only_once.models import FearGreedData, GeopoliticalNewsData, MarketIndicesData


# Fear & Greed Index


def _get_fear_greed_label(value: int | None) -> str | None:
    """Convert Fear & Greed value to label.

    Args:
        value: Fear & Greed index value (0-100).

    Returns:
        Label string or None.
    """
    if value is None:
        return None

    if value <= 24:
        return "Extreme Fear"
    elif value <= 44:
        return "Fear"
    elif value <= 55:
        return "Neutral"
    elif value <= 75:
        return "Greed"
    else:
        return "Extreme Greed"


def get_fear_greed_index() -> FearGreedData:
    """Fetch CNN Fear & Greed Index.

    Uses CNN's public API endpoint for the Fear & Greed Index data.
    Gracefully degrades if the fetch fails.

    Returns:
        FearGreedData with value (0-100) and label.
    """
    try:
        url = "https://production.dataviz.cnn.io/index/fearandgreed/graphdata"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
        }

        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        data = response.json()

        # Extract fear and greed score
        fear_greed = data.get("fear_and_greed", {})
        score = fear_greed.get("score")
        rating = fear_greed.get("rating")

        if score is not None:
            value = int(round(float(score)))
            # Use the API's rating if available, otherwise calculate
            label = rating if rating else _get_fear_greed_label(value)
            return FearGreedData(value=value, label=label)

    except requests.RequestException:
        # Network error - graceful degradation
        pass
    except (KeyError, ValueError, TypeError):
        # Parsing error - graceful degradation
        pass

    # Return empty data on failure (graceful degradation)
    return FearGreedData(value=None, label=None)


# Sector to ETF mapping
SECTOR_ETF_MAP = {
    "Technology": "XLK",
    "Healthcare": "XLV",
    "Financial Services": "XLF",
    "Financials": "XLF",
    "Consumer Cyclical": "XLY",
    "Consumer Defensive": "XLP",
    "Energy": "XLE",
    "Industrials": "XLI",
    "Basic Materials": "XLB",
    "Materials": "XLB",
    "Real Estate": "XLRE",
    "Utilities": "XLU",
    "Communication Services": "XLC",
}


def _get_ticker_data(symbol: str) -> dict:
    """Fetch basic price data for a ticker.

    Args:
        symbol: Ticker symbol.

    Returns:
        Dict with price, 50d_ma, 200d_ma, change_pct.
    """
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        fast_info = getattr(ticker, "fast_info", {}) or {}

        price = fast_info.get("last_price") or fast_info.get("previous_close") or info.get("regularMarketPrice")
        ma_50 = fast_info.get("fifty_day_average") or info.get("fiftyDayAverage")
        ma_200 = fast_info.get("two_hundred_day_average") or info.get("twoHundredDayAverage")
        change_pct = info.get("regularMarketChangePercent")

        return {
            "price": price,
            "ma_50": ma_50,
            "ma_200": ma_200,
            "change_pct": change_pct,
        }
    except Exception:
        return {}


@tool
def get_market_indices(sector: str | None = None) -> MarketIndicesData:
    """Fetch market indices data for macro risk assessment.

    Gets SPY, VIX, sector ETF data, and Fear & Greed Index.

    Args:
        sector: Company sector to look up corresponding ETF (e.g., "Technology" -> XLK).

    Returns:
        MarketIndicesData with SPY, VIX, sector ETF, and sentiment data.
    """
    # Get SPY data
    spy_data = _get_ticker_data("SPY")

    # Get VIX data
    vix_data = _get_ticker_data("^VIX")

    # Get sector ETF data if sector is provided
    sector_etf = SECTOR_ETF_MAP.get(sector) if sector else None
    sector_data = _get_ticker_data(sector_etf) if sector_etf else {}

    # Get Fear & Greed Index
    fear_greed = get_fear_greed_index()

    return MarketIndicesData(
        spy_price=spy_data.get("price"),
        spy_50d_ma=spy_data.get("ma_50"),
        spy_200d_ma=spy_data.get("ma_200"),
        spy_change_pct=spy_data.get("change_pct"),
        vix_level=vix_data.get("price"),
        vix_change_pct=vix_data.get("change_pct"),
        sector_etf=sector_etf,
        sector_price=sector_data.get("price"),
        sector_50d_ma=sector_data.get("ma_50"),
        sector_change_pct=sector_data.get("change_pct"),
        fear_greed_value=fear_greed.value,
        fear_greed_label=fear_greed.label,
    )


@tool
def search_geopolitical_news() -> GeopoliticalNewsData:
    """Search for geopolitical news that may impact markets.

    Searches for major geopolitical events, conflicts, sanctions,
    and global economic concerns.

    Returns:
        GeopoliticalNewsData with headlines and snippets.
    """
    query = "geopolitical risk market impact news today"

    try:
        with DDGS() as ddgs:
            results = list(ddgs.news(query, max_results=5))

        headlines = [r.get("title", "") for r in results if r.get("title")]
        snippets = [r.get("body", "")[:200] for r in results if r.get("body")]

        return GeopoliticalNewsData(
            headlines=headlines,
            snippets=snippets,
            search_query=query,
        )
    except Exception:
        # Graceful degradation
        return GeopoliticalNewsData(search_query=query)
