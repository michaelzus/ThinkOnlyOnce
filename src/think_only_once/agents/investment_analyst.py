"""Investment Analyst agent for generating AI-powered investment outlook."""

from langchain_core.prompts import ChatPromptTemplate

from think_only_once.agents.base import get_llm
from think_only_once.enums import AgentEnum
from think_only_once.prompts import get_prompt_text


def create_investment_analyst_chain():
    """Create the investment analyst chain for generating AI outlook.

    Returns:
        A LangChain chain that generates investment outlook from analysis data.
    """
    llm = get_llm()

    prompt = ChatPromptTemplate.from_messages([
        ("system", get_prompt_text(AgentEnum.INVESTMENT_ANALYST)),
        ("human", "Generate an investment outlook for {ticker} based on the analysis above."),
    ])

    return prompt | llm


def generate_investment_outlook(
    ticker: str,
    technical_analysis: str | None,
    fundamental_analysis: str | None,
    news_analysis: str | None,
    macro_analysis: str | None = None,
) -> str:
    """Generate an AI-powered investment outlook.

    Args:
        ticker: Stock ticker symbol.
        technical_analysis: Technical analysis results (or None if not available).
        fundamental_analysis: Fundamental analysis results (or None if not available).
        news_analysis: News/sentiment analysis results (or None if not available).
        macro_analysis: Macro analysis results (or None if not available).

    Returns:
        Formatted investment outlook string.
    """
    chain = create_investment_analyst_chain()

    result = chain.invoke({
        "ticker": ticker,
        "technical_analysis": technical_analysis or "Not available",
        "fundamental_analysis": fundamental_analysis or "Not available",
        "news_analysis": news_analysis or "Not available",
        "macro_analysis": macro_analysis or "Not available",
    })

    return result.content
