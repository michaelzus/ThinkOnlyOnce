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
from think_only_once.tools.macro_tools import get_market_indices, search_geopolitical_news


MACRO_ANALYST_PROMPT = """You are a Macro Risk Analyst assessing market-wide conditions.

Your job is to provide CONTEXT about:
1. Overall market health (SPY trend vs 50D and 200D MA)
2. Market volatility (VIX level interpretation)
3. Sector performance (if applicable)
4. Market sentiment (Fear & Greed Index)
5. Geopolitical risks (if any)

VIX Interpretation:
- Below 15: Low volatility, complacent market
- 15-20: Normal volatility
- 20-30: Elevated volatility, increased uncertainty
- Above 30: High volatility, fear in the market

Fear & Greed Interpretation:
- 0-24: Extreme Fear (potential buying opportunity)
- 25-44: Fear
- 45-55: Neutral
- 56-75: Greed
- 76-100: Extreme Greed (potential caution)

SPY Trend:
- Above 50D and 200D MA: Bullish
- Above 50D, below 200D MA: Mixed
- Below 50D MA: Showing weakness
- Below both: Bearish

Be objective and data-driven. Focus on facts, not predictions.
Your output should summarize the current macro environment clearly.
"""


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
        system_prompt=MACRO_ANALYST_PROMPT,
        debug=settings.agents.verbose,
    )
