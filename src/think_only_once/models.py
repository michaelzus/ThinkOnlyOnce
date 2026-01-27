"""Pydantic models for tool outputs and data schemas."""

import re

from pydantic import BaseModel, Field


class InvestmentSummary(BaseModel):
    """Summary of investment recommendation for stdout output."""

    recommendation: str = Field(description="BUY, HOLD, or SELL recommendation")
    confidence: str = Field(description="Confidence level: High, Medium, or Low")
    price_target: str = Field(description="Target price with percentage change")
    thesis: str = Field(description="Investment thesis summary")


def parse_investment_outlook(outlook_text: str) -> InvestmentSummary:
    """Parse AI investment outlook text into structured summary.

    Args:
        outlook_text: Raw text from the investment analyst.

    Returns:
        Parsed InvestmentSummary with key fields.
    """
    # Extract recommendation (e.g., "BUY (High Confidence)")
    rec_match = re.search(r"\*\*Recommendation:\*\*\s*(BUY|HOLD|SELL)\s*\((\w+)\s*Confidence\)", outlook_text, re.IGNORECASE)
    recommendation = rec_match.group(1).upper() if rec_match else "N/A"
    confidence = rec_match.group(2).capitalize() if rec_match else "N/A"

    # Extract price target (e.g., "$150 (+15% from current)")
    price_match = re.search(r"\*\*Price Target:\*\*\s*(\$[\d,.]+\s*\([^)]+\))", outlook_text, re.IGNORECASE)
    price_target = price_match.group(1) if price_match else "N/A"

    # Extract investment thesis
    thesis_match = re.search(r"\*\*Investment Thesis:\*\*\s*(.+?)(?:\n\n|\Z)", outlook_text, re.DOTALL | re.IGNORECASE)
    thesis = thesis_match.group(1).strip() if thesis_match else "N/A"

    return InvestmentSummary(
        recommendation=recommendation,
        confidence=confidence,
        price_target=price_target,
        thesis=thesis,
    )


class TechnicalData(BaseModel):
    """Output schema for technical analysis tool."""

    current_price: float | None = Field(default=None, description="Current stock price")
    price_change_pct: float | None = Field(default=None, description="Year-to-date price change percentage")
    fifty_day_ma: float | None = Field(default=None, description="50-day moving average")
    two_hundred_day_ma: float | None = Field(default=None, description="200-day moving average")
    fifty_two_week_high: float | None = Field(default=None, description="52-week high price")
    fifty_two_week_low: float | None = Field(default=None, description="52-week low price")
    volume: int | None = Field(default=None, description="Last trading volume")
    avg_volume: int | None = Field(default=None, description="3-month average volume")


class FundamentalData(BaseModel):
    """Output schema for fundamental analysis tool."""

    market_cap: int | None = Field(default=None, description="Market capitalization in USD")
    pe_ratio: float | None = Field(default=None, description="Trailing P/E ratio")
    forward_pe: float | None = Field(default=None, description="Forward P/E ratio")
    eps: float | None = Field(default=None, description="Earnings per share")
    revenue: int | None = Field(default=None, description="Total revenue in USD")
    profit_margin: float | None = Field(default=None, description="Profit margin percentage")
    debt_to_equity: float | None = Field(default=None, description="Debt to equity ratio")
    dividend_yield: float | None = Field(default=None, description="Dividend yield percentage")
    sector: str | None = Field(default=None, description="Company sector")
    industry: str | None = Field(default=None, description="Company industry")


class NewsData(BaseModel):
    """Output schema for news search tool."""

    headlines: list[str] = Field(default_factory=list, description="List of news headlines")
    snippets: list[str] = Field(default_factory=list, description="List of news snippets")
    search_query: str = Field(description="The search query used")
