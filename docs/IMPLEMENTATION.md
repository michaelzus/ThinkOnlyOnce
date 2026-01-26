# Implementation Guide

This document contains the complete implementation details for the Stock Market Multi-Agent Analysis System.

## Table of Contents

1. [Project Structure](#1-project-structure)
2. [Configuration Module](#2-configuration-module)
3. [Tool Implementations](#3-tool-implementations)
4. [Agent Definitions](#4-agent-definitions)
5. [LangGraph Orchestrator](#5-langgraph-orchestrator)
6. [Main Entry Point](#6-main-entry-point)
7. [Dependencies](#7-dependencies)
8. [Configuration Examples](#8-configuration-examples)

---

## 1. Project Structure

```
src/
├── __init__.py
├── main.py                 # Entry point, runs the demo
├── config/
│   ├── __init__.py
│   ├── settings.py         # Pydantic settings (LLM config)
│   └── config.yaml         # YAML configuration file
├── agents/
│   ├── __init__.py
│   ├── base.py             # Base agent factory with shared LLM
│   ├── router.py           # Smart router (supervisor)
│   ├── technical_analyst.py
│   ├── fundamental_analyst.py
│   ├── news_analyst.py
│   └── investment_analyst.py
├── tools/
│   ├── __init__.py
│   ├── models.py           # Pydantic models for tool I/O
│   ├── yfinance_tools.py   # Technical & Fundamental tools
│   └── search_tools.py     # DuckDuckGo tool
└── graph/
    ├── __init__.py
    ├── state.py            # AnalysisState definition
    └── orchestrator.py     # LangGraph definition
```

---

## 2. Configuration Module

### 2.1 YAML Configuration File

```yaml
# src/config/config.yaml

llm:
  model: "gpt-4o-mini"
  temperature: 0.2
  base_url: null  # Uses default OpenAI endpoint
  api_key: null   # Set via OPENAI_API_KEY env var or here
  max_tokens: 1024

# Agent-specific settings
agents:
  verbose: true   # Show agent reasoning in output
```

### 2.2 Pydantic Settings

```python
# src/config/settings.py

import os
from functools import lru_cache
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings
import yaml


class LLMSettings(BaseSettings):
    """LLM configuration shared by all agents."""
    
    model: str = Field(default="gpt-4o-mini", description="Model name")
    temperature: float = Field(default=0.2, ge=0.0, le=2.0, description="Sampling temperature")
    base_url: str | None = Field(default=None, description="API endpoint URL (None = OpenAI default)")
    api_key: str | None = Field(default=None, description="API key (defaults to OPENAI_API_KEY env var)")
    max_tokens: int = Field(default=1024, ge=1, description="Maximum tokens in response")


class AgentSettings(BaseSettings):
    """Agent behavior configuration."""
    
    verbose: bool = Field(default=True, description="Show agent reasoning")


class Settings(BaseSettings):
    """Root settings container."""
    
    llm: LLMSettings = Field(default_factory=LLMSettings)
    agents: AgentSettings = Field(default_factory=AgentSettings)
    
    @classmethod
    def from_yaml(cls, path: Path | str) -> "Settings":
        """Load settings from YAML file."""
        path = Path(path)
        if not path.exists():
            return cls()
        
        with open(path) as f:
            data = yaml.safe_load(f) or {}
        
        return cls(
            llm=LLMSettings(**data.get("llm", {})),
            agents=AgentSettings(**data.get("agents", {})),
        )


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    config_path = Path(__file__).parent / "config.yaml"
    return Settings.from_yaml(config_path)
```

### 2.3 Base Agent Factory

```python
# src/agents/base.py

import os
from typing import Any

from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

from src.config.settings import get_settings


def get_llm() -> ChatOpenAI:
    """Create LLM instance with centralized configuration.

    All agents use the same LLM settings from config.yaml.
    Supports OpenAI (default) or any OpenAI-compatible endpoint.

    Returns:
        Configured ChatOpenAI instance.

    Raises:
        ValueError: If API key is not set.
    """
    settings = get_settings()
    llm_config = settings.llm

    api_key = llm_config.api_key or os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("API key required. Set OPENAI_API_KEY env var or api_key in config.yaml")

    return ChatOpenAI(
        model=llm_config.model,
        temperature=llm_config.temperature,
        base_url=llm_config.base_url,
        api_key=api_key,
        max_tokens=llm_config.max_tokens,
    )


def create_agent(
    system_prompt: str,
    tools: list,
    *,
    debug: bool = False,
) -> Any:
    """Create a ReAct agent using LangGraph's prebuilt function.

    This function uses `langgraph.prebuilt.create_react_agent` which provides
    an optimized implementation of the ReAct (Reasoning + Acting) pattern.

    Args:
        system_prompt: System prompt to guide the agent's behavior and instructions.
        tools: List of tools for the agent to use (must be callable with @tool decorator).
        debug: Whether to enable agent execution debug output (currently unused).

    Returns:
        Compiled agent graph ready for invocation with {"messages": [...]} format.

    Example:
        >>> agent = create_agent(
        ...     system_prompt="You are a helpful assistant.",
        ...     tools=[search_tool]
        ... )
        >>> result = agent.invoke({"messages": [{"role": "user", "content": "Hello"}]})
        >>> print(result["messages"][-1].content)
    """
    llm = get_llm()

    agent = create_react_agent(
        model=llm,
        tools=tools,
        prompt=system_prompt,
    )

    return agent
```

---

## 3. Tool Implementations

### 3.1 Pydantic Models for Tools

```python
# src/tools/models.py

from pydantic import BaseModel, Field


class TechnicalData(BaseModel):
    """Output schema for technical analysis tool."""

    current_price: float | None = Field(description="Current stock price")
    price_change_pct: float | None = Field(description="Year-to-date price change percentage")
    fifty_day_ma: float | None = Field(description="50-day moving average")
    two_hundred_day_ma: float | None = Field(description="200-day moving average")
    fifty_two_week_high: float | None = Field(description="52-week high price")
    fifty_two_week_low: float | None = Field(description="52-week low price")
    volume: int | None = Field(description="Last trading volume")
    avg_volume: int | None = Field(description="3-month average volume")


class FundamentalData(BaseModel):
    """Output schema for fundamental analysis tool."""

    market_cap: int | None = Field(description="Market capitalization in USD")
    pe_ratio: float | None = Field(description="Trailing P/E ratio")
    forward_pe: float | None = Field(description="Forward P/E ratio")
    eps: float | None = Field(description="Earnings per share")
    revenue: int | None = Field(description="Total revenue in USD")
    profit_margin: float | None = Field(description="Profit margin percentage")
    debt_to_equity: float | None = Field(description="Debt to equity ratio")
    dividend_yield: float | None = Field(description="Dividend yield percentage")
    sector: str | None = Field(description="Company sector")
    industry: str | None = Field(description="Company industry")


class NewsData(BaseModel):
    """Output schema for news search tool."""

    headlines: list[str] = Field(description="List of news headlines")
    snippets: list[str] = Field(description="List of news snippets")
    search_query: str = Field(description="The search query used")
```

### 3.2 YFinance Technical Tool

```python
# src/tools/yfinance_tools.py

import yfinance as yf
from langchain_core.tools import tool

from src.tools.models import TechnicalData, FundamentalData


@tool
def get_technical_data(ticker: str) -> TechnicalData:
    """
    Fetch technical analysis data for a stock.

    Args:
        ticker: Stock ticker symbol (e.g., NVDA, AAPL, MSFT)

    Returns:
        TechnicalData with price, moving averages, volume data
    """
    stock = yf.Ticker(ticker)
    fast_info = stock.fast_info

    return TechnicalData(
        current_price=fast_info.get("last_price") or fast_info.get("previous_close"),
        fifty_two_week_high=fast_info.get("year_high"),
        fifty_two_week_low=fast_info.get("year_low"),
        fifty_day_ma=fast_info.get("fifty_day_average"),
        two_hundred_day_ma=fast_info.get("two_hundred_day_average"),
        volume=fast_info.get("last_volume"),
        avg_volume=fast_info.get("three_month_average_volume"),
        price_change_pct=fast_info.get("year_change"),
    )
```

### 3.3 YFinance Fundamental Tool

```python
@tool
def get_fundamental_data(ticker: str) -> FundamentalData:
    """
    Fetch fundamental analysis data for a stock.

    Args:
        ticker: Stock ticker symbol (e.g., NVDA, AAPL, MSFT)

    Returns:
        FundamentalData with financial metrics like P/E, market cap, revenue
    """
    stock = yf.Ticker(ticker)
    info = stock.info

    return FundamentalData(
        market_cap=info.get("marketCap"),
        pe_ratio=info.get("trailingPE"),
        forward_pe=info.get("forwardPE"),
        eps=info.get("trailingEps"),
        revenue=info.get("totalRevenue"),
        profit_margin=info.get("profitMargins"),
        debt_to_equity=info.get("debtToEquity"),
        dividend_yield=info.get("dividendYield"),
        sector=info.get("sector"),
        industry=info.get("industry"),
    )
```

### 3.4 DuckDuckGo News Tool

```python
# src/tools/search_tools.py

import re
from langchain_community.tools import DuckDuckGoSearchResults
from langchain_core.tools import tool

from src.tools.models import NewsData


@tool
def search_stock_news(ticker: str) -> NewsData:
    """
    Search for recent news about a stock.

    Args:
        ticker: Stock ticker symbol (e.g., NVDA, AAPL, MSFT)

    Returns:
        NewsData with headlines and snippets about the stock
    """
    search = DuckDuckGoSearchResults(num_results=5)
    query = f"{ticker} stock news latest"
    raw_results = search.invoke(query)

    # Parse results into structured format
    headlines = []
    snippets = []

    # DuckDuckGoSearchResults returns a string, parse it
    if isinstance(raw_results, str):
        # Extract titles and snippets from the raw string
        title_matches = re.findall(r"title:\s*([^,\]]+)", raw_results)
        snippet_matches = re.findall(r"snippet:\s*([^,\]]+)", raw_results)
        headlines = [t.strip() for t in title_matches]
        snippets = [s.strip() for s in snippet_matches]

    return NewsData(
        headlines=headlines,
        snippets=snippets,
        search_query=query,
    )
```

---

## 4. Agent Definitions

### 4.1 Smart Router Agent

```python
# src/agents/router.py

from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate

from src.agents.base import get_llm


class RouterDecision(BaseModel):
    """Structured output for routing decisions."""
    
    ticker: str = Field(description="Extracted stock ticker symbol (e.g., NVDA, AAPL)")
    run_technical: bool = Field(
        description="True if user needs price/trend/volume analysis"
    )
    run_fundamental: bool = Field(
        description="True if user needs valuation/financial health analysis"
    )
    run_news: bool = Field(
        description="True if user needs news/sentiment analysis"
    )
    reasoning: str = Field(description="Brief explanation of the routing decision")


ROUTER_PROMPT = """You are a query router for a stock analysis system.

Analyze the user's query and determine:
1. Which stock ticker they are asking about
2. Which type(s) of analysis they need

Analysis types:
- TECHNICAL: Price trends, moving averages, volume, support/resistance, chart patterns
- FUNDAMENTAL: P/E ratio, market cap, revenue, earnings, valuation, financials
- NEWS: Recent headlines, sentiment, market news, events, announcements

Rules:
- If the query is vague like "analyze X" or "tell me about X", enable ALL analysis types
- If the query mentions specific aspects, only enable relevant types
- Always extract the ticker symbol (convert company names to tickers if needed)

Examples:
- "What's the news on NVDA?" → run_news=True only
- "Is AAPL overvalued?" → run_fundamental=True only
- "TSLA price and trends" → run_technical=True only
- "Full analysis of MSFT" → all True
- "Should I buy GOOGL?" → all True (needs comprehensive view)
"""


def create_router():
    """Create the smart router with structured output."""
    llm = get_llm()
    
    # Use structured output for reliable parsing
    structured_llm = llm.with_structured_output(RouterDecision)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", ROUTER_PROMPT),
        ("human", "{query}"),
    ])
    
    return prompt | structured_llm


def route_query(query: str) -> RouterDecision:
    """Route a user query to determine which agents to invoke."""
    router = create_router()
    return router.invoke({"query": query})
```

### 4.2 Technical Analyst Agent

```python
# src/agents/technical_analyst.py

from typing import Any

from src.agents.base import create_agent
from src.config.settings import get_settings
from src.tools.yfinance_tools import get_technical_data

TECHNICAL_ANALYST_PROMPT = """You are a Technical Analyst specializing in stock price analysis.

Your task is to analyze the technical indicators for a given stock and provide insights.

Focus on:
1. Price trend (bullish/bearish/neutral)
2. Support and resistance levels
3. Moving average signals (golden cross, death cross)
4. Volume analysis
5. Short-term price outlook

Be concise and actionable in your analysis.
"""


def create_technical_analyst() -> Any:
    """Create technical analyst agent using LangGraph's create_react_agent.

    Returns:
        Compiled agent graph that accepts {"messages": [...]} input format.
    """
    settings = get_settings()
    tools = [get_technical_data]

    return create_agent(
        system_prompt=TECHNICAL_ANALYST_PROMPT,
        tools=tools,
        debug=settings.agents.verbose,
    )
```

### 4.3 Fundamental Analyst Agent

```python
# src/agents/fundamental_analyst.py

from typing import Any

from src.agents.base import create_agent
from src.config.settings import get_settings
from src.tools.yfinance_tools import get_fundamental_data

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


def create_fundamental_analyst() -> Any:
    """Create fundamental analyst agent using LangGraph's create_react_agent.

    Returns:
        Compiled agent graph that accepts {"messages": [...]} input format.
    """
    settings = get_settings()
    tools = [get_fundamental_data]

    return create_agent(
        system_prompt=FUNDAMENTAL_ANALYST_PROMPT,
        tools=tools,
        debug=settings.agents.verbose,
    )
```

### 4.4 News Analyst Agent

```python
# src/agents/news_analyst.py

from typing import Any

from src.agents.base import create_agent
from src.config.settings import get_settings
from src.tools.search_tools import search_stock_news

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


def create_news_analyst() -> Any:
    """Create news analyst agent using LangGraph's create_react_agent.

    Returns:
        Compiled agent graph that accepts {"messages": [...]} input format.
    """
    settings = get_settings()
    tools = [search_stock_news]

    return create_agent(
        system_prompt=NEWS_ANALYST_PROMPT,
        tools=tools,
        debug=settings.agents.verbose,
    )
```

### 4.5 Investment Analyst Agent

```python
# src/agents/investment_analyst.py

from langchain_core.prompts import ChatPromptTemplate

from src.agents.base import get_llm


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
- If data is limited, acknowledge uncertainty in your confidence level

---

Stock Ticker: {ticker}

Technical Analysis:
{technical_analysis}

Fundamental Analysis:
{fundamental_analysis}

News & Sentiment Analysis:
{news_analysis}

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
    """Create the investment analyst chain for generating AI outlook."""
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
) -> str:
    """Generate an AI-powered investment outlook."""
    chain = create_investment_analyst_chain()

    result = chain.invoke({
        "ticker": ticker,
        "technical_analysis": technical_analysis or "Not available",
        "fundamental_analysis": fundamental_analysis or "Not available",
        "news_analysis": news_analysis or "Not available",
    })

    return result.content
```

---

## 5. LangGraph Orchestrator

```python
# src/graph/orchestrator.py

from langgraph.graph import StateGraph, START, END
from langgraph.graph.graph import CompiledGraph

from src.graph.state import AnalysisState
from src.agents.router import route_query
from src.agents.technical_analyst import create_technical_analyst
from src.agents.fundamental_analyst import create_fundamental_analyst
from src.agents.news_analyst import create_news_analyst
from src.agents.investment_analyst import generate_investment_outlook


class StockAnalyzerOrchestrator:
    """Orchestrator for the multi-agent stock analysis workflow.
    
    This class encapsulates the LangGraph workflow, managing agent lifecycle
    and defining the graph structure for stock analysis.
    
    Attributes:
        _technical_agent: Lazy-initialized technical analyst agent.
        _fundamental_agent: Lazy-initialized fundamental analyst agent.
        _news_agent: Lazy-initialized news analyst agent.
        _graph: Compiled LangGraph workflow.
    """
    
    def __init__(self) -> None:
        """Initialize the orchestrator with lazy agent initialization."""
        self._technical_agent = None
        self._fundamental_agent = None
        self._news_agent = None
        self._graph: CompiledGraph | None = None
    
    # =========================================================================
    # Agent Accessors (Lazy Initialization)
    # =========================================================================
    
    @property
    def technical_agent(self):
        """Get or create the technical analyst agent."""
        if self._technical_agent is None:
            self._technical_agent = create_technical_analyst()
        return self._technical_agent
    
    @property
    def fundamental_agent(self):
        """Get or create the fundamental analyst agent."""
        if self._fundamental_agent is None:
            self._fundamental_agent = create_fundamental_analyst()
        return self._fundamental_agent
    
    @property
    def news_agent(self):
        """Get or create the news analyst agent."""
        if self._news_agent is None:
            self._news_agent = create_news_analyst()
        return self._news_agent
    
    # =========================================================================
    # Node Methods
    # =========================================================================
    
    def router_node(self, state: AnalysisState) -> dict:
        """Smart router: analyze query and decide which agents to invoke."""
        decision = route_query(state["query"])
        return {
            "ticker": decision.ticker,
            "run_technical": decision.run_technical,
            "run_fundamental": decision.run_fundamental,
            "run_news": decision.run_news,
        }
    
    def technical_analysis_node(self, state: AnalysisState) -> dict:
        """Run technical analysis if requested by router."""
        if not state.get("run_technical"):
            return {"technical_analysis": None}
        
        result = self.technical_agent.invoke({
            "messages": [{"role": "user", "content": f"Analyze {state['ticker']}"}]
        })
        content = result["messages"][-1].content
        return {"technical_analysis": content}
    
    def fundamental_analysis_node(self, state: AnalysisState) -> dict:
        """Run fundamental analysis if requested by router."""
        if not state.get("run_fundamental"):
            return {"fundamental_analysis": None}
        
        result = self.fundamental_agent.invoke({
            "messages": [{"role": "user", "content": f"Analyze {state['ticker']}"}]
        })
        content = result["messages"][-1].content
        return {"fundamental_analysis": content}
    
    def news_analysis_node(self, state: AnalysisState) -> dict:
        """Run news analysis if requested by router."""
        if not state.get("run_news"):
            return {"news_analysis": None}
        
        result = self.news_agent.invoke({
            "messages": [{"role": "user", "content": f"Analyze news for {state['ticker']}"}]
        })
        content = result["messages"][-1].content
        return {"news_analysis": content}
    
    def aggregator_node(self, state: AnalysisState) -> dict:
        """Aggregate all analyses into sections for the report."""
        sections = []
        
        if state.get("technical_analysis"):
            sections.append(f"## Technical Analysis\n{state['technical_analysis']}")
        
        if state.get("fundamental_analysis"):
            sections.append(f"## Fundamental Analysis\n{state['fundamental_analysis']}")
        
        if state.get("news_analysis"):
            sections.append(f"## News & Sentiment Analysis\n{state['news_analysis']}")
        
        return {"_aggregated_sections": sections}
    
    def investment_analyst_node(self, state: AnalysisState) -> dict:
        """Generate AI investment outlook and compile final report."""
        ai_outlook = generate_investment_outlook(
            ticker=state["ticker"],
            technical_analysis=state.get("technical_analysis"),
            fundamental_analysis=state.get("fundamental_analysis"),
            news_analysis=state.get("news_analysis"),
        )
        
        sections = state.get("_aggregated_sections", [])
        sections.append(f"## AI Investment Outlook\n{ai_outlook}")
        
        report = f"""# Stock Analysis Report: {state["ticker"]}

{chr(10).join(sections)}

---
*Generated by Multi-Agent Stock Analyzer*
"""
        return {"ai_outlook": ai_outlook, "final_report": report}
    
    # =========================================================================
    # Graph Construction
    # =========================================================================
    
    def build(self) -> CompiledGraph:
        """Build and compile the LangGraph workflow.
        
        Returns:
            Compiled graph ready for invocation.
        """
        if self._graph is not None:
            return self._graph
        
        workflow = StateGraph(AnalysisState)
        
        # Add nodes
        workflow.add_node("router", self.router_node)
        workflow.add_node("technical_analyst", self.technical_analysis_node)
        workflow.add_node("fundamental_analyst", self.fundamental_analysis_node)
        workflow.add_node("news_analyst", self.news_analysis_node)
        workflow.add_node("aggregator", self.aggregator_node)
        workflow.add_node("investment_analyst", self.investment_analyst_node)
        
        # Define graph flow: START → router → analysts → aggregator → investment_analyst → END
        workflow.add_edge(START, "router")
        workflow.add_edge("router", "technical_analyst")
        workflow.add_edge("technical_analyst", "fundamental_analyst")
        workflow.add_edge("fundamental_analyst", "news_analyst")
        workflow.add_edge("news_analyst", "aggregator")
        workflow.add_edge("aggregator", "investment_analyst")
        workflow.add_edge("investment_analyst", END)
        
        self._graph = workflow.compile()
        return self._graph
    
    def invoke(self, query: str) -> str:
        """Run the analysis workflow for a given query.
        
        Args:
            query: Natural language query about a stock.
        
        Returns:
            Final analysis report as a string.
        """
        graph = self.build()
        
        initial_state = {
            "query": query,
            "ticker": "",
            "run_technical": False,
            "run_fundamental": False,
            "run_news": False,
            "technical_analysis": None,
            "fundamental_analysis": None,
            "news_analysis": None,
            "ai_outlook": None,
            "final_report": None,
            "messages": [],
        }
        
        result = graph.invoke(initial_state)
        return result["final_report"]


# Module-level instance for convenience
_orchestrator: StockAnalyzerOrchestrator | None = None


def get_orchestrator() -> StockAnalyzerOrchestrator:
    """Get or create the singleton orchestrator instance."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = StockAnalyzerOrchestrator()
    return _orchestrator
```

---

## 6. Main Entry Point

```python
# src/main.py

from src.graph.orchestrator import get_orchestrator


def analyze_stock(query: str) -> str:
    """Analyze a stock using the multi-agent system with smart routing.
    
    Args:
        query: Natural language query (e.g., "What's the news on NVDA?",
               "Full analysis of AAPL", "Is TSLA overvalued?")
    
    Returns:
        Analysis report (only includes requested analyses)
    
    Examples:
        >>> analyze_stock("Analyze NVDA")  # Full analysis
        >>> analyze_stock("What's the news on AAPL?")  # News only
        >>> analyze_stock("Check TSLA technicals")  # Technical only
    """
    orchestrator = get_orchestrator()
    return orchestrator.invoke(query)


def main() -> None:
    """Entry point for the CLI."""
    import sys
    
    query = sys.argv[1] if len(sys.argv) > 1 else "Analyze NVDA stock"
    
    print(f"Query: {query}\n")
    report = analyze_stock(query)
    print(report)


if __name__ == "__main__":
    main()
```

---

## 7. Dependencies

### 7.1 Required Packages

The project uses `pyproject.toml` for dependency management following modern Python packaging standards.

#### Core Dependencies

```toml
dependencies = [
    "langchain>=0.3.0",
    "langchain-openai>=0.2.0",
    "langchain-community>=0.3.0",
    "langgraph>=0.2.0",
    "yfinance>=0.2.40",
    "ddgs>=1.0.0",
    "pydantic>=2.0.0",
    "pydantic-settings>=2.0.0",
    "pyyaml>=6.0.0",
    "python-dotenv>=1.0.0",
]
```

#### Development Dependencies

```toml
[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "pytest-asyncio>=0.21.0",
    "black>=24.0.0",
    "mypy>=1.0.0",
    "flake8>=7.0.0",
    "Flake8-pyproject>=1.2.0",
    "pydocstyle>=6.0.0",
    "darglint>=1.8.0",
    "pre-commit>=3.0.0",
    "types-PyYAML>=6.0.0",
]
```

**Installation:**
```bash
# Install core dependencies
pip install -e .

# Install with development dependencies
pip install -e ".[dev]"
```

### 7.2 Environment Variables

```bash
# Required: OpenAI API key
OPENAI_API_KEY=your-openai-api-key
```

---

## 8. Configuration Examples

### OpenAI (Default)

```yaml
# config/config.yaml
llm:
  model: "gpt-4o-mini"
  temperature: 0.0
  base_url: null  # Uses default OpenAI endpoint
  api_key: null   # Uses OPENAI_API_KEY env var
  max_tokens: 1024

agents:
  verbose: true
```

### Local LLM (Ollama, vLLM, etc.)

```yaml
# config/config.yaml
llm:
  model: "llama3.1"
  temperature: 0.0
  base_url: "http://localhost:11434/v1"
  api_key: "not-needed"  # Some local servers require a placeholder
  max_tokens: 2048

agents:
  verbose: true
```

---

*Implementation Guide Version: 1.0*
 