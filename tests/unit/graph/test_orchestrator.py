"""Tests for LangGraph orchestrator."""

from unittest.mock import MagicMock, patch

from think_only_once.graph.orchestrator import StockAnalyzerOrchestrator, get_orchestrator


class TestStockAnalyzerOrchestrator:
    """Tests for StockAnalyzerOrchestrator class."""

    def test_orchestrator_initialization(self) -> None:
        """Test orchestrator can be instantiated."""
        orchestrator = StockAnalyzerOrchestrator()
        assert orchestrator is not None
        assert orchestrator._technical_agent is None
        assert orchestrator._graph is None

    def test_orchestrator_lazy_agent_init(self, mock_env_api_key) -> None:
        """Test agents are lazily initialized."""
        orchestrator = StockAnalyzerOrchestrator()
        with patch("think_only_once.graph.orchestrator.create_technical_analyst") as mock_create:
            mock_create.return_value = MagicMock()
            _ = orchestrator.technical_agent
            assert orchestrator._technical_agent is not None

    def test_router_node(self, sample_analysis_state) -> None:
        """Test router_node correctly routes queries."""
        orchestrator = StockAnalyzerOrchestrator()
        with patch("think_only_once.graph.orchestrator.route_query") as mock_route:
            mock_route.return_value.ticker = "NVDA"
            mock_route.return_value.run_technical = True
            mock_route.return_value.run_fundamental = True
            mock_route.return_value.run_news = False

            result = orchestrator.router_node(sample_analysis_state)
            assert result["ticker"] == "NVDA"
            assert result["run_technical"] is True
            assert result["run_news"] is False

    def test_technical_analysis_node_enabled(self, sample_analysis_state) -> None:
        """Test technical analysis runs when enabled."""
        orchestrator = StockAnalyzerOrchestrator()
        sample_analysis_state["run_technical"] = True

        mock_agent = MagicMock()
        mock_message = MagicMock()
        mock_message.content = "Technical analysis results"
        mock_agent.invoke.return_value = {"messages": [mock_message]}
        orchestrator._technical_agent = mock_agent

        result = orchestrator.technical_analysis_node(sample_analysis_state)
        assert result["technical_analysis"] == "Technical analysis results"

    def test_technical_analysis_node_disabled(self, sample_analysis_state) -> None:
        """Test technical analysis skipped when disabled."""
        orchestrator = StockAnalyzerOrchestrator()
        sample_analysis_state["run_technical"] = False

        result = orchestrator.technical_analysis_node(sample_analysis_state)
        assert result["technical_analysis"] is None

    def test_aggregator_node(self, completed_analysis_state) -> None:
        """Test report aggregation."""
        orchestrator = StockAnalyzerOrchestrator()
        result = orchestrator.aggregator_node(completed_analysis_state)
        assert "aggregated_sections" in result
        assert len(result["aggregated_sections"]) == 3

    def test_investment_analyst_node(self, completed_analysis_state) -> None:
        """Test AI outlook generation and report assembly."""
        orchestrator = StockAnalyzerOrchestrator()
        with patch("think_only_once.graph.orchestrator.generate_investment_outlook") as mock_outlook:
            mock_outlook.return_value = "BUY outlook"
            result = orchestrator.investment_analyst_node(completed_analysis_state)
            assert result["ai_outlook"] == "BUY outlook"
            assert "Stock Analysis Report" in result["final_report"]

    def test_build_graph_returns_compiled_graph(self) -> None:
        """Test build method returns compiled graph."""
        orchestrator = StockAnalyzerOrchestrator()
        graph = orchestrator.build()
        assert graph is not None
        assert hasattr(graph, "invoke")


class TestGetOrchestrator:
    """Tests for get_orchestrator singleton function."""

    def test_get_orchestrator_returns_instance(self) -> None:
        """Test get_orchestrator returns an orchestrator instance."""
        orchestrator = get_orchestrator()
        assert orchestrator is not None

    def test_get_orchestrator_singleton(self) -> None:
        """Test get_orchestrator returns same instance."""
        orch1 = get_orchestrator()
        orch2 = get_orchestrator()
        assert orch1 is orch2
