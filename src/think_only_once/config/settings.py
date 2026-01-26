"""Configuration settings using Pydantic."""

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings


class LLMSettings(BaseSettings):
    """LLM configuration shared by all agents.

    Supports multiple LLM providers:
    - OpenAI (default)
    - Any OpenAI-compatible endpoint (Ollama, vLLM, etc.)
    """

    model: str = Field(default="gpt-4o-mini", description="Model name")
    temperature: float = Field(default=0.2, ge=0.0, le=2.0, description="Sampling temperature")
    base_url: str | None = Field(default=None, description="API endpoint URL (None = OpenAI default)")
    api_key: str | None = Field(
        default=None,
        description="API key (defaults to OPENAI_API_KEY env var)",
    )
    max_tokens: int = Field(default=1024, ge=1, description="Maximum tokens in response")


class AgentSettings(BaseSettings):
    """Agent behavior configuration."""

    verbose: bool = Field(default=False, description="Show agent reasoning")


class Settings(BaseSettings):
    """Root settings container."""

    llm: LLMSettings = Field(default_factory=LLMSettings)
    agents: AgentSettings = Field(default_factory=AgentSettings)

    @classmethod
    def from_yaml(cls, path: Path | str) -> "Settings":
        """Load settings from YAML file.

        Args:
            path: Path to YAML configuration file.

        Returns:
            Settings instance loaded from file.
        """
        import yaml

        path = Path(path)
        if not path.exists():
            return cls()

        with open(path) as f:
            data = yaml.safe_load(f) or {}

        return cls(
            llm=LLMSettings(**data.get("llm", {})),
            agents=AgentSettings(**data.get("agents", {})),
        )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Get cached settings instance.

    Returns:
        Cached Settings instance.
    """
    config_path = Path(__file__).parent / "config.yaml"
    return Settings.from_yaml(config_path)
