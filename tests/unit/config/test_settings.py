"""Tests for configuration module."""

from pathlib import Path

import pytest

from think_only_once.config.settings import AgentSettings, LLMSettings, Settings


class TestLLMSettings:
    """Tests for LLMSettings class."""

    def test_llm_settings_defaults(self) -> None:
        """Test LLMSettings has correct default values."""
        settings = LLMSettings()
        assert settings.model == "gpt-4o-mini"
        assert settings.temperature == 0.2
        assert settings.base_url is None
        assert settings.api_key is None
        assert settings.max_tokens == 1024

    def test_llm_settings_custom_values(self) -> None:
        """Test LLMSettings accepts custom values."""
        settings = LLMSettings(
            model="gpt-4o-mini",
            temperature=0.7,
            base_url="https://api.openai.com/v1",
            api_key="test-key",
            max_tokens=2048,
        )
        assert settings.model == "gpt-4o-mini"
        assert settings.temperature == 0.7
        assert settings.api_key == "test-key"

    def test_llm_settings_temperature_lower_bound(self) -> None:
        """Test temperature cannot be below 0.0."""
        with pytest.raises(ValueError):
            LLMSettings(temperature=-0.1)

    def test_llm_settings_temperature_upper_bound(self) -> None:
        """Test temperature cannot exceed 2.0."""
        with pytest.raises(ValueError):
            LLMSettings(temperature=2.1)

    def test_llm_settings_max_tokens_positive(self) -> None:
        """Test max_tokens must be positive."""
        with pytest.raises(ValueError):
            LLMSettings(max_tokens=0)


class TestAgentSettings:
    """Tests for AgentSettings class."""

    def test_agent_settings_defaults(self) -> None:
        """Test AgentSettings has correct default values."""
        settings = AgentSettings()
        assert settings.verbose is False

    def test_agent_settings_custom_verbose(self) -> None:
        """Test AgentSettings accepts custom verbose setting."""
        settings = AgentSettings(verbose=False)
        assert settings.verbose is False


class TestSettings:
    """Tests for Settings container class."""

    def test_settings_can_be_created(self) -> None:
        """Test Settings can be instantiated with defaults."""
        settings = Settings()
        assert settings.llm is not None
        assert settings.agents is not None
        assert isinstance(settings.llm, LLMSettings)
        assert isinstance(settings.agents, AgentSettings)

    def test_settings_from_yaml_valid(self, tmp_path: Path) -> None:
        """Test loading settings from a valid YAML file."""
        yaml_content = """
llm:
  model: "gpt-4o"
  temperature: 0.5
  max_tokens: 512

agents:
  verbose: false
"""
        yaml_file = tmp_path / "config.yaml"
        yaml_file.write_text(yaml_content)

        settings = Settings.from_yaml(yaml_file)
        assert settings.llm.model == "gpt-4o"
        assert settings.llm.temperature == 0.5
        assert settings.llm.max_tokens == 512
        assert settings.agents.verbose is False

    def test_settings_from_yaml_missing_file(self, tmp_path: Path) -> None:
        """Test graceful handling of missing YAML file."""
        missing_file = tmp_path / "nonexistent.yaml"
        settings = Settings.from_yaml(missing_file)
        assert settings.llm.model == "gpt-4o-mini"

    def test_settings_from_yaml_partial_config(self, tmp_path: Path) -> None:
        """Test loading YAML with only some sections."""
        yaml_content = """
llm:
  temperature: 0.8
"""
        yaml_file = tmp_path / "partial.yaml"
        yaml_file.write_text(yaml_content)

        settings = Settings.from_yaml(yaml_file)
        assert settings.llm.temperature == 0.8
        assert settings.llm.model == "gpt-4o-mini"
        assert settings.agents.verbose is False
