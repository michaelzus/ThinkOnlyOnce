"""Tests for investment analyst agent."""

from unittest.mock import MagicMock, patch

from think_only_once.agents.investment_analyst import (
    create_investment_analyst_chain,
    generate_investment_outlook,
)
from think_only_once.enums import AgentEnum
from think_only_once.prompts import get_prompt_text


class TestCreateInvestmentAnalystChain:
    """Tests for create_investment_analyst_chain function."""

    def test_create_investment_analyst_chain_returns_chain(
        self, mock_env_api_key, mock_chat_openai
    ) -> None:
        """Test that create_investment_analyst_chain returns a chain."""
        chain = create_investment_analyst_chain()
        assert chain is not None
        assert hasattr(chain, "invoke")


class TestGenerateInvestmentOutlook:
    """Tests for generate_investment_outlook function."""

    def test_generate_investment_outlook_with_all_data(
        self, mock_env_api_key
    ) -> None:
        """Test outlook generation with all analysis data."""
        mock_chain = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "**Recommendation:** BUY"
        mock_chain.invoke.return_value = mock_response

        with patch("think_only_once.agents.investment_analyst.create_investment_analyst_chain", return_value=mock_chain):
            result = generate_investment_outlook(
                ticker="NVDA",
                technical_analysis="Bullish trend",
                fundamental_analysis="Strong financials",
                news_analysis="Positive sentiment",
            )
        assert isinstance(result, str)
        assert len(result) > 0

    def test_generate_investment_outlook_with_partial_data(
        self, mock_env_api_key
    ) -> None:
        """Test outlook generation with partial analysis data."""
        mock_chain = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "**Recommendation:** HOLD"
        mock_chain.invoke.return_value = mock_response

        with patch("think_only_once.agents.investment_analyst.create_investment_analyst_chain", return_value=mock_chain):
            result = generate_investment_outlook(
                ticker="AAPL",
                technical_analysis="Price trending up",
                fundamental_analysis=None,
                news_analysis=None,
            )
        assert isinstance(result, str)

    def test_generate_investment_outlook_handles_all_none(
        self, mock_env_api_key
    ) -> None:
        """Test outlook generation when all analyses are None."""
        mock_chain = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "Insufficient data"
        mock_chain.invoke.return_value = mock_response

        with patch("think_only_once.agents.investment_analyst.create_investment_analyst_chain", return_value=mock_chain):
            result = generate_investment_outlook(
                ticker="TSLA",
                technical_analysis=None,
                fundamental_analysis=None,
                news_analysis=None,
            )
        assert isinstance(result, str)


class TestInvestmentAnalystPrompt:
    """Tests for the investment analyst prompt."""

    def test_prompt_contains_recommendation_section(self) -> None:
        """Test prompt mentions RECOMMENDATION."""
        assert "RECOMMENDATION" in get_prompt_text(AgentEnum.INVESTMENT_ANALYST)

    def test_prompt_contains_price_target_section(self) -> None:
        """Test prompt mentions PRICE TARGET."""
        assert "PRICE TARGET" in get_prompt_text(AgentEnum.INVESTMENT_ANALYST)

    def test_prompt_contains_risk_assessment_section(self) -> None:
        """Test prompt mentions RISK ASSESSMENT."""
        assert "RISK ASSESSMENT" in get_prompt_text(AgentEnum.INVESTMENT_ANALYST)

    def test_prompt_contains_investment_thesis_section(self) -> None:
        """Test prompt mentions INVESTMENT THESIS."""
        assert "INVESTMENT THESIS" in get_prompt_text(AgentEnum.INVESTMENT_ANALYST)

    def test_prompt_has_placeholders(self) -> None:
        """Test prompt has required placeholders."""
        prompt = get_prompt_text(AgentEnum.INVESTMENT_ANALYST)
        assert "{ticker}" in prompt
        assert "{technical_analysis}" in prompt
        assert "{fundamental_analysis}" in prompt
        assert "{news_analysis}" in prompt
