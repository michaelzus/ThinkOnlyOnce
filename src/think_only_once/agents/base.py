"""Base agent factory with shared LLM configuration."""

import os
from typing import Any

from langchain_openai import ChatOpenAI
from langchain.agents import create_agent as create_react_agent
from think_only_once.config.settings import get_settings
from langgraph.graph.state import CompiledStateGraph


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
    )


def create_agent(
    system_prompt: str,
    tools: list,
    *,
    debug: bool = False,
) -> CompiledStateGraph:
    """Create a ReAct agent using LangChain's agent factory.

    This function uses `langchain.agents.create_agent` which provides
    an optimized implementation of the ReAct (Reasoning + Acting) pattern.

    Args:
        system_prompt: System prompt to guide the agent's behavior and instructions.
        tools: List of tools for the agent to use (must be callable with @tool decorator).
        debug: Whether to enable agent execution debug output (currently unused).

    Returns:
        CompiledStateGraph: Compiled agent graph ready for invocation with {"messages": [...]} format.

    Example:
        >>> from langchain_core.tools import tool
        >>> @tool
        ... def search(query: str) -> str:
        ...     '''Search for information.'''
        ...     return f"Results for {query}"
        >>> agent = create_agent(
        ...     system_prompt="You are a helpful assistant.",
        ...     tools=[search]
        ... )
        >>> result = agent.invoke({"messages": [{"role": "user", "content": "Search for AI"}]})
        >>> print(result["messages"][-1].content)
    """
    llm = get_llm()

    agent: Any = create_react_agent(model=llm, tools=tools, system_prompt=system_prompt, debug=debug)

    return agent
