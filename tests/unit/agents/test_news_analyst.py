"""Tests for news analyst agent."""

from unittest.mock import MagicMock, patch

from think_only_once.agents.news_analyst import create_news_analyst


class TestNewsAnalyst:
    """Tests for news analyst agent."""

    def test_create_news_analyst_returns_executor(self, mock_env_api_key) -> None:
        """Test that create_news_analyst returns an agent executor."""
        with patch("think_only_once.agents.base.get_llm", return_value=MagicMock()):
            agent = create_news_analyst()
            assert hasattr(agent, "invoke")
