"""Tests for macro market tools."""

from unittest.mock import MagicMock, patch

import pytest

from think_only_once.models import FearGreedData, GeopoliticalNewsData, MarketIndicesData
from think_only_once.tools.macro_tools import (
    SECTOR_ETF_MAP,
    _get_fear_greed_label,
    _get_ticker_data,
    get_fear_greed_index,
    get_market_indices,
    search_geopolitical_news,
)


class TestGetFearGreedLabel:
    """Tests for _get_fear_greed_label helper function."""

    def test_extreme_fear_label(self) -> None:
        """Test that values 0-24 return Extreme Fear."""
        assert _get_fear_greed_label(0) == "Extreme Fear"
        assert _get_fear_greed_label(15) == "Extreme Fear"
        assert _get_fear_greed_label(24) == "Extreme Fear"

    def test_fear_label(self) -> None:
        """Test that values 25-44 return Fear."""
        assert _get_fear_greed_label(25) == "Fear"
        assert _get_fear_greed_label(35) == "Fear"
        assert _get_fear_greed_label(44) == "Fear"

    def test_neutral_label(self) -> None:
        """Test that values 45-55 return Neutral."""
        assert _get_fear_greed_label(45) == "Neutral"
        assert _get_fear_greed_label(50) == "Neutral"
        assert _get_fear_greed_label(55) == "Neutral"

    def test_greed_label(self) -> None:
        """Test that values 56-75 return Greed."""
        assert _get_fear_greed_label(56) == "Greed"
        assert _get_fear_greed_label(65) == "Greed"
        assert _get_fear_greed_label(75) == "Greed"

    def test_extreme_greed_label(self) -> None:
        """Test that values 76-100 return Extreme Greed."""
        assert _get_fear_greed_label(76) == "Extreme Greed"
        assert _get_fear_greed_label(90) == "Extreme Greed"
        assert _get_fear_greed_label(100) == "Extreme Greed"

    def test_none_value_returns_none(self) -> None:
        """Test that None input returns None."""
        assert _get_fear_greed_label(None) is None


