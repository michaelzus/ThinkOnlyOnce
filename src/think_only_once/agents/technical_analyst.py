"""Technical Analyst agent for price and trend analysis."""

from langchain.agents import create_agent
from langgraph.graph.state import CompiledStateGraph

from think_only_once.agents.base import get_llm
from think_only_once.config.settings import get_settings
from think_only_once.enums import AgentEnum
from think_only_once.prompts import get_prompt_text
from think_only_once.tools.yfinance_tools import get_technical_data


def create_technical_analyst() -> CompiledStateGraph:
    """Create technical analyst agent using LangGraph's create_react_agent.

    Returns:
        CompiledStateGraph: Compiled agent graph that accepts {"messages": [...]} input format.
    """
    settings = get_settings()
    llm = get_llm()
    tools = [get_technical_data]

    return create_agent(
        model=llm,
        tools=tools,
        system_prompt=get_prompt_text(AgentEnum.TECHNICAL_ANALYST),
        debug=settings.agents.verbose,
    )
