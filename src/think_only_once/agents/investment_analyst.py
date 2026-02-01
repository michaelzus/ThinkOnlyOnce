"""Investment Analyst agent for generating AI-powered investment outlook."""

from langchain_core.prompts import ChatPromptTemplate

from think_only_once.agents.base import get_llm


INVESTMENT_ANALYST_PROMPT = """You are a Senior Investment Analyst with expertise in equity research.

Your task is to synthesize all available analysis data and provide an actionable investment outlook.

Based on the analysis provided below, generate a comprehensive investment outlook that includes:

1. **RECOMMENDATION**: BUY, HOLD, or SELL with confidence level (High/Medium/Low)
2. **PRICE TARGET**: Specific price target with brief methodology explanation
3. **RISK ASSESSMENT**: LOW, MEDIUM, or HIGH with top 3 key risks
4. **INVESTMENT THESIS**: 2-3 sentence summary of the investment case

Guidelines:
- Be specific and actionable in your recommendations
- Base price targets on available fundamental data (P/E, growth rates, etc.)
- Consider both upside potential and downside risks
- Consider macro conditions (market health, VIX, sentiment) in your risk assessment
- If data is limited, acknowledge uncertainty in your confidence level

---

Stock Ticker: {ticker}

Technical Analysis:
{technical_analysis}

Fundamental Analysis:
{fundamental_analysis}

News & Sentiment Analysis:
{news_analysis}

Macro Analysis:
{macro_analysis}

---

Provide your investment outlook in the following format:

**Recommendation:** [BUY/HOLD/SELL] ([High/Medium/Low] Confidence)

**Price Target:** $[price] ([+/-X%] from current)
- [Brief methodology explanation]

**Risk Assessment:** [LOW/MEDIUM/HIGH]
- Key Risks:
  1. [Risk 1]
  2. [Risk 2]
  3. [Risk 3]

**Investment Thesis:**
[2-3 sentence summary]
"""


def create_investment_analyst_chain():
    """Create the investment analyst chain for generating AI outlook.

    Returns:
        A LangChain chain that generates investment outlook from analysis data.
    """
    llm = get_llm()

    prompt = ChatPromptTemplate.from_messages([
        ("system", INVESTMENT_ANALYST_PROMPT),
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