class TestGetFearGreedIndex:
    """Tests for get_fear_greed_index function."""

    def test_returns_fear_greed_data_model(self) -> None:
        """Test that function returns FearGreedData model."""
        with patch("think_only_once.tools.macro_tools.requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "fear_and_greed": {"score": 45.5, "rating": "Neutral"}
            }
            mock_get.return_value = mock_response

            result = get_fear_greed_index()

            assert isinstance(result, FearGreedData)
            assert result.value == 46  # Rounded
            assert result.label == "Neutral"

    def test_graceful_degradation_on_network_error(self) -> None:
        """Test that function returns empty data on network error."""
        with patch("think_only_once.tools.macro_tools.requests.get") as mock_get:
            import requests

            mock_get.side_effect = requests.RequestException("Network error")

            result = get_fear_greed_index()

            assert isinstance(result, FearGreedData)
            assert result.value is None
            assert result.label is None

    def test_graceful_degradation_on_parse_error(self) -> None:
        """Test that function returns empty data on parse error."""
        with patch("think_only_once.tools.macro_tools.requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = {"invalid": "data"}
            mock_get.return_value = mock_response

            result = get_fear_greed_index()

            assert isinstance(result, FearGreedData)
            assert result.value is None
            assert result.label is None


class TestGetTickerData:
    """Tests for _get_ticker_data helper function."""

    def test_returns_price_data_dict(self) -> None:
        """Test that function returns dict with price data."""
        with patch("think_only_once.tools.macro_tools.yf.Ticker") as mock_ticker_class:
            mock_ticker = MagicMock()
            mock_ticker.fast_info = {
                "last_price": 450.50,
                "fifty_day_average": 445.00,
                "two_hundred_day_average": 430.00,
            }
            mock_ticker.info = {"regularMarketChangePercent": 0.56}
            mock_ticker_class.return_value = mock_ticker

            result = _get_ticker_data("SPY")

            assert result["price"] == 450.50
            assert result["ma_50"] == 445.00
            assert result["ma_200"] == 430.00
            assert result["change_pct"] == 0.56

    def test_returns_empty_dict_on_exception(self) -> None:
        """Test that function returns empty dict on exception."""
        with patch("think_only_once.tools.macro_tools.yf.Ticker") as mock_ticker_class:
            mock_ticker_class.side_effect = Exception("API Error")

            result = _get_ticker_data("INVALID")

            assert result == {}


class TestSectorEtfMap:
    """Tests for SECTOR_ETF_MAP constant."""

    def test_contains_major_sectors(self) -> None:
        """Test that map contains all major sector ETFs."""
        assert "Technology" in SECTOR_ETF_MAP
        assert "Healthcare" in SECTOR_ETF_MAP
        assert "Energy" in SECTOR_ETF_MAP
        assert "Financials" in SECTOR_ETF_MAP

    def test_technology_maps_to_xlk(self) -> None:
        """Test that Technology maps to XLK."""
        assert SECTOR_ETF_MAP["Technology"] == "XLK"

    def test_energy_maps_to_xle(self) -> None:
        """Test that Energy maps to XLE."""
        assert SECTOR_ETF_MAP["Energy"] == "XLE"


class TestGetMarketIndices:
    """Tests for get_market_indices tool."""

    def test_returns_market_indices_data_model(self) -> None:
        """Test that function returns MarketIndicesData model."""
        with patch("think_only_once.tools.macro_tools._get_ticker_data") as mock_ticker, patch(
            "think_only_once.tools.macro_tools.get_fear_greed_index"
        ) as mock_fg:
            mock_ticker.return_value = {
                "price": 450.50,
                "ma_50": 445.00,
                "ma_200": 430.00,
                "change_pct": 0.56,
            }
            mock_fg.return_value = FearGreedData(value=50, label="Neutral")

            result = get_market_indices.invoke({})

            assert isinstance(result, MarketIndicesData)
            assert result.spy_price == 450.50
            assert result.fear_greed_value == 50

    def test_includes_sector_etf_when_provided(self) -> None:
        """Test that sector ETF data is included when sector is provided."""
        with patch("think_only_once.tools.macro_tools._get_ticker_data") as mock_ticker, patch(
            "think_only_once.tools.macro_tools.get_fear_greed_index"
        ) as mock_fg:
            mock_ticker.return_value = {
                "price": 200.00,
                "ma_50": 195.00,
                "ma_200": 185.00,
                "change_pct": 1.2,
            }
            mock_fg.return_value = FearGreedData(value=60, label="Greed")

            result = get_market_indices.invoke({"sector": "Technology"})

            assert result.sector_etf == "XLK"

    def test_no_sector_etf_when_not_provided(self) -> None:
        """Test that sector ETF is None when sector is not provided."""
        with patch("think_only_once.tools.macro_tools._get_ticker_data") as mock_ticker, patch(
            "think_only_once.tools.macro_tools.get_fear_greed_index"
        ) as mock_fg:
            mock_ticker.return_value = {"price": 450.50}
            mock_fg.return_value = FearGreedData(value=50, label="Neutral")

            result = get_market_indices.invoke({})

            assert result.sector_etf is None

    def test_is_langchain_tool(self) -> None:
        """Test that get_market_indices is a LangChain tool."""
        assert hasattr(get_market_indices, "invoke")
        assert hasattr(get_market_indices, "name")
        assert get_market_indices.name == "get_market_indices"


class TestSearchGeopoliticalNews:
    """Tests for search_geopolitical_news tool."""

    def test_returns_geopolitical_news_data_model(self) -> None:
        """Test that function returns GeopoliticalNewsData model."""
        with patch("think_only_once.tools.macro_tools.DDGS") as mock_ddgs_class:
            mock_ddgs = MagicMock()
            mock_ddgs.__enter__ = MagicMock(return_value=mock_ddgs)
            mock_ddgs.__exit__ = MagicMock(return_value=False)
            mock_ddgs.news.return_value = [
                {"title": "Global tensions", "body": "Geopolitical risks increase..."},
                {"title": "Trade concerns", "body": "Tariff discussions ongoing..."},
            ]
            mock_ddgs_class.return_value = mock_ddgs

            result = search_geopolitical_news.invoke({})

            assert isinstance(result, GeopoliticalNewsData)
            assert len(result.headlines) == 2
            assert "Global tensions" in result.headlines

    def test_graceful_degradation_on_exception(self) -> None:
        """Test that function returns empty data on exception."""
        with patch("think_only_once.tools.macro_tools.DDGS") as mock_ddgs_class:
            mock_ddgs_class.side_effect = Exception("Search error")

            result = search_geopolitical_news.invoke({})

            assert isinstance(result, GeopoliticalNewsData)
            assert result.headlines == []
            assert result.snippets == []

    def test_is_langchain_tool(self) -> None:
        """Test that search_geopolitical_news is a LangChain tool."""
        assert hasattr(search_geopolitical_news, "invoke")
        assert hasattr(search_geopolitical_news, "name")
        assert search_geopolitical_news.name == "search_geopolitical_news"

    def test_includes_search_query(self) -> None:
        """Test that result includes the search query used."""
        with patch("think_only_once.tools.macro_tools.DDGS") as mock_ddgs_class:
            mock_ddgs = MagicMock()
            mock_ddgs.__enter__ = MagicMock(return_value=mock_ddgs)
            mock_ddgs.__exit__ = MagicMock(return_value=False)
            mock_ddgs.news.return_value = []
            mock_ddgs_class.return_value = mock_ddgs

            result = search_geopolitical_news.invoke({})

            assert "geopolitical" in result.search_query.lower()
