"""Shared test fixtures and configuration."""

from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def mock_env_api_key(monkeypatch):
    """Set up mock API key in environment."""
    monkeypatch.setenv("OPENAI_API_KEY", "test-api-key-12345")


@pytest.fixture
def clean_env(monkeypatch):
    """Remove API key from environment for negative tests."""
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)


@pytest.fixture
def mock_llm():
    """Create a mock LLM that returns predictable responses."""
    mock = MagicMock()
    mock.invoke.return_value.content = "Mock LLM response"
    return mock


@pytest.fixture
def mock_chat_openai(mock_llm):
    """Patch ChatOpenAI to return mock LLM."""
    with patch("think_only_once.agents.base.ChatOpenAI", return_value=mock_llm):
        yield mock_llm


@pytest.fixture
def mock_yfinance_ticker():
    """Create mock yfinance Ticker with sample data."""
    mock_ticker = MagicMock()
    mock_ticker.fast_info = {
        "last_price": 875.50,
        "previous_close": 870.00,
        "year_high": 950.00,
        "year_low": 450.00,
        "fifty_day_average": 820.00,
        "two_hundred_day_average": 750.00,
        "last_volume": 45000000,
        "three_month_average_volume": 40000000,
        "year_change": 0.025,
    }
    mock_ticker.info = {
        "currentPrice": 875.50,
        "regularMarketPrice": 875.50,
        "fiftyTwoWeekHigh": 950.00,
        "fiftyTwoWeekLow": 450.00,
        "fiftyDayAverage": 820.00,
        "twoHundredDayAverage": 750.00,
        "volume": 45000000,
        "averageVolume": 40000000,
        "regularMarketChangePercent": 2.5,
        "marketCap": 2100000000000,
        "trailingPE": 65.4,
        "forwardPE": 45.2,
        "trailingEps": 13.38,
        "totalRevenue": 60000000000,
        "profitMargins": 0.55,
        "debtToEquity": 41.5,
        "dividendYield": 0.0004,
        "sector": "Technology",
        "industry": "Semiconductors",
    }
    return mock_ticker


@pytest.fixture
def patch_yfinance(mock_yfinance_ticker):
    """Patch yfinance.Ticker to return mock."""
    with patch("think_only_once.tools.yfinance_tools.yf.Ticker", return_value=mock_yfinance_ticker):
        yield mock_yfinance_ticker


@pytest.fixture
def mock_ddg_news_results():
    """Create mock DuckDuckGo NEWS results (ddgs.news)."""
    return [
        {
            "title": "NVDA hits record high",
            "body": "NVIDIA stock reaches new ATH as AI demand accelerates across data centers.",
            "source": "ExampleWire",
            "date": "2026-02-02",
            "url": "https://example.com/nvda-record-high",
        },
        {
            "title": "AI demand surge lifts semiconductor outlook",
            "body": "Analysts cite sustained capex and strong GPU demand supporting near-term revenue visibility.",
            "source": "MarketDaily",
            "date": "2026-02-01",
            "url": "https://example.com/ai-demand-surge",
        },
    ]


@pytest.fixture
def patch_ddg_search(mock_ddg_news_results):
    """Patch DDGS context manager for search_stock_news."""
    mock_ddgs = MagicMock()
    mock_ddgs.news.return_value = mock_ddg_news_results

    mock_ctx = MagicMock()
    mock_ctx.__enter__.return_value = mock_ddgs
    mock_ctx.__exit__.return_value = None

    with patch("think_only_once.tools.search_tools.DDGS", return_value=mock_ctx):
        yield mock_ddgs


@pytest.fixture
def sample_analysis_state():
    """Create sample AnalysisState for testing."""
    return {
        "ticker": "NVDA",
        "query": "Analyze NVDA stock",
        "run_technical": True,
        "run_fundamental": True,
        "run_news": True,
        "run_macro": True,
        "technical_analysis": None,
        "fundamental_analysis": None,
        "news_analysis": None,
        "macro_analysis": None,
        "ai_outlook": None,
        "messages": [],
    }


@pytest.fixture
def completed_analysis_state():
    """Create completed AnalysisState with all analyses."""
    return {
        "ticker": "NVDA",
        "query": "Analyze NVDA stock",
        "run_technical": True,
        "run_fundamental": True,
        "run_news": True,
        "run_macro": True,
        "technical_analysis": "Bullish trend",
        "fundamental_analysis": "Overvalued but strong growth",
        "news_analysis": "Positive sentiment",
        "macro_analysis": "Market conditions favorable",
        "ai_outlook": "BUY recommendation with $950 target",
        "messages": [],
    }


@pytest.fixture
def mock_router_decision():
    """Create mock RouterDecision for full analysis."""
    from think_only_once.agents.router import RouterDecision

    return RouterDecision(
        ticker="NVDA",
        run_technical=True,
        run_fundamental=True,
        run_news=True,
        run_macro=True,
        reasoning="User requested full analysis",
    )


@pytest.fixture
def mock_yfinance_market_ticker():
    """Create mock yfinance Ticker for market indices (SPY, VIX)."""
    mock_ticker = MagicMock()
    mock_ticker.fast_info = {
        "last_price": 450.50,
        "previous_close": 448.00,
        "fifty_day_average": 445.00,
        "two_hundred_day_average": 430.00,
    }
    mock_ticker.info = {
        "regularMarketPrice": 450.50,
        "fiftyDayAverage": 445.00,
        "twoHundredDayAverage": 430.00,
        "regularMarketChangePercent": 0.56,
    }
    return mock_ticker


@pytest.fixture
def mock_ddg_news():
    """Create mock DuckDuckGo news results for geopolitical news."""
    return [
        {"title": "Global tensions rise", "body": "Geopolitical risks increase market volatility..."},
        {"title": "Trade concerns", "body": "Tariff discussions impact stocks..."},
    ]
