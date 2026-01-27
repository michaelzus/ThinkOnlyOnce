"""Tests for yfinance tools."""

from think_only_once.models import FundamentalData, TechnicalData
from think_only_once.tools.yfinance_tools import get_fundamental_data, get_technical_data


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
