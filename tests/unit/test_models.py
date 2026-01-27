"""Unit tests for Pydantic models and parsing functions."""

import pytest

from think_only_once.models import InvestmentSummary, parse_investment_outlook


class TestParseInvestmentOutlook:
    """Tests for the parse_investment_outlook function."""

    def test_parse_complete_outlook(self) -> None:
        """Test parsing a complete investment outlook."""
        outlook = """**Recommendation:** BUY (High Confidence)

**Price Target:** $150.00 (+15% from current)
- Based on DCF analysis

**Risk Assessment:** MEDIUM
- Key Risks:
  1. Market volatility
  2. Competition
  3. Regulatory changes

**Investment Thesis:**
Strong growth potential with solid fundamentals and positive momentum."""

        result = parse_investment_outlook(outlook)

        assert result.recommendation == "BUY"
        assert result.confidence == "High"
        assert result.price_target == "$150.00 (+15% from current)"
        assert "Strong growth potential" in result.thesis

    def test_parse_hold_recommendation(self) -> None:
        """Test parsing a HOLD recommendation."""
        outlook = """**Recommendation:** HOLD (Medium Confidence)

**Price Target:** $85 (-5% from current)

**Investment Thesis:**
Wait for better entry point."""

        result = parse_investment_outlook(outlook)

        assert result.recommendation == "HOLD"
        assert result.confidence == "Medium"

    def test_parse_sell_recommendation(self) -> None:
        """Test parsing a SELL recommendation."""
        outlook = """**Recommendation:** SELL (Low Confidence)

**Price Target:** $50 (-20% from current)

**Investment Thesis:**
Overvalued relative to peers."""

        result = parse_investment_outlook(outlook)

        assert result.recommendation == "SELL"
        assert result.confidence == "Low"

    def test_parse_missing_fields_returns_na(self) -> None:
        """Test that missing fields return N/A."""
        outlook = "Some random text without structured format."

        result = parse_investment_outlook(outlook)

        assert result.recommendation == "N/A"
        assert result.confidence == "N/A"
        assert result.price_target == "N/A"
        assert result.thesis == "N/A"

    def test_parse_empty_string(self) -> None:
        """Test parsing an empty string."""
        result = parse_investment_outlook("")

        assert result.recommendation == "N/A"
        assert result.price_target == "N/A"


class TestInvestmentSummary:
    """Tests for the InvestmentSummary model."""

    def test_investment_summary_creation(self) -> None:
        """Test creating an InvestmentSummary instance."""
        summary = InvestmentSummary(
            recommendation="BUY",
            confidence="High",
            price_target="$100 (+10%)",
            thesis="Strong buy case.",
        )

        assert summary.recommendation == "BUY"
        assert summary.confidence == "High"
        assert summary.price_target == "$100 (+10%)"
        assert summary.thesis == "Strong buy case."
