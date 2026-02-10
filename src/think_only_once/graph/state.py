"""LangGraph state definitions."""

from typing import Annotated, TypedDict

from langgraph.graph.message import add_messages


class AnalysisState(TypedDict):
    """Shared state across all agents in the graph."""

    # Input
    ticker: str
    query: str

    # Router decisions
    run_technical: bool
    run_fundamental: bool
    run_news: bool
    run_macro: bool

    # Agent outputs (prose from LLM agents)
    technical_analysis: str | None
    fundamental_analysis: str | None
    news_analysis: str | None
    macro_analysis: str | None

    # Investment Analyst output
    ai_outlook: str | None

    # Message history (for debugging)
    messages: Annotated[list, add_messages]
