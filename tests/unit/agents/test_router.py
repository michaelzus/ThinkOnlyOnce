"""Tests for smart router agent."""

from unittest.mock import MagicMock, patch

import pytest

from think_only_once.agents.router import RouterDecision, route_query


class TestRouterDecision:
    """Tests for RouterDecision Pydantic model."""

    def test_router_decision_schema(self) -> None:
        """Test RouterDecision has correct fields."""
        decision = RouterDecision(
            ticker="NVDA",
            run_technical=True,
            run_fundamental=False,
            run_news=True,
            reasoning="Test reasoning",
        )
        assert decision.ticker == "NVDA"
        assert decision.run_technical is True
        assert decision.run_fundamental is False

    def test_router_decision_requires_ticker(self) -> None:
        """Test RouterDecision requires ticker field."""
        with pytest.raises(ValueError):
            RouterDecision(
                run_technical=True,
                run_fundamental=True,
                run_news=True,
                reasoning="Missing ticker",
            )


class TestRouteQuery:
    """Tests for route_query function."""

    def test_route_query_full_analysis(self, mock_router_decision) -> None:
        """Test routing returns the LLM decision."""
        mock_router = MagicMock()
        mock_router.invoke.return_value = mock_router_decision

        with patch("think_only_once.agents.router.create_router", return_value=mock_router):
            result = route_query("Analyze NVDA stock")
            assert result.run_technical is True
            assert result.run_fundamental is True
            assert result.run_news is True
