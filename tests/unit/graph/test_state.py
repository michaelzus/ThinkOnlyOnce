"""Tests for LangGraph state definitions."""

from think_only_once.graph.state import AnalysisState


class TestAnalysisState:
    """Tests for AnalysisState TypedDict."""

    def test_analysis_state_is_typed_dict(self) -> None:
        """Test AnalysisState is a TypedDict."""
        assert hasattr(AnalysisState, "__annotations__")

    def test_analysis_state_has_required_keys(self) -> None:
        """Test AnalysisState has all required keys."""
        required_keys = [
            "ticker",
            "query",
            "run_technical",
            "run_fundamental",
            "run_news",
            "run_macro",
            "technical_analysis",
            "fundamental_analysis",
            "news_analysis",
            "macro_analysis",
            "ai_outlook",
            "final_report",
            "messages",
        ]
        annotations = AnalysisState.__annotations__
        for key in required_keys:
            assert key in annotations, f"Missing key: {key}"

    def test_analysis_state_can_be_instantiated(self) -> None:
        """Test AnalysisState can be created with valid data."""
        state: AnalysisState = {
            "ticker": "NVDA",
            "query": "Analyze NVDA stock",
            "run_technical": True,
            "run_fundamental": False,
            "run_news": False,
            "run_macro": False,
            "technical_analysis": None,
            "fundamental_analysis": None,
            "news_analysis": None,
            "macro_analysis": None,
            "ai_outlook": None,
            "final_report": None,
            "messages": [],
        }
        assert state["ticker"] == "NVDA"
        assert state["messages"] == []

    def test_analysis_state_accepts_analysis_data(self) -> None:
        """Test AnalysisState accepts populated analysis data."""
        state: AnalysisState = {
            "ticker": "AAPL",
            "query": "Analyze AAPL stock",
            "run_technical": True,
            "run_fundamental": True,
            "run_news": True,
            "run_macro": True,
            "technical_analysis": "Trend is bullish",
            "fundamental_analysis": "Overvalued but strong",
            "news_analysis": "Positive sentiment",
            "macro_analysis": "Supportive macro",
            "ai_outlook": "BUY with target $200",
            "final_report": "# Analysis Report\n...",
            "messages": [],
        }
        assert state["technical_analysis"] == "Trend is bullish"
        assert state["news_analysis"] == "Positive sentiment"
