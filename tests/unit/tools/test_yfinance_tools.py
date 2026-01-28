"""Tests for yfinance tools."""

from unittest.mock import MagicMock, patch

import pandas as pd

from think_only_once.models import FundamentalData, PriceHistory, TechnicalData
from think_only_once.tools.yfinance_tools import get_fundamental_data, get_price_history, get_technical_data


class TestGetTechnicalData:
    """Tests for get_technical_data tool."""

    def test_get_technical_data_returns_dict(self, patch_yfinance) -> None:
        """Test that get_technical_data returns TechnicalData model."""
        result = get_technical_data.invoke({"ticker": "NVDA"})
        assert isinstance(result, TechnicalData)

    def test_get_technical_data_has_required_keys(self, patch_yfinance) -> None:
        """Test that result contains all required technical data fields."""
        result = get_technical_data.invoke({"ticker": "NVDA"})
        required_fields = [
            "current_price",
            "fifty_two_week_high",
            "fifty_two_week_low",
            "fifty_day_ma",
            "two_hundred_day_ma",
            "volume",
            "avg_volume",
            "price_change_pct",
        ]
        for field in required_fields:
            assert hasattr(result, field), f"Missing field: {field}"

    def test_get_technical_data_values(self, patch_yfinance) -> None:
        """Test that returned values match mock data."""
        result = get_technical_data.invoke({"ticker": "NVDA"})
        assert result.current_price == 875.50
        assert result.fifty_two_week_high == 950.00
        assert result.volume == 45000000

    def test_get_technical_data_is_langchain_tool(self) -> None:
        """Test that get_technical_data is a LangChain tool."""
        assert hasattr(get_technical_data, "invoke")
        assert hasattr(get_technical_data, "name")


class TestGetFundamentalData:
    """Tests for get_fundamental_data tool."""

    def test_get_fundamental_data_returns_dict(self, patch_yfinance) -> None:
        """Test that get_fundamental_data returns FundamentalData model."""
        result = get_fundamental_data.invoke({"ticker": "NVDA"})
        assert isinstance(result, FundamentalData)

    def test_get_fundamental_data_has_required_keys(self, patch_yfinance) -> None:
        """Test that result contains all required fundamental data fields."""
        result = get_fundamental_data.invoke({"ticker": "NVDA"})
        required_fields = [
            "market_cap",
            "pe_ratio",
            "forward_pe",
            "eps",
            "revenue",
            "profit_margin",
            "debt_to_equity",
            "sector",
            "industry",
        ]
        for field in required_fields:
            assert hasattr(result, field), f"Missing field: {field}"

    def test_get_fundamental_data_values(self, patch_yfinance) -> None:
        """Test that returned values match mock data."""
        result = get_fundamental_data.invoke({"ticker": "NVDA"})
        assert result.market_cap == 2100000000000
        assert result.pe_ratio == 65.4
        assert result.sector == "Technology"

    def test_get_fundamental_data_is_langchain_tool(self) -> None:
        """Test that get_fundamental_data is a LangChain tool."""
        assert hasattr(get_fundamental_data, "invoke")
        assert hasattr(get_fundamental_data, "name")


class TestGetPriceHistory:
    """Tests for get_price_history function."""

    @staticmethod
    def _create_mock_history() -> pd.DataFrame:
        """Create mock historical price data."""
        dates = pd.date_range("2024-01-01", periods=5, freq="D")
        data = {
            "Open": [100.0, 101.0, 102.0, 101.5, 103.0],
            "High": [102.0, 103.0, 104.0, 103.5, 105.0],
            "Low": [99.0, 100.0, 101.0, 100.5, 102.0],
            "Close": [101.0, 102.0, 103.0, 102.5, 104.0],
            "Volume": [1000000, 1100000, 1200000, 1150000, 1300000],
        }
        return pd.DataFrame(data, index=dates)

    def test_get_price_history_returns_price_history_model(self) -> None:
        """Test that get_price_history returns PriceHistory model."""
        mock_ticker = MagicMock()
        mock_ticker.history.return_value = self._create_mock_history()

        with patch("think_only_once.tools.yfinance_tools.yf.Ticker", return_value=mock_ticker):
            result = get_price_history("NVDA", "6mo")
            assert isinstance(result, PriceHistory)

    def test_get_price_history_has_correct_ticker(self) -> None:
        """Test that result contains correct ticker."""
        mock_ticker = MagicMock()
        mock_ticker.history.return_value = self._create_mock_history()

        with patch("think_only_once.tools.yfinance_tools.yf.Ticker", return_value=mock_ticker):
            result = get_price_history("AAPL", "6mo")
            assert result.ticker == "AAPL"

    def test_get_price_history_has_correct_period(self) -> None:
        """Test that result contains correct period."""
        mock_ticker = MagicMock()
        mock_ticker.history.return_value = self._create_mock_history()

        with patch("think_only_once.tools.yfinance_tools.yf.Ticker", return_value=mock_ticker):
            result = get_price_history("NVDA", "1y")
            assert result.period == "1y"

    def test_get_price_history_data_points_count(self) -> None:
        """Test that result contains correct number of data points."""
        mock_ticker = MagicMock()
        mock_ticker.history.return_value = self._create_mock_history()

        with patch("think_only_once.tools.yfinance_tools.yf.Ticker", return_value=mock_ticker):
            result = get_price_history("NVDA", "6mo")
            assert len(result.data) == 5

    def test_get_price_history_data_point_fields(self) -> None:
        """Test that data points contain all required fields."""
        mock_ticker = MagicMock()
        mock_ticker.history.return_value = self._create_mock_history()

        with patch("think_only_once.tools.yfinance_tools.yf.Ticker", return_value=mock_ticker):
            result = get_price_history("NVDA", "6mo")
            point = result.data[0]
            assert hasattr(point, "date")
            assert hasattr(point, "open")
            assert hasattr(point, "high")
            assert hasattr(point, "low")
            assert hasattr(point, "close")
            assert hasattr(point, "volume")

    def test_get_price_history_data_values(self) -> None:
        """Test that data point values are correct."""
        mock_ticker = MagicMock()
        mock_ticker.history.return_value = self._create_mock_history()

        with patch("think_only_once.tools.yfinance_tools.yf.Ticker", return_value=mock_ticker):
            result = get_price_history("NVDA", "6mo")
            point = result.data[0]
            assert point.open == 100.0
            assert point.high == 102.0
            assert point.low == 99.0
            assert point.close == 101.0
            assert point.volume == 1000000

    def test_get_price_history_default_period(self) -> None:
        """Test that default period is 6mo."""
        mock_ticker = MagicMock()
        mock_ticker.history.return_value = self._create_mock_history()

        with patch("think_only_once.tools.yfinance_tools.yf.Ticker", return_value=mock_ticker):
            result = get_price_history("NVDA")
            assert result.period == "6mo"
            mock_ticker.history.assert_called_with(period="6mo")

    def test_get_price_history_empty_data(self) -> None:
        """Test handling of empty historical data."""
        mock_ticker = MagicMock()
        mock_ticker.history.return_value = pd.DataFrame()

        with patch("think_only_once.tools.yfinance_tools.yf.Ticker", return_value=mock_ticker):
            result = get_price_history("INVALID", "6mo")
            assert result.data == []
