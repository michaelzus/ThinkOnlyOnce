"""YFinance tools for technical and fundamental analysis."""

import yfinance as yf
from langchain_core.tools import tool


def _first_non_null(*values):
    """Return the first non-null value from the provided options.

    Args:
        *values: Candidate values in priority order.

    Returns:
        First non-null value or None.
    """
    for value in values:
        if value is not None:
            return value
    return None


@tool
def get_technical_data(ticker: str) -> dict:
    """Fetch technical analysis data for a stock.

    Args:
        ticker: Stock ticker symbol (e.g., NVDA, AAPL, MSFT).

    Returns:
        Dictionary with price, moving averages, volume data.
    """
    stock = yf.Ticker(ticker)
    info = stock.info
    fast_info = getattr(stock, "fast_info", {}) or {}

    return {
        "current_price": _first_non_null(
            fast_info.get("last_price"),
            fast_info.get("previous_close"),
            info.get("currentPrice", info.get("regularMarketPrice")),
        ),
        "fifty_two_week_high": _first_non_null(
            fast_info.get("year_high"),
            info.get("fiftyTwoWeekHigh"),
        ),
        "fifty_two_week_low": _first_non_null(
            fast_info.get("year_low"),
            info.get("fiftyTwoWeekLow"),
        ),
        "fifty_day_ma": _first_non_null(
            fast_info.get("fifty_day_average"),
            info.get("fiftyDayAverage"),
        ),
        "two_hundred_day_ma": _first_non_null(
            fast_info.get("two_hundred_day_average"),
            info.get("twoHundredDayAverage"),
        ),
        "volume": _first_non_null(
            fast_info.get("last_volume"),
            info.get("volume"),
        ),
        "avg_volume": _first_non_null(
            fast_info.get("three_month_average_volume"),
            info.get("averageVolume"),
        ),
        "price_change_pct": _first_non_null(
            fast_info.get("year_change"),
            info.get("regularMarketChangePercent"),
        ),
    }


@tool
def get_fundamental_data(ticker: str) -> dict:
    """Fetch fundamental analysis data for a stock.

    Args:
        ticker: Stock ticker symbol (e.g., NVDA, AAPL, MSFT).

    Returns:
        Dictionary with financial metrics like P/E, market cap, revenue.
    """
    stock = yf.Ticker(ticker)
    info = stock.info

    return {
        "market_cap": info.get("marketCap"),
        "pe_ratio": info.get("trailingPE"),
        "forward_pe": info.get("forwardPE"),
        "eps": info.get("trailingEps"),
        "revenue": info.get("totalRevenue"),
        "profit_margin": info.get("profitMargins"),
        "debt_to_equity": info.get("debtToEquity"),
        "dividend_yield": info.get("dividendYield"),
        "sector": info.get("sector"),
        "industry": info.get("industry"),
    }
