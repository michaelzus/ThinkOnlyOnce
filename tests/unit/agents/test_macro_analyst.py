"""Tests for macro analyst agent."""

from unittest.mock import MagicMock, patch

from think_only_once.agents.macro_analyst import create_macro_analyst
from think_only_once.prompts import get_prompt_text


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
        prompt = get_prompt_text("macro_analyst")
        assert "VIX Interpretation" in prompt
        assert "Below 15" in prompt
        assert "Above 30" in prompt

    def test_prompt_contains_fear_greed_interpretation(self) -> None:
        """Test that prompt includes Fear & Greed interpretation."""
        prompt = get_prompt_text("macro_analyst")
        assert "Fear & Greed Interpretation" in prompt
        assert "Extreme Fear" in prompt
        assert "Extreme Greed" in prompt

    def test_prompt_contains_spy_trend_guidance(self) -> None:
        """Test that prompt includes SPY trend guidance."""
        prompt = get_prompt_text("macro_analyst")
        assert "SPY Trend" in prompt
        assert "50D" in prompt
        assert "200D" in prompt
        assert "Bullish" in prompt
        assert "Bearish" in prompt

    def test_prompt_emphasizes_objectivity(self) -> None:
        """Test that prompt emphasizes data-driven objectivity."""
        prompt = get_prompt_text("macro_analyst")
        assert "objective" in prompt.lower()
        assert "data-driven" in prompt.lower()
