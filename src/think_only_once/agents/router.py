"""Smart router agent for query analysis and routing decisions."""

from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate

from think_only_once.agents.base import get_llm


class RouterDecision(BaseModel):
    """Structured output for routing decisions."""

    ticker: str = Field(description="Extracted stock ticker symbol (e.g., NVDA, AAPL)")
    run_technical: bool = Field(description="True if user needs price/trend/volume analysis")
    run_fundamental: bool = Field(description="True if user needs valuation/financial health analysis")
    run_news: bool = Field(description="True if user needs news/sentiment analysis")
    run_macro: bool = Field(default=True, description="True if user needs market-wide macro analysis (usually enabled)")
    reasoning: str = Field(description="Brief explanation of the routing decision")


ROUTER_PROMPT = """You are a query router for a stock analysis system.

Analyze the user's query and determine:
1. Which stock ticker they are asking about
2. Which type(s) of analysis they need

Analysis types:
- TECHNICAL: Price trends, moving averages, volume, support/resistance, chart patterns
- FUNDAMENTAL: P/E ratio, market cap, revenue, earnings, valuation, financials
- NEWS: Recent headlines, sentiment, market news, events, announcements
- MACRO: Market-wide conditions, SPY/VIX levels, sector performance, Fear & Greed

Rules:
- If the query is vague like "analyze X" or "tell me about X", enable ALL analysis types
- If the query mentions specific aspects, only enable relevant types
- MACRO is usually enabled for comprehensive analysis (market context is valuable)
- Always extract the ticker symbol (convert company names to tickers if needed)

Examples:
- "What's the news on NVDA?" → run_news=True, run_macro=True
- "Is AAPL overvalued?" → run_fundamental=True, run_macro=True
- "TSLA price and trends" → run_technical=True, run_macro=True
- "Full analysis of MSFT" → all True
- "Should I buy GOOGL?" → all True (needs comprehensive view)
"""


def create_router():
    """Create the smart router with structured output.

    Returns:
        Runnable chain that produces RouterDecision objects.
    """
    llm = get_llm()
    structured_llm = llm.with_structured_output(RouterDecision)

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", ROUTER_PROMPT),
            ("human", "{query}"),
        ]
    )

    return prompt | structured_llm


def route_query(query: str) -> RouterDecision:
    """Route a user query to determine which agents to invoke.

    Args:
        query: User's stock analysis query.

    Returns:
        RouterDecision with ticker and analysis type selections.
    """
    router = create_router()
    return router.invoke({"query": query})
