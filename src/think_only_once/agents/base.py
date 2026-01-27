"""Base module with shared LLM configuration."""

import os

from langchain_openai import ChatOpenAI
from think_only_once.config.settings import get_settings


def get_llm() -> ChatOpenAI:
    """Create LLM instance with centralized configuration.

    All agents use the same LLM settings from config.yaml.
    Supports OpenAI (default) or any OpenAI-compatible endpoint.

    Returns:
        Configured ChatOpenAI instance.

    Raises:
        ValueError: If API key is not set.
    """
    settings = get_settings()
    llm_config = settings.llm

    # Get API key from config file or OPENAI_API_KEY env var
    api_key = llm_config.api_key or os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError(
            "API key required. Set OPENAI_API_KEY env var or specify api_key in config.yaml"
        )

    return ChatOpenAI(
        model=llm_config.model,
        temperature=llm_config.temperature,
        base_url=llm_config.base_url,
        api_key=api_key,  # type: ignore[arg-type]
        max_tokens=llm_config.max_tokens,  # type: ignore[call-arg]
        max_retries=3,  # Retry on rate limit (429) errors with exponential backoff
        request_timeout=60,  # Timeout per request in seconds
    )
