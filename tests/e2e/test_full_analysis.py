"""End-to-end tests with real API calls."""

import os

import pytest

from think_only_once.main import analyze_stock


@pytest.mark.e2e
@pytest.mark.slow
@pytest.mark.skipif(
    not os.getenv("OPENAI_API_KEY"),
    reason="OPENAI_API_KEY not set - skipping E2E tests",
)
class TestFullAnalysisE2E:
    """End-to-end tests requiring real API keys."""

    def test_analyze_stock_real_api(self) -> None:
        """Test real stock analysis with actual API calls."""
        result = analyze_stock("Analyze NVDA")
        assert result is not None
        assert "NVDA" in result
        assert len(result) > 100

    def test_news_only_query(self) -> None:
        """Test news-only query with real API."""
        result = analyze_stock("What's the news on AAPL?")
        assert result is not None
        assert "News" in result or "news" in result

    def test_invalid_ticker_handling(self) -> None:
        """Test handling of invalid ticker symbol."""
        result = analyze_stock("Analyze INVALIDTICKER123")
        assert result is not None
