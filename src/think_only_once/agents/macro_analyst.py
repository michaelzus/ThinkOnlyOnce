"""Macro Risk Agent for market-wide risk assessment.

This agent assesses market-wide conditions including:
- Market health (SPY trend)
- Market volatility (VIX level)
- Sector performance
- Market sentiment (Fear & Greed)
- Geopolitical risks
"""

from langchain.agents import create_agent
from langgraph.graph.state import CompiledStateGraph

from think_only_once.agents.base import get_llm
from think_only_once.config.settings import get_settings
from think_only_once.enums import AgentEnum
from think_only_once.prompts import get_prompt_text
from think_only_once.tools.macro_tools import get_market_indices, search_geopolitical_news


def create_macro_analyst() -> CompiledStateGraph:
    """Create macro analyst agent using LangGraph's create_react_agent.

    Returns:
        CompiledStateGraph: Compiled agent graph that accepts {"messages": [...]} input format.
    """
    settings = get_settings()
    llm = get_llm()
    tools = [get_market_indices, search_geopolitical_news]

    return create_agent(
        model=llm,
        tools=tools,
        system_prompt=get_prompt_text(AgentEnum.MACRO_ANALYST),
        debug=settings.agents.verbose,
    )
