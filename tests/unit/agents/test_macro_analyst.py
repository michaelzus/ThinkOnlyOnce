"""Tests for macro analyst agent."""

from unittest.mock import MagicMock, patch

from think_only_once.agents.macro_analyst import MACRO_ANALYST_PROMPT, create_macro_analyst


class TestMacroAnalyst:
    """Tests for macro analyst agent."""

    def test_create_macro_analyst_returns_executor(self, mock_env_api_key) -> None:
        """Test that create_macro_analyst returns an agent executor."""
        with patch("think_only_once.agents.macro_analyst.get_llm", return_value=MagicMock()):
            agent = create_macro_analyst()
            assert hasattr(agent, "invoke")

    def test_create_macro_analyst_has_correct_tools(self, mock_env_api_key) -> None:
        """Test that macro analyst is created with the correct tools."""
        with patch("think_only_once.agents.macro_analyst.get_llm") as mock_get_llm, patch(
            "think_only_once.agents.macro_analyst.create_agent"
        ) as mock_create_agent:
            mock_get_llm.return_value = MagicMock()
            mock_create_agent.return_value = MagicMock()

            create_macro_analyst()

            # Verify create_agent was called with tools list containing 2 tools
            call_kwargs = mock_create_agent.call_args
            tools = call_kwargs.kwargs.get("tools") or call_kwargs[1].get("tools")
            assert len(tools) == 2


class TestMacroAnalystPrompt:
    """Tests for macro analyst prompt content."""

    def test_prompt_contains_vix_interpretation(self) -> None:
        """Test that prompt includes VIX interpretation guidelines."""
        assert "VIX Interpretation" in MACRO_ANALYST_PROMPT
        assert "Below 15" in MACRO_ANALYST_PROMPT
        assert "Above 30" in MACRO_ANALYST_PROMPT

    def test_prompt_contains_fear_greed_interpretation(self) -> None:
        """Test that prompt includes Fear & Greed interpretation."""
        assert "Fear & Greed Interpretation" in MACRO_ANALYST_PROMPT
        assert "Extreme Fear" in MACRO_ANALYST_PROMPT
        assert "Extreme Greed" in MACRO_ANALYST_PROMPT

    def test_prompt_contains_spy_trend_guidance(self) -> None:
        """Test that prompt includes SPY trend guidance."""
        assert "SPY Trend" in MACRO_ANALYST_PROMPT
        assert "50D" in MACRO_ANALYST_PROMPT
        assert "200D" in MACRO_ANALYST_PROMPT
        assert "Bullish" in MACRO_ANALYST_PROMPT
        assert "Bearish" in MACRO_ANALYST_PROMPT

    def test_prompt_emphasizes_objectivity(self) -> None:
        """Test that prompt emphasizes data-driven objectivity."""
        assert "objective" in MACRO_ANALYST_PROMPT.lower()
        assert "data-driven" in MACRO_ANALYST_PROMPT.lower()
