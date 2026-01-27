"""Pydantic models for tool outputs and data schemas."""

from pydantic import BaseModel, Field


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
