"""News Analyst agent for sentiment and headline analysis."""

from langchain.agents import create_agent
from langgraph.graph.state import CompiledStateGraph

from think_only_once.agents.base import get_llm
from think_only_once.config.settings import get_settings
from think_only_once.enums import AgentEnum
from think_only_once.prompts import get_prompt_text
from think_only_once.tools.search_tools import search_stock_news


def create_news_analyst() -> CompiledStateGraph:
    """Create news analyst agent using LangGraph's create_react_agent.

    Returns:
        CompiledStateGraph: Compiled agent graph that accepts {"messages": [...]} input format.
    """
    settings = get_settings()
    llm = get_llm()
    tools = [search_stock_news]

    return create_agent(
        model=llm,
        tools=tools,
        system_prompt=get_prompt_text(AgentEnum.NEWS_ANALYST),
        debug=settings.agents.verbose,
    )
