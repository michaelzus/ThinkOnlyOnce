"""Fundamental Analyst agent for valuation and financial health analysis."""

from think_only_once.agents.base import create_agent
from think_only_once.config.settings import get_settings
from think_only_once.tools.yfinance_tools import get_fundamental_data
from langgraph.graph.state import CompiledStateGraph


FUNDAMENTAL_ANALYST_PROMPT = """You are a Fundamental Analyst specializing in company valuation.

Your task is to analyze the financial health and valuation of a given stock.

Focus on:
1. Valuation metrics (P/E ratio, forward P/E)
2. Profitability (margins, EPS)
3. Growth potential
4. Financial health (debt levels)
5. Investment thesis

Be concise and actionable in your analysis.
"""


def create_fundamental_analyst() -> CompiledStateGraph:
    """Create fundamental analyst agent using LangGraph's create_react_agent.

    Returns:
        CompiledStateGraph: Compiled agent graph that accepts {"messages": [...]} input format.
    """
    settings = get_settings()
    tools = [get_fundamental_data]

    return create_agent(
        system_prompt=FUNDAMENTAL_ANALYST_PROMPT,
        tools=tools,
        debug=settings.agents.verbose,
    )
