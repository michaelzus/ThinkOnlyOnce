"""Integration tests for the analysis workflow."""

from unittest.mock import MagicMock, patch

import pytest

from think_only_once.graph.orchestrator import StockAnalyzerOrchestrator


@pytest.mark.integration
class TestAnalysisWorkflow:
    """Integration tests for the full analysis workflow."""

    def test_full_workflow_with_mocked_dependencies(self) -> None:
        """Test complete workflow with all dependencies mocked."""
        orchestrator = StockAnalyzerOrchestrator()

        with patch("think_only_once.graph.orchestrator.route_query") as mock_route, patch(
            "think_only_once.graph.orchestrator.create_technical_analyst"
        ) as mock_tech, patch(
            "think_only_once.graph.orchestrator.create_fundamental_analyst"
        ) as mock_fund, patch(
            "think_only_once.graph.orchestrator.create_news_analyst"
        ) as mock_news, patch(
            "think_only_once.graph.orchestrator.generate_investment_outlook"
        ) as mock_outlook:
            mock_route.return_value.ticker = "NVDA"
            mock_route.return_value.run_technical = True
            mock_route.return_value.run_fundamental = True
            mock_route.return_value.run_news = True

            tech_msg = MagicMock()
            tech_msg.content = "Technical analysis"
            tech_agent = MagicMock()
            tech_agent.invoke.return_value = {"messages": [tech_msg]}

            fund_msg = MagicMock()
            fund_msg.content = "Fundamental analysis"
            fund_agent = MagicMock()
            fund_agent.invoke.return_value = {"messages": [fund_msg]}

            news_msg = MagicMock()
            news_msg.content = "News analysis"
            news_agent = MagicMock()
            news_agent.invoke.return_value = {"messages": [news_msg]}

            mock_tech.return_value = tech_agent
            mock_fund.return_value = fund_agent
            mock_news.return_value = news_agent
            mock_outlook.return_value = "**Recommendation:** BUY"

            result = orchestrator.invoke("Analyze NVDA stock")

            assert result is not None
            assert "NVDA" in result
            assert "Stock Analysis Report" in result

    def test_workflow_respects_router_decisions(self) -> None:
        """Test that workflow only runs agents selected by router."""
        orchestrator = StockAnalyzerOrchestrator()

        with patch("think_only_once.graph.orchestrator.route_query") as mock_route, patch(
            "think_only_once.graph.orchestrator.create_technical_analyst"
        ) as mock_tech, patch(
            "think_only_once.graph.orchestrator.create_fundamental_analyst"
        ) as mock_fund, patch(
            "think_only_once.graph.orchestrator.create_news_analyst"
        ) as mock_news, patch(
            "think_only_once.graph.orchestrator.generate_investment_outlook"
        ) as mock_outlook:
            mock_route.return_value.ticker = "AAPL"
            mock_route.return_value.run_technical = True
            mock_route.return_value.run_fundamental = False
            mock_route.return_value.run_news = False

            tech_msg = MagicMock()
            tech_msg.content = "Technical analysis"
            tech_agent = MagicMock()
            tech_agent.invoke.return_value = {"messages": [tech_msg]}
            mock_tech.return_value = tech_agent
            mock_fund.return_value = MagicMock()
            mock_news.return_value = MagicMock()
            mock_outlook.return_value = "**Recommendation:** HOLD"

            result = orchestrator.invoke("Check AAPL technicals")

            assert "Technical Analysis" in result
            assert "Fundamental Analysis" not in result
            assert "News & Sentiment Analysis" not in result
