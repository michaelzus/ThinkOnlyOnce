"""Technical Analyst agent for price and trend analysis."""

from langchain.agents import create_agent
from langgraph.graph.state import CompiledStateGraph

from think_only_once.agents.base import get_llm
from think_only_once.config.settings import get_settings
from think_only_once.tools.yfinance_tools import get_technical_data


TECHNICAL_ANALYST_PROMPT = """You are a Technical Analyst specializing in stock price analysis.

Your task is to analyze the technical indicators for a given stock and provide insights.

Focus on:
1. Price trend (bullish/bearish/neutral)
2. Support and resistance levels
3. Moving average signals (golden cross, death cross)
4. Volume analysis
5. Short-term price outlook

Be concise and actionable in your analysis.
"""


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
        system_prompt=TECHNICAL_ANALYST_PROMPT,
        debug=settings.agents.verbose,
    )
