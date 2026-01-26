# Pytest Test Plan

## Stock Market Multi-Agent Analysis System

**Version:** 1.0  
**Status:** Draft  
**Purpose:** Comprehensive test plan for the ThinkOnlyOnce project

---

## Table of Contents

1. [Test Strategy Overview](#1-test-strategy-overview)
2. [Test Structure](#2-test-structure)
3. [Fixtures and Mocking](#3-fixtures-and-mocking)
4. [Unit Tests](#4-unit-tests)
5. [Integration Tests](#5-integration-tests)
6. [End-to-End Tests](#6-end-to-end-tests)
7. [Test Markers and Categories](#7-test-markers-and-categories)
8. [Coverage Requirements](#8-coverage-requirements)

---

## 1. Test Strategy Overview

### 1.1 Testing Philosophy

- **Unit Tests**: Test individual functions/classes in isolation with mocked dependencies
- **Integration Tests**: Test component interactions with mocked external services (LLM, APIs)
- **End-to-End Tests**: Full workflow tests (require API keys, marked as slow/integration)

### 1.2 Mocking Strategy

| Component | Mock Strategy |
|-----------|---------------|
| LLM (ChatOpenAI) | Mock `langchain_openai.ChatOpenAI` |
| YFinance API | Mock `yfinance.Ticker` |
| DuckDuckGo Search | Mock `langchain_community.tools.DuckDuckGoSearchResults` |
| Environment Variables | Use `monkeypatch` or `pytest-env` |

### 1.3 Test Priorities

1. **P0 (Critical)**: Config, State, Base Agent Factory
2. **P1 (High)**: Tools, Router, Individual Agents
3. **P2 (Medium)**: Orchestrator, Integration flows
4. **P3 (Low)**: E2E tests with real APIs

---

## 2. Test Structure

```
tests/
├── __init__.py
├── conftest.py                     # Shared fixtures
├── unit/
│   ├── __init__.py
│   ├── config/
│   │   ├── __init__.py
│   │   └── test_settings.py        # Settings, LLMSettings, AgentSettings
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── test_yfinance_tools.py  # get_technical_data, get_fundamental_data
│   │   └── test_search_tools.py    # search_stock_news
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── test_base.py            # get_llm factory
│   │   ├── test_router.py          # RouterDecision, route_query
│   │   ├── test_technical_analyst.py
│   │   ├── test_fundamental_analyst.py
│   │   ├── test_news_analyst.py
│   │   └── test_investment_analyst.py
│   └── graph/
│       ├── __init__.py
│       ├── test_state.py           # AnalysisState
│       └── test_orchestrator.py    # StockAnalyzerOrchestrator
├── integration/
│   ├── __init__.py
│   ├── test_router_workflow.py     # Router + agent selection
│   ├── test_analysis_workflow.py   # Full analysis with mocked LLM
│   └── test_orchestrator_flow.py   # Graph execution flow
└── e2e/
    ├── __init__.py
    └── test_full_analysis.py       # Real API tests (optional)
```

---

## 3. Fixtures and Mocking

### 3.1 conftest.py Fixtures

```python
# tests/conftest.py

"""Shared test fixtures and configuration."""

import pytest
from unittest.mock import MagicMock, patch


# =============================================================================
# Environment Fixtures
# =============================================================================

@pytest.fixture
def mock_env_api_key(monkeypatch):
    """Set up mock API key in environment."""
    monkeypatch.setenv("OPENAI_API_KEY", "test-api-key-12345")


@pytest.fixture
def clean_env(monkeypatch):
    """Remove API key from environment for negative tests."""
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)


# =============================================================================
# LLM Fixtures
# =============================================================================

@pytest.fixture
def mock_llm():
    """Create a mock LLM that returns predictable responses."""
    mock = MagicMock()
    mock.invoke.return_value.content = "Mock LLM response"
    return mock


@pytest.fixture
def mock_chat_openai(mock_llm):
    """Patch ChatOpenAI to return mock LLM."""
    with patch("think_only_once.agents.base.ChatOpenAI", return_value=mock_llm):
        yield mock_llm


# =============================================================================
# YFinance Fixtures
# =============================================================================

@pytest.fixture
def mock_yfinance_ticker():
    """Create mock yfinance Ticker with sample data."""
    mock_ticker = MagicMock()
    mock_ticker.info = {
        "currentPrice": 875.50,
        "regularMarketPrice": 875.50,
        "fiftyTwoWeekHigh": 950.00,
        "fiftyTwoWeekLow": 450.00,
        "fiftyDayAverage": 820.00,
        "twoHundredDayAverage": 750.00,
        "volume": 45000000,
        "averageVolume": 40000000,
        "regularMarketChangePercent": 2.5,
        "marketCap": 2100000000000,
        "trailingPE": 65.4,
        "forwardPE": 45.2,
        "trailingEps": 13.38,
        "totalRevenue": 60000000000,
        "profitMargins": 0.55,
        "debtToEquity": 41.5,
        "dividendYield": 0.0004,
        "sector": "Technology",
        "industry": "Semiconductors",
    }
    return mock_ticker


@pytest.fixture
def patch_yfinance(mock_yfinance_ticker):
    """Patch yfinance.Ticker to return mock."""
    with patch("think_only_once.tools.yfinance_tools.yf.Ticker", return_value=mock_yfinance_ticker):
        yield mock_yfinance_ticker


# =============================================================================
# DuckDuckGo Fixtures
# =============================================================================

@pytest.fixture
def mock_ddg_search():
    """Create mock DuckDuckGo search results."""
    mock = MagicMock()
    mock.invoke.return_value = (
        '[{"title": "NVDA hits record high", "snippet": "NVIDIA stock reaches new ATH..."},'
        '{"title": "AI demand surge", "snippet": "Data center revenue grows 200%..."}]'
    )
    return mock


@pytest.fixture
def patch_ddg_search(mock_ddg_search):
    """Patch DuckDuckGoSearchResults."""
    with patch(
        "think_only_once.tools.search_tools.DuckDuckGoSearchResults",
        return_value=mock_ddg_search
    ):
        yield mock_ddg_search


# =============================================================================
# State Fixtures
# =============================================================================

@pytest.fixture
def sample_analysis_state():
    """Create sample AnalysisState for testing."""
    return {
        "ticker": "NVDA",
        "query": "Analyze NVDA stock",
        "run_technical": True,
        "run_fundamental": True,
        "run_news": True,
        "technical_analysis": None,
        "fundamental_analysis": None,
        "news_analysis": None,
        "ai_outlook": None,
        "final_report": None,
        "messages": [],
    }


@pytest.fixture
def completed_analysis_state():
    """Create completed AnalysisState with all analyses."""
    return {
        "ticker": "NVDA",
        "query": "Analyze NVDA stock",
        "run_technical": True,
        "run_fundamental": True,
        "run_news": True,
        "technical_analysis": {"current_price": 875.50, "trend": "BULLISH"},
        "fundamental_analysis": {"pe_ratio": 65.4, "valuation": "OVERVALUED"},
        "news_analysis": {"sentiment": "POSITIVE", "headlines": ["AI demand surge"]},
        "ai_outlook": "BUY recommendation with $950 target",
        "final_report": "# Stock Analysis Report: NVDA\n...",
        "messages": [],
    }


# =============================================================================
# Router Fixtures
# =============================================================================

@pytest.fixture
def mock_router_decision():
    """Create mock RouterDecision for full analysis."""
    from unittest.mock import MagicMock
    decision = MagicMock()
    decision.ticker = "NVDA"
    decision.run_technical = True
    decision.run_fundamental = True
    decision.run_news = True
    decision.reasoning = "User requested full analysis"
    return decision
```

---

## 4. Unit Tests

### 4.1 Config Module Tests

**File:** `tests/unit/config/test_settings.py`

| Test ID | Test Name | Description | Priority |
|---------|-----------|-------------|----------|
| CFG-001 | `test_llm_settings_defaults` | Verify LLMSettings default values | P0 |
| CFG-002 | `test_llm_settings_custom_values` | Test LLMSettings with custom values | P0 |
| CFG-003 | `test_llm_settings_temperature_validation` | Validate temperature bounds (0.0-2.0) | P0 |
| CFG-004 | `test_agent_settings_defaults` | Verify AgentSettings default values | P0 |
| CFG-005 | `test_settings_container` | Test Settings root container | P0 |
| CFG-006 | `test_settings_from_yaml_valid` | Load settings from valid YAML file | P0 |
| CFG-007 | `test_settings_from_yaml_missing_file` | Handle missing YAML file gracefully | P0 |
| CFG-008 | `test_settings_from_yaml_partial` | Load partial YAML (missing sections) | P1 |
| CFG-009 | `test_get_settings_cached` | Verify get_settings returns cached instance | P1 |

```python
# tests/unit/config/test_settings.py

"""Tests for configuration module."""

import pytest
from pathlib import Path
from tempfile import NamedTemporaryFile

from think_only_once.config.settings import LLMSettings, AgentSettings, Settings


class TestLLMSettings:
    """Tests for LLMSettings class."""

    def test_llm_settings_defaults(self) -> None:
        """Test LLMSettings has correct default values."""
        settings = LLMSettings()
        assert settings.model == "gpt-4o-mini"
        assert settings.temperature == 0.2
        assert settings.base_url is None
        assert settings.api_key is None
        assert settings.max_tokens == 1024

    def test_llm_settings_custom_values(self) -> None:
        """Test LLMSettings accepts custom values."""
        settings = LLMSettings(
            model="gpt-4o-mini",
            temperature=0.7,
            base_url="https://api.openai.com/v1",
            api_key="test-key",
            max_tokens=2048,
        )
        assert settings.model == "gpt-4o-mini"
        assert settings.temperature == 0.7
        assert settings.api_key == "test-key"

    def test_llm_settings_temperature_lower_bound(self) -> None:
        """Test temperature cannot be below 0.0."""
        with pytest.raises(ValueError):
            LLMSettings(temperature=-0.1)

    def test_llm_settings_temperature_upper_bound(self) -> None:
        """Test temperature cannot exceed 2.0."""
        with pytest.raises(ValueError):
            LLMSettings(temperature=2.1)

    def test_llm_settings_max_tokens_positive(self) -> None:
        """Test max_tokens must be positive."""
        with pytest.raises(ValueError):
            LLMSettings(max_tokens=0)


class TestAgentSettings:
    """Tests for AgentSettings class."""

    def test_agent_settings_defaults(self) -> None:
        """Test AgentSettings has correct default values."""
        settings = AgentSettings()
        assert settings.verbose is True

    def test_agent_settings_custom_verbose(self) -> None:
        """Test AgentSettings accepts custom verbose setting."""
        settings = AgentSettings(verbose=False)
        assert settings.verbose is False


class TestSettings:
    """Tests for Settings container class."""

    def test_settings_can_be_created(self) -> None:
        """Test Settings can be instantiated with defaults."""
        settings = Settings()
        assert settings.llm is not None
        assert settings.agents is not None
        assert isinstance(settings.llm, LLMSettings)
        assert isinstance(settings.agents, AgentSettings)

    def test_settings_from_yaml_valid(self, tmp_path: Path) -> None:
        """Test loading settings from a valid YAML file."""
        yaml_content = """
llm:
  model: "gpt-4o"
  temperature: 0.5
  max_tokens: 512

agents:
  verbose: false
"""
        yaml_file = tmp_path / "config.yaml"
        yaml_file.write_text(yaml_content)

        settings = Settings.from_yaml(yaml_file)
        assert settings.llm.model == "gpt-4o"
        assert settings.llm.temperature == 0.5
        assert settings.llm.max_tokens == 512
        assert settings.agents.verbose is False

    def test_settings_from_yaml_missing_file(self, tmp_path: Path) -> None:
        """Test graceful handling of missing YAML file."""
        missing_file = tmp_path / "nonexistent.yaml"
        settings = Settings.from_yaml(missing_file)
        # Should return defaults
        assert settings.llm.model == "gpt-4o-mini"

    def test_settings_from_yaml_partial_config(self, tmp_path: Path) -> None:
        """Test loading YAML with only some sections."""
        yaml_content = """
llm:
  temperature: 0.8
"""
        yaml_file = tmp_path / "partial.yaml"
        yaml_file.write_text(yaml_content)

        settings = Settings.from_yaml(yaml_file)
        assert settings.llm.temperature == 0.8
        # Other values should be defaults
        assert settings.llm.model == "gpt-4o-mini"
        assert settings.agents.verbose is True
```

### 4.2 Tools Module Tests

**File:** `tests/unit/tools/test_yfinance_tools.py`

| Test ID | Test Name | Description | Priority |
|---------|-----------|-------------|----------|
| YF-001 | `test_get_technical_data_returns_dict` | Verify return type is dict | P1 |
| YF-002 | `test_get_technical_data_has_required_keys` | Check all required keys present | P1 |
| YF-003 | `test_get_technical_data_valid_ticker` | Test with valid ticker symbol | P1 |
| YF-004 | `test_get_technical_data_handles_missing_data` | Handle None/missing values | P1 |
| YF-005 | `test_get_fundamental_data_returns_dict` | Verify return type is dict | P1 |
| YF-006 | `test_get_fundamental_data_has_required_keys` | Check all required keys present | P1 |
| YF-007 | `test_get_fundamental_data_valid_ticker` | Test with valid ticker symbol | P1 |
| YF-008 | `test_tools_are_langchain_tools` | Verify tools have @tool decorator | P1 |

```python
# tests/unit/tools/test_yfinance_tools.py

"""Tests for yfinance tools."""

import pytest
from unittest.mock import patch, MagicMock

from think_only_once.tools.yfinance_tools import get_technical_data, get_fundamental_data


class TestGetTechnicalData:
    """Tests for get_technical_data tool."""

    def test_get_technical_data_returns_dict(self, patch_yfinance) -> None:
        """Test that get_technical_data returns a dictionary."""
        result = get_technical_data.invoke({"ticker": "NVDA"})
        assert isinstance(result, dict)

    def test_get_technical_data_has_required_keys(self, patch_yfinance) -> None:
        """Test that result contains all required technical data keys."""
        result = get_technical_data.invoke({"ticker": "NVDA"})
        required_keys = [
            "current_price",
            "fifty_two_week_high",
            "fifty_two_week_low",
            "fifty_day_ma",
            "two_hundred_day_ma",
            "volume",
            "avg_volume",
            "price_change_pct",
        ]
        for key in required_keys:
            assert key in result, f"Missing key: {key}"

    def test_get_technical_data_values(self, patch_yfinance) -> None:
        """Test that returned values match mock data."""
        result = get_technical_data.invoke({"ticker": "NVDA"})
        assert result["current_price"] == 875.50
        assert result["fifty_two_week_high"] == 950.00
        assert result["volume"] == 45000000

    def test_get_technical_data_is_langchain_tool(self) -> None:
        """Test that get_technical_data is a LangChain tool."""
        assert hasattr(get_technical_data, "invoke")
        assert hasattr(get_technical_data, "name")


class TestGetFundamentalData:
    """Tests for get_fundamental_data tool."""

    def test_get_fundamental_data_returns_dict(self, patch_yfinance) -> None:
        """Test that get_fundamental_data returns a dictionary."""
        result = get_fundamental_data.invoke({"ticker": "NVDA"})
        assert isinstance(result, dict)

    def test_get_fundamental_data_has_required_keys(self, patch_yfinance) -> None:
        """Test that result contains all required fundamental data keys."""
        result = get_fundamental_data.invoke({"ticker": "NVDA"})
        required_keys = [
            "market_cap",
            "pe_ratio",
            "forward_pe",
            "eps",
            "revenue",
            "profit_margin",
            "debt_to_equity",
            "sector",
            "industry",
        ]
        for key in required_keys:
            assert key in result, f"Missing key: {key}"

    def test_get_fundamental_data_values(self, patch_yfinance) -> None:
        """Test that returned values match mock data."""
        result = get_fundamental_data.invoke({"ticker": "NVDA"})
        assert result["market_cap"] == 2100000000000
        assert result["pe_ratio"] == 65.4
        assert result["sector"] == "Technology"

    def test_get_fundamental_data_is_langchain_tool(self) -> None:
        """Test that get_fundamental_data is a LangChain tool."""
        assert hasattr(get_fundamental_data, "invoke")
        assert hasattr(get_fundamental_data, "name")
```

**File:** `tests/unit/tools/test_search_tools.py`

| Test ID | Test Name | Description | Priority |
|---------|-----------|-------------|----------|
| DDG-001 | `test_search_stock_news_returns_string` | Verify return type is string | P1 |
| DDG-002 | `test_search_stock_news_constructs_query` | Verify query format | P1 |
| DDG-003 | `test_search_stock_news_is_langchain_tool` | Verify @tool decorator | P1 |

```python
# tests/unit/tools/test_search_tools.py

"""Tests for search tools."""

import pytest
from unittest.mock import patch, MagicMock

from think_only_once.tools.search_tools import search_stock_news


class TestSearchStockNews:
    """Tests for search_stock_news tool."""

    def test_search_stock_news_returns_string(self, patch_ddg_search) -> None:
        """Test that search_stock_news returns a string."""
        result = search_stock_news.invoke({"ticker": "NVDA"})
        assert isinstance(result, str)

    def test_search_stock_news_calls_ddg_with_correct_query(self, mock_ddg_search) -> None:
        """Test that DDG search is called with correct query format."""
        with patch(
            "think_only_once.tools.search_tools.DuckDuckGoSearchResults",
            return_value=mock_ddg_search
        ):
            search_stock_news.invoke({"ticker": "AAPL"})
            mock_ddg_search.invoke.assert_called_once()
            call_args = mock_ddg_search.invoke.call_args[0][0]
            assert "AAPL" in call_args
            assert "stock" in call_args
            assert "news" in call_args

    def test_search_stock_news_is_langchain_tool(self) -> None:
        """Test that search_stock_news is a LangChain tool."""
        assert hasattr(search_stock_news, "invoke")
        assert hasattr(search_stock_news, "name")
```

### 4.3 Agents Module Tests

**File:** `tests/unit/agents/test_base.py`

| Test ID | Test Name | Description | Priority |
|---------|-----------|-------------|----------|
| BASE-001 | `test_get_llm_with_env_api_key` | Create LLM with env var API key | P0 |
| BASE-002 | `test_get_llm_with_config_api_key` | Create LLM with config API key | P0 |
| BASE-003 | `test_get_llm_raises_without_api_key` | Raise ValueError if no API key | P0 |
| BASE-004 | `test_get_llm_uses_settings` | Verify settings are applied to LLM | P1 |
| BASE-005 | `test_get_llm_returns_chat_openai` | Verify return type | P1 |

```python
# tests/unit/agents/test_base.py

"""Tests for base agent factory."""

import pytest
from unittest.mock import patch, MagicMock

from think_only_once.agents.base import get_llm


class TestGetLLM:
    """Tests for get_llm factory function."""

    def test_get_llm_with_env_api_key(self, mock_env_api_key) -> None:
        """Test get_llm succeeds with API key from environment."""
        with patch("think_only_once.agents.base.ChatOpenAI") as mock_chat:
            mock_chat.return_value = MagicMock()
            llm = get_llm()
            assert llm is not None
            mock_chat.assert_called_once()

    def test_get_llm_raises_without_api_key(self, clean_env) -> None:
        """Test get_llm raises ValueError when no API key is available."""
        with pytest.raises(ValueError, match="API key required"):
            get_llm()

    def test_get_llm_uses_config_settings(self, mock_env_api_key) -> None:
        """Test get_llm applies settings from config."""
        with patch("think_only_once.agents.base.ChatOpenAI") as mock_chat:
            mock_chat.return_value = MagicMock()
            get_llm()

            call_kwargs = mock_chat.call_args.kwargs
            assert call_kwargs["model"] == "gpt-4o-mini"
            assert call_kwargs["temperature"] == 0.2
            assert call_kwargs["max_tokens"] == 1024

    def test_get_llm_prefers_config_api_key(self, mock_env_api_key) -> None:
        """Test that config API key takes precedence over env var."""
        with patch("think_only_once.agents.base.get_settings") as mock_settings:
            mock_settings.return_value.llm.api_key = "config-key"
            mock_settings.return_value.llm.model = "test-model"
            mock_settings.return_value.llm.temperature = 0.5
            mock_settings.return_value.llm.base_url = "https://test.com"
            mock_settings.return_value.llm.max_tokens = 512

            with patch("think_only_once.agents.base.ChatOpenAI") as mock_chat:
                mock_chat.return_value = MagicMock()
                get_llm()

                call_kwargs = mock_chat.call_args.kwargs
                assert call_kwargs["api_key"] == "config-key"
```

**File:** `tests/unit/agents/test_router.py` (for planned implementation)

| Test ID | Test Name | Description | Priority |
|---------|-----------|-------------|----------|
| RTR-001 | `test_router_decision_schema` | Validate RouterDecision Pydantic model | P1 |
| RTR-002 | `test_route_query_full_analysis` | Route "Analyze NVDA" to all agents | P1 |
| RTR-003 | `test_route_query_news_only` | Route "news on AAPL" to news agent | P1 |
| RTR-004 | `test_route_query_technical_only` | Route "TSLA technicals" to tech agent | P1 |
| RTR-005 | `test_route_query_fundamental_only` | Route "Is MSFT overvalued" to fund agent | P1 |
| RTR-006 | `test_route_query_extracts_ticker` | Extract ticker from various formats | P1 |
| RTR-007 | `test_route_query_company_name_to_ticker` | Convert "Apple" to "AAPL" | P2 |

```python
# tests/unit/agents/test_router.py

"""Tests for smart router agent."""

import pytest
from unittest.mock import patch, MagicMock

# Note: Import will work after router.py is implemented
# from think_only_once.agents.router import RouterDecision, route_query, create_router


class TestRouterDecision:
    """Tests for RouterDecision Pydantic model."""

    @pytest.mark.skip(reason="Router not yet implemented")
    def test_router_decision_schema(self) -> None:
        """Test RouterDecision has correct fields."""
        from think_only_once.agents.router import RouterDecision
        decision = RouterDecision(
            ticker="NVDA",
            run_technical=True,
            run_fundamental=False,
            run_news=True,
            reasoning="Test reasoning",
        )
        assert decision.ticker == "NVDA"
        assert decision.run_technical is True
        assert decision.run_fundamental is False

    @pytest.mark.skip(reason="Router not yet implemented")
    def test_router_decision_requires_ticker(self) -> None:
        """Test RouterDecision requires ticker field."""
        from think_only_once.agents.router import RouterDecision
        with pytest.raises(ValueError):
            RouterDecision(
                run_technical=True,
                run_fundamental=True,
                run_news=True,
                reasoning="Missing ticker",
            )


class TestRouteQuery:
    """Tests for route_query function."""

    @pytest.fixture
    def mock_router_llm(self, mock_router_decision):
        """Mock the router LLM to return predictable decisions."""
        with patch("think_only_once.agents.router.get_llm") as mock_get_llm:
            mock_llm = MagicMock()
            mock_llm.with_structured_output.return_value = MagicMock(
                invoke=MagicMock(return_value=mock_router_decision)
            )
            mock_get_llm.return_value = mock_llm
            yield mock_llm

    @pytest.mark.skip(reason="Router not yet implemented")
    def test_route_query_full_analysis(self, mock_router_llm) -> None:
        """Test routing 'Analyze NVDA' enables all agents."""
        from think_only_once.agents.router import route_query
        # Setup mock to return full analysis decision
        result = route_query("Analyze NVDA stock")
        assert result.run_technical is True
        assert result.run_fundamental is True
        assert result.run_news is True

    @pytest.mark.skip(reason="Router not yet implemented")
    def test_route_query_news_only(self) -> None:
        """Test routing news-specific query."""
        from think_only_once.agents.router import route_query
        # This would need proper mock setup
        pass

    @pytest.mark.skip(reason="Router not yet implemented")
    def test_route_query_technical_only(self) -> None:
        """Test routing technical-specific query."""
        from think_only_once.agents.router import route_query
        pass

    @pytest.mark.skip(reason="Router not yet implemented")
    def test_route_query_extracts_ticker(self) -> None:
        """Test ticker extraction from query."""
        from think_only_once.agents.router import route_query
        pass
```

**File:** `tests/unit/agents/test_investment_analyst.py`

| Test ID | Test Name | Description | Priority |
|---------|-----------|-------------|----------|
| INV-001 | `test_create_investment_analyst_chain` | Verify chain creation | P1 |
| INV-002 | `test_generate_investment_outlook_with_all_data` | Generate with all analyses | P1 |
| INV-003 | `test_generate_investment_outlook_with_partial_data` | Handle missing analyses | P1 |
| INV-004 | `test_generate_investment_outlook_handles_none` | Handle None values | P1 |
| INV-005 | `test_investment_prompt_contains_required_sections` | Verify prompt structure | P2 |

```python
# tests/unit/agents/test_investment_analyst.py

"""Tests for investment analyst agent."""

import pytest
from unittest.mock import patch, MagicMock

from think_only_once.agents.investment_analyst import (
    create_investment_analyst_chain,
    generate_investment_outlook,
    INVESTMENT_ANALYST_PROMPT,
)


class TestCreateInvestmentAnalystChain:
    """Tests for create_investment_analyst_chain function."""

    def test_create_investment_analyst_chain_returns_chain(
        self, mock_env_api_key, mock_chat_openai
    ) -> None:
        """Test that create_investment_analyst_chain returns a chain."""
        chain = create_investment_analyst_chain()
        assert chain is not None
        assert hasattr(chain, "invoke")


class TestGenerateInvestmentOutlook:
    """Tests for generate_investment_outlook function."""

    def test_generate_investment_outlook_with_all_data(
        self, mock_env_api_key, mock_chat_openai
    ) -> None:
        """Test outlook generation with all analysis data."""
        mock_chat_openai.invoke.return_value.content = "**Recommendation:** BUY"

        result = generate_investment_outlook(
            ticker="NVDA",
            technical_analysis="Bullish trend",
            fundamental_analysis="Strong financials",
            news_analysis="Positive sentiment",
        )
        assert isinstance(result, str)
        assert len(result) > 0

    def test_generate_investment_outlook_with_partial_data(
        self, mock_env_api_key, mock_chat_openai
    ) -> None:
        """Test outlook generation with partial analysis data."""
        mock_chat_openai.invoke.return_value.content = "**Recommendation:** HOLD"

        result = generate_investment_outlook(
            ticker="AAPL",
            technical_analysis="Price trending up",
            fundamental_analysis=None,
            news_analysis=None,
        )
        assert isinstance(result, str)

    def test_generate_investment_outlook_handles_all_none(
        self, mock_env_api_key, mock_chat_openai
    ) -> None:
        """Test outlook generation when all analyses are None."""
        mock_chat_openai.invoke.return_value.content = "Insufficient data"

        result = generate_investment_outlook(
            ticker="TSLA",
            technical_analysis=None,
            fundamental_analysis=None,
            news_analysis=None,
        )
        assert isinstance(result, str)


class TestInvestmentAnalystPrompt:
    """Tests for the investment analyst prompt."""

    def test_prompt_contains_recommendation_section(self) -> None:
        """Test prompt mentions RECOMMENDATION."""
        assert "RECOMMENDATION" in INVESTMENT_ANALYST_PROMPT

    def test_prompt_contains_price_target_section(self) -> None:
        """Test prompt mentions PRICE TARGET."""
        assert "PRICE TARGET" in INVESTMENT_ANALYST_PROMPT

    def test_prompt_contains_risk_assessment_section(self) -> None:
        """Test prompt mentions RISK ASSESSMENT."""
        assert "RISK ASSESSMENT" in INVESTMENT_ANALYST_PROMPT

    def test_prompt_contains_investment_thesis_section(self) -> None:
        """Test prompt mentions INVESTMENT THESIS."""
        assert "INVESTMENT THESIS" in INVESTMENT_ANALYST_PROMPT

    def test_prompt_has_placeholders(self) -> None:
        """Test prompt has required placeholders."""
        assert "{ticker}" in INVESTMENT_ANALYST_PROMPT
        assert "{technical_analysis}" in INVESTMENT_ANALYST_PROMPT
        assert "{fundamental_analysis}" in INVESTMENT_ANALYST_PROMPT
        assert "{news_analysis}" in INVESTMENT_ANALYST_PROMPT
```

### 4.4 Graph Module Tests

**File:** `tests/unit/graph/test_state.py`

| Test ID | Test Name | Description | Priority |
|---------|-----------|-------------|----------|
| ST-001 | `test_analysis_state_is_typed_dict` | Verify AnalysisState is TypedDict | P0 |
| ST-002 | `test_analysis_state_has_required_keys` | Check all required keys | P0 |
| ST-003 | `test_analysis_state_can_be_instantiated` | Create valid state instance | P0 |
| ST-004 | `test_analysis_state_messages_annotation` | Verify messages uses add_messages | P1 |

```python
# tests/unit/graph/test_state.py

"""Tests for LangGraph state definitions."""

import pytest
from typing import get_type_hints

from think_only_once.graph.state import AnalysisState


class TestAnalysisState:
    """Tests for AnalysisState TypedDict."""

    def test_analysis_state_is_typed_dict(self) -> None:
        """Test AnalysisState is a TypedDict."""
        assert hasattr(AnalysisState, "__annotations__")

    def test_analysis_state_has_required_keys(self) -> None:
        """Test AnalysisState has all required keys."""
        required_keys = [
            "ticker",
            "technical_analysis",
            "fundamental_analysis",
            "news_analysis",
            "ai_outlook",
            "final_report",
            "messages",
        ]
        annotations = AnalysisState.__annotations__
        for key in required_keys:
            assert key in annotations, f"Missing key: {key}"

    def test_analysis_state_can_be_instantiated(self) -> None:
        """Test AnalysisState can be created with valid data."""
        state: AnalysisState = {
            "ticker": "NVDA",
            "technical_analysis": None,
            "fundamental_analysis": None,
            "news_analysis": None,
            "ai_outlook": None,
            "final_report": None,
            "messages": [],
        }
        assert state["ticker"] == "NVDA"
        assert state["messages"] == []

    def test_analysis_state_accepts_analysis_data(self) -> None:
        """Test AnalysisState accepts populated analysis data."""
        state: AnalysisState = {
            "ticker": "AAPL",
            "technical_analysis": {"current_price": 175.50},
            "fundamental_analysis": {"pe_ratio": 28.5},
            "news_analysis": {"sentiment": "POSITIVE"},
            "ai_outlook": "BUY with target $200",
            "final_report": "# Analysis Report\n...",
            "messages": [],
        }
        assert state["technical_analysis"]["current_price"] == 175.50
        assert state["news_analysis"]["sentiment"] == "POSITIVE"
```

**File:** `tests/unit/graph/test_orchestrator.py` (for planned implementation)

| Test ID | Test Name | Description | Priority |
|---------|-----------|-------------|----------|
| ORCH-001 | `test_orchestrator_initialization` | Create orchestrator instance | P1 |
| ORCH-002 | `test_orchestrator_lazy_agent_init` | Verify lazy initialization | P1 |
| ORCH-003 | `test_router_node` | Test router_node method | P1 |
| ORCH-004 | `test_technical_analysis_node_enabled` | Run tech analysis when enabled | P1 |
| ORCH-005 | `test_technical_analysis_node_disabled` | Skip tech analysis when disabled | P1 |
| ORCH-006 | `test_aggregator_node` | Test report aggregation | P1 |
| ORCH-007 | `test_investment_analyst_node` | Test AI outlook generation | P1 |
| ORCH-008 | `test_build_graph` | Build and compile graph | P1 |
| ORCH-009 | `test_invoke_full_workflow` | Full workflow invocation | P2 |
| ORCH-010 | `test_get_orchestrator_singleton` | Verify singleton pattern | P2 |

```python
# tests/unit/graph/test_orchestrator.py

"""Tests for LangGraph orchestrator."""

import pytest
from unittest.mock import patch, MagicMock

# Note: Imports will work after orchestrator.py is implemented
# from think_only_once.graph.orchestrator import (
#     StockAnalyzerOrchestrator,
#     get_orchestrator,
# )


class TestStockAnalyzerOrchestrator:
    """Tests for StockAnalyzerOrchestrator class."""

    @pytest.mark.skip(reason="Orchestrator not yet implemented")
    def test_orchestrator_initialization(self) -> None:
        """Test orchestrator can be instantiated."""
        from think_only_once.graph.orchestrator import StockAnalyzerOrchestrator
        orchestrator = StockAnalyzerOrchestrator()
        assert orchestrator is not None
        assert orchestrator._technical_agent is None  # Lazy init
        assert orchestrator._graph is None

    @pytest.mark.skip(reason="Orchestrator not yet implemented")
    def test_orchestrator_lazy_agent_init(self, mock_env_api_key) -> None:
        """Test agents are lazily initialized."""
        from think_only_once.graph.orchestrator import StockAnalyzerOrchestrator
        orchestrator = StockAnalyzerOrchestrator()
        # Access property to trigger initialization
        with patch("think_only_once.agents.technical_analyst.create_technical_analyst"):
            _ = orchestrator.technical_agent
            assert orchestrator._technical_agent is not None

    @pytest.mark.skip(reason="Orchestrator not yet implemented")
    def test_router_node(self, sample_analysis_state) -> None:
        """Test router_node correctly routes queries."""
        from think_only_once.graph.orchestrator import StockAnalyzerOrchestrator
        orchestrator = StockAnalyzerOrchestrator()
        with patch("think_only_once.graph.orchestrator.route_query") as mock_route:
            mock_route.return_value.ticker = "NVDA"
            mock_route.return_value.run_technical = True
            mock_route.return_value.run_fundamental = True
            mock_route.return_value.run_news = False

            result = orchestrator.router_node(sample_analysis_state)
            assert result["ticker"] == "NVDA"
            assert result["run_technical"] is True
            assert result["run_news"] is False

    @pytest.mark.skip(reason="Orchestrator not yet implemented")
    def test_technical_analysis_node_enabled(self, sample_analysis_state) -> None:
        """Test technical analysis runs when enabled."""
        from think_only_once.graph.orchestrator import StockAnalyzerOrchestrator
        orchestrator = StockAnalyzerOrchestrator()
        sample_analysis_state["run_technical"] = True

        with patch.object(orchestrator, "technical_agent") as mock_agent:
            mock_agent.invoke.return_value = {"output": "Technical analysis results"}
            result = orchestrator.technical_analysis_node(sample_analysis_state)
            assert result["technical_analysis"] == "Technical analysis results"

    @pytest.mark.skip(reason="Orchestrator not yet implemented")
    def test_technical_analysis_node_disabled(self, sample_analysis_state) -> None:
        """Test technical analysis skipped when disabled."""
        from think_only_once.graph.orchestrator import StockAnalyzerOrchestrator
        orchestrator = StockAnalyzerOrchestrator()
        sample_analysis_state["run_technical"] = False

        result = orchestrator.technical_analysis_node(sample_analysis_state)
        assert result["technical_analysis"] is None

    @pytest.mark.skip(reason="Orchestrator not yet implemented")
    def test_build_graph_returns_compiled_graph(self, mock_env_api_key) -> None:
        """Test build method returns compiled graph."""
        from think_only_once.graph.orchestrator import StockAnalyzerOrchestrator
        orchestrator = StockAnalyzerOrchestrator()
        graph = orchestrator.build()
        assert graph is not None
        assert hasattr(graph, "invoke")


class TestGetOrchestrator:
    """Tests for get_orchestrator singleton function."""

    @pytest.mark.skip(reason="Orchestrator not yet implemented")
    def test_get_orchestrator_returns_instance(self) -> None:
        """Test get_orchestrator returns an orchestrator instance."""
        from think_only_once.graph.orchestrator import get_orchestrator
        orchestrator = get_orchestrator()
        assert orchestrator is not None

    @pytest.mark.skip(reason="Orchestrator not yet implemented")
    def test_get_orchestrator_singleton(self) -> None:
        """Test get_orchestrator returns same instance."""
        from think_only_once.graph.orchestrator import get_orchestrator
        orch1 = get_orchestrator()
        orch2 = get_orchestrator()
        assert orch1 is orch2
```

---

## 5. Integration Tests

**File:** `tests/integration/test_analysis_workflow.py`

| Test ID | Test Name | Description | Priority |
|---------|-----------|-------------|----------|
| INT-001 | `test_full_workflow_mocked_llm` | Complete workflow with mocked LLM | P2 |
| INT-002 | `test_router_to_single_agent` | Router selects single agent | P2 |
| INT-003 | `test_router_to_multiple_agents` | Router selects multiple agents | P2 |
| INT-004 | `test_aggregator_combines_results` | Aggregator merges all analyses | P2 |
| INT-005 | `test_final_report_generation` | Full report is generated | P2 |

```python
# tests/integration/test_analysis_workflow.py

"""Integration tests for the analysis workflow."""

import pytest
from unittest.mock import patch, MagicMock


class TestAnalysisWorkflow:
    """Integration tests for the full analysis workflow."""

    @pytest.mark.skip(reason="Orchestrator not yet implemented")
    @pytest.mark.integration
    def test_full_workflow_with_mocked_dependencies(
        self,
        mock_env_api_key,
        mock_chat_openai,
        patch_yfinance,
        patch_ddg_search,
    ) -> None:
        """Test complete workflow with all dependencies mocked."""
        from think_only_once.graph.orchestrator import get_orchestrator

        # Configure mock responses
        mock_chat_openai.invoke.return_value.content = "**Recommendation:** BUY"

        orchestrator = get_orchestrator()
        result = orchestrator.invoke("Analyze NVDA stock")

        assert result is not None
        assert "NVDA" in result
        assert "Analysis Report" in result or "Stock Analysis" in result

    @pytest.mark.skip(reason="Orchestrator not yet implemented")
    @pytest.mark.integration
    def test_workflow_respects_router_decisions(
        self,
        mock_env_api_key,
        mock_chat_openai,
        patch_yfinance,
    ) -> None:
        """Test that workflow only runs agents selected by router."""
        from think_only_once.graph.orchestrator import StockAnalyzerOrchestrator

        orchestrator = StockAnalyzerOrchestrator()

        # Mock router to only enable technical analysis
        with patch("think_only_once.graph.orchestrator.route_query") as mock_route:
            mock_route.return_value.ticker = "AAPL"
            mock_route.return_value.run_technical = True
            mock_route.return_value.run_fundamental = False
            mock_route.return_value.run_news = False

            # The workflow should only call technical agent
            # This would need more detailed mocking to verify
            pass
```

---

## 6. End-to-End Tests

**File:** `tests/e2e/test_full_analysis.py`

| Test ID | Test Name | Description | Priority |
|---------|-----------|-------------|----------|
| E2E-001 | `test_analyze_stock_real_api` | Real API call (requires key) | P3 |
| E2E-002 | `test_analyze_with_different_queries` | Various query types | P3 |
| E2E-003 | `test_error_handling_invalid_ticker` | Handle invalid ticker | P3 |

```python
# tests/e2e/test_full_analysis.py

"""End-to-end tests with real API calls."""

import os
import pytest


@pytest.mark.e2e
@pytest.mark.slow
@pytest.mark.skipif(
    not os.getenv("OPENAI_API_KEY"),
    reason="OPENAI_API_KEY not set - skipping E2E tests"
)
class TestFullAnalysisE2E:
    """End-to-end tests requiring real API keys."""

    @pytest.mark.skip(reason="Full implementation not yet complete")
    def test_analyze_stock_real_api(self) -> None:
        """Test real stock analysis with actual API calls."""
        from think_only_once.main import analyze_stock

        result = analyze_stock("Analyze NVDA")
        assert result is not None
        assert "NVDA" in result
        assert len(result) > 100  # Should have substantial content

    @pytest.mark.skip(reason="Full implementation not yet complete")
    def test_news_only_query(self) -> None:
        """Test news-only query with real API."""
        from think_only_once.main import analyze_stock

        result = analyze_stock("What's the news on AAPL?")
        assert result is not None
        assert "News" in result or "news" in result

    @pytest.mark.skip(reason="Full implementation not yet complete")
    def test_invalid_ticker_handling(self) -> None:
        """Test handling of invalid ticker symbol."""
        from think_only_once.main import analyze_stock

        # Should handle gracefully, not crash
        result = analyze_stock("Analyze INVALIDTICKER123")
        assert result is not None  # Should return something, even if error message
```

---

## 7. Test Markers and Categories

### 7.1 Custom Markers

Add to `pyproject.toml`:

```toml
[tool.pytest.ini_options]
markers = [
    "unit: Unit tests (fast, isolated)",
    "integration: Integration tests (may be slower)",
    "e2e: End-to-end tests (requires API keys)",
    "slow: Slow tests (network calls, etc.)",
]
```

### 7.2 Running Tests by Category

```bash
# Run all unit tests
pytest tests/unit/ -v

# Run only config tests
pytest tests/unit/config/ -v

# Run integration tests
pytest -m integration -v

# Run everything except E2E
pytest -m "not e2e" -v

# Run with coverage
pytest --cov=think_only_once --cov-report=html tests/

# Run fast tests only
pytest -m "not slow" -v
```

---

## 8. Coverage Requirements

### 8.1 Target Coverage

| Module | Target Coverage |
|--------|-----------------|
| `config/settings.py` | 90%+ |
| `agents/base.py` | 90%+ |
| `agents/investment_analyst.py` | 85%+ |
| `tools/yfinance_tools.py` | 80%+ |
| `tools/search_tools.py` | 80%+ |
| `graph/state.py` | 95%+ |
| `graph/orchestrator.py` | 80%+ |
| **Overall** | **85%+** |

### 8.2 Coverage Commands

```bash
# Generate coverage report
pytest --cov=think_only_once --cov-report=term-missing tests/

# Generate HTML report
pytest --cov=think_only_once --cov-report=html tests/

# Fail if coverage drops below threshold
pytest --cov=think_only_once --cov-fail-under=80 tests/
```

---

## Appendix: Implementation Checklist

### Tests to Implement (Priority Order)

- [x] `test_config.py` - Basic config tests (already exists)
- [ ] `tests/conftest.py` - Shared fixtures
- [ ] `tests/unit/config/test_settings.py` - Extended config tests
- [ ] `tests/unit/tools/test_yfinance_tools.py`
- [ ] `tests/unit/tools/test_search_tools.py`
- [ ] `tests/unit/agents/test_base.py`
- [ ] `tests/unit/agents/test_investment_analyst.py`
- [ ] `tests/unit/graph/test_state.py`
- [ ] `tests/unit/agents/test_router.py` (after router.py implemented)
- [ ] `tests/unit/graph/test_orchestrator.py` (after orchestrator.py implemented)
- [ ] `tests/integration/test_analysis_workflow.py`
- [ ] `tests/e2e/test_full_analysis.py`

---

*Test Plan Version: 1.0*  
*Created: January 2026*  
*Author: ThinkOnlyOnce Team*
