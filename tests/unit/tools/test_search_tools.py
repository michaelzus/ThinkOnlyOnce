"""Tests for search tools."""

from unittest.mock import MagicMock
from unittest.mock import patch

from think_only_once.models import NewsData
from think_only_once.tools.search_tools import search_stock_news


class TestSearchStockNews:
    """Tests for search_stock_news tool."""

    def test_search_stock_news_returns_string(self, patch_ddg_search) -> None:
        """Test that search_stock_news returns NewsData model."""
        result = search_stock_news.invoke({"ticker": "NVDA"})
        assert isinstance(result, NewsData)
        assert result.search_query == "NVDA stock news"
        assert len(result.headlines) > 0

    def test_search_stock_news_calls_ddg_with_correct_query(self, mock_ddg_news_results) -> None:
        """Test that DDG news search is called with correct query format."""
        mock_ddgs = MagicMock()
        mock_ddgs.news.return_value = mock_ddg_news_results

        mock_ctx = MagicMock()
        mock_ctx.__enter__.return_value = mock_ddgs
        mock_ctx.__exit__.return_value = None

        with patch("think_only_once.tools.search_tools.DDGS", return_value=mock_ctx):
            search_stock_news.invoke({"ticker": "AAPL"})
            mock_ddgs.news.assert_called_once()
            call_args = mock_ddgs.news.call_args[0][0]
            assert "AAPL" in call_args
            assert "stock" in call_args
            assert "news" in call_args

    def test_search_stock_news_is_langchain_tool(self) -> None:
        """Test that search_stock_news is a LangChain tool."""
        assert hasattr(search_stock_news, "invoke")
        assert hasattr(search_stock_news, "name")
