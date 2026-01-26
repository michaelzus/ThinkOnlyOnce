"""News Analyst agent for sentiment and headline analysis."""

from langchain.agents import create_agent
from langgraph.graph.state import CompiledStateGraph

from think_only_once.agents.base import get_llm
from think_only_once.config.settings import get_settings
from think_only_once.tools.search_tools import search_stock_news


NEWS_ANALYST_PROMPT = """You are a News Analyst specializing in market sentiment.

Your task is to analyze recent news about a stock and assess market sentiment.

Focus on:
1. Overall sentiment (positive/negative/neutral/mixed)
2. Key headlines and their impact
3. Emerging themes or trends
4. Potential catalysts or risks
5. News-driven price outlook

Be concise and actionable in your analysis.
"""


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
        system_prompt=NEWS_ANALYST_PROMPT,
        debug=settings.agents.verbose,
    )
