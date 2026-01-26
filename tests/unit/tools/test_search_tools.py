"""Tests for search tools."""

from unittest.mock import patch

from think_only_once.tools.search_tools import search_stock_news


class TestSearchStockNews:
    """Tests for search_stock_news tool."""

    def test_search_stock_news_returns_string(self, patch_ddg_search) -> None:
        """Test that search_stock_news returns a string."""
        result = search_stock_news.invoke({"ticker": "NVDA"})
        assert isinstance(result, str)

    def test_search_stock_news_calls_ddg_with_correct_query(self, mock_ddg_search) -> None:
        """Test that DDG search is called with correct query format."""
        with patch("think_only_once.tools.search_tools.DuckDuckGoSearchResults", return_value=mock_ddg_search):
            search_stock_news.invoke({"ticker": "AAPL"})
            mock_ddg_search.invoke.assert_called_once()
            call_args = mock_ddg_search.invoke.call_args[0][0]
            assert "AAPL" in call_args
            assert "stock" in call_args
            assert "news" in call_args

    def test_search_stock_news_is_langchain_tool(self) -> None:
        """Test that search_stock_news is a LangChain tool."""
        assert hasattr(search_stock_news, "invoke")
        assert hasattr(search_stock_news, "name")
