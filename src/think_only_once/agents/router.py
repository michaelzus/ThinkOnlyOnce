"""Smart router agent for query analysis and routing decisions."""

from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate

from think_only_once.agents.base import get_llm
from think_only_once.enums import AgentEnum
from think_only_once.prompts import get_prompt_text


class RouterDecision(BaseModel):
    """Structured output for routing decisions."""

    ticker: str = Field(description="Extracted stock ticker symbol (e.g., NVDA, AAPL)")
    run_technical: bool = Field(description="True if user needs price/trend/volume analysis")
    run_fundamental: bool = Field(description="True if user needs valuation/financial health analysis")
    run_news: bool = Field(description="True if user needs news/sentiment analysis")
    run_macro: bool = Field(default=True, description="True if user needs market-wide macro analysis (usually enabled)")
    reasoning: str = Field(description="Brief explanation of the routing decision")


def create_router():
    """Create the smart router with structured output.

    Returns:
        Runnable chain that produces RouterDecision objects.
    """
    llm = get_llm()
    structured_llm = llm.with_structured_output(RouterDecision)

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", get_prompt_text(AgentEnum.ROUTER)),
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
