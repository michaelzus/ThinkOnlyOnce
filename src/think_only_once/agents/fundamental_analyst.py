"""Fundamental Analyst agent for valuation and financial health analysis."""

from langchain.agents import create_agent
from langgraph.graph.state import CompiledStateGraph

from think_only_once.agents.base import get_llm
from think_only_once.config.settings import get_settings
from think_only_once.prompts import get_prompt_text
from think_only_once.tools.yfinance_tools import get_fundamental_data


def create_fundamental_analyst() -> CompiledStateGraph:
    """Create fundamental analyst agent using LangGraph's create_react_agent.

    Returns:
        CompiledStateGraph: Compiled agent graph that accepts {"messages": [...]} input format.
    """
    settings = get_settings()
    llm = get_llm()
    tools = [get_fundamental_data]

    return create_agent(
        model=llm,
        tools=tools,
        system_prompt=get_prompt_text("fundamental_analyst"),
        debug=settings.agents.verbose,
    )
