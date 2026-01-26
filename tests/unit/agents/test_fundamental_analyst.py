"""Tests for fundamental analyst agent."""

from unittest.mock import MagicMock, patch

from think_only_once.agents.fundamental_analyst import create_fundamental_analyst


class TestFundamentalAnalyst:
    """Tests for fundamental analyst agent."""

    def test_create_fundamental_analyst_returns_executor(self, mock_env_api_key) -> None:
        """Test that create_fundamental_analyst returns an agent executor."""
        with patch("think_only_once.agents.base.get_llm", return_value=MagicMock()):
            agent = create_fundamental_analyst()
            assert hasattr(agent, "invoke")
