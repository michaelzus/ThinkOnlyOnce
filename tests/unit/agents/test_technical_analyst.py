"""Tests for technical analyst agent."""

from unittest.mock import MagicMock, patch

from think_only_once.agents.technical_analyst import create_technical_analyst


class TestTechnicalAnalyst:
    """Tests for technical analyst agent."""

    def test_create_technical_analyst_returns_executor(self, mock_env_api_key) -> None:
        """Test that create_technical_analyst returns an agent executor."""
        with patch("think_only_once.agents.base.get_llm", return_value=MagicMock()):
            agent = create_technical_analyst()
            assert hasattr(agent, "invoke")
