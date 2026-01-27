"""Tests for base agent factory."""

import os
from unittest.mock import MagicMock, patch

import pytest

from think_only_once.agents.base import get_llm


class TestGetLLM:
    """Tests for get_llm factory function."""

    def test_get_llm_with_env_api_key(self, mock_env_api_key) -> None:
        """Test get_llm succeeds with API key from environment."""
        with patch("think_only_once.agents.base.ChatOpenAI") as mock_chat:
            mock_chat.return_value = MagicMock()
            llm = get_llm()
            assert llm is not None
            mock_chat.assert_called_once()

    def test_get_llm_raises_without_api_key(self, clean_env) -> None:
        """Test get_llm raises ValueError when no API key is available."""
        with pytest.raises(ValueError, match="API key required"):
            get_llm()

    @pytest.mark.skipif(not os.environ.get("CI"), reason="CI only - depends on config.yaml")
    def test_get_llm_uses_config_settings(self, mock_env_api_key) -> None:
        """Test get_llm applies settings from config."""
        # Clear cache to ensure fresh config load
        from think_only_once.config.settings import get_settings
        get_settings.cache_clear()
        
        with patch("think_only_once.agents.base.ChatOpenAI") as mock_chat:
            mock_chat.return_value = MagicMock()
            get_llm()

            call_kwargs = mock_chat.call_args.kwargs
            assert call_kwargs["model"] == "gpt-4o-mini"
            assert call_kwargs["temperature"] == 0.2
            assert call_kwargs["max_tokens"] == 1024

    def test_get_llm_prefers_config_api_key(self, mock_env_api_key) -> None:
        """Test that config API key takes precedence over env var."""
        with patch("think_only_once.agents.base.get_settings") as mock_settings:
            mock_settings.return_value.llm.api_key = "config-key"
            mock_settings.return_value.llm.model = "test-model"
            mock_settings.return_value.llm.temperature = 0.5
            mock_settings.return_value.llm.base_url = "https://test.com"
            mock_settings.return_value.llm.max_tokens = 512

            with patch("think_only_once.agents.base.ChatOpenAI") as mock_chat:
                mock_chat.return_value = MagicMock()
                get_llm()

                call_kwargs = mock_chat.call_args.kwargs
                assert call_kwargs["api_key"] == "config-key"
