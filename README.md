# ThinkOnlyOnce

**Stock Market Multi-Agent Analysis System**

A multi-agent AI system built with LangChain and LangGraph that analyzes US equity stocks by coordinating specialized agents for technical, fundamental, news, and macroeconomic analysis.

## The Story

This project started as a colleague's demonstration of agentic coding concepts using LangChain and LangGraph. What began as an educational example to showcase multi-agent architectures quickly caught my attention. I found the concept compelling and saw real potential in it.

I decided to invest more time into the project, refactoring and extending it beyond its original demo scope. What was once a simple presentation tool evolved into something I actually use for my own stock market research. Along the way, it also became a portfolio piece that demonstrates my understanding of modern AI agent patterns, clean architecture principles, and practical LLM integration.

## Purpose

Originally created to demonstrate **LangChain** and **LangGraph** capabilities, this project now serves dual purposes:

**As a Learning Resource:**
- Building multi-agent systems with LangGraph's state management
- Implementing intelligent routing patterns with LangChain
- Creating modular, extensible AI agent architectures
- Integrating real-world data sources (financial APIs, news) with LLM reasoning

**As a Practical Tool:**
- Personal stock analysis assistant for US equities
- Quick synthesis of technical, fundamental, and sentiment data
- Actionable investment outlook generation

## Features

- **Smart Routing**: LLM-based query router that determines which analysis agents to invoke
- **Multi-Agent Architecture**: Specialized agents for technical, fundamental, news, and macro analysis
- **AI Investment Outlook**: Synthesizes all analyses into actionable investment recommendations
- **Flexible Configuration**: YAML-based configuration for LLM settings

## Quick Start

```bash
# Install dependencies
make install

# Activate virtual environment
source venv/bin/activate

# Set your OpenAI API key
export OPENAI_API_KEY=your-openai-api-key

# Run analysis
thinkonlyonce "Analyze NVDA stock"
```

## Usage Examples

```bash
# Full analysis (all agents invoked)
thinkonlyonce "Analyze NVDA stock"

# News only
thinkonlyonce "What's the latest news on AAPL?"

# Technical only
thinkonlyonce "Check TSLA price and trends"

# Fundamental only
thinkonlyonce "Is MSFT overvalued?"

# Combined (technical + news)
thinkonlyonce "GOOGL price action and recent headlines"
```

## Architecture

```mermaid
flowchart LR
    A[User Query] --> B[Smart Router]
    B --> C["Technical, Fundamental,<br/>News, Macro Analysts"]
    C --> D[Investment Analyst]
    D --> E[Aggregator]
    E --> F[Report]
```

The system uses a supervisor pattern where an LLM-based router analyzes the user's query and determines which specialist agents to invoke, optimizing for efficiency and relevance.

## Agents

| Agent | Role | Data Source |
|-------|------|-------------|
| Smart Router | Query analysis & routing | LLM |
| Technical Analyst | Price & volume analysis | yfinance |
| Fundamental Analyst | Financial health analysis | yfinance |
| News Analyst | Market sentiment | DuckDuckGo |
| Macro Analyst | Market-wide risk context (SPY, VIX, Fear & Greed) | yfinance, CNN API, DuckDuckGo |
| Investment Analyst | AI outlook & recommendations | LLM |

## Documentation

- [Software Design Document](docs/SDD.md) - Architecture and design decisions
- [Demo Guide](docs/DEMO.md) - Presentation script for colleagues

## Development

```bash
# Install with dev dependencies
make install-dev

# Run linting and type checks
make check

# Run tests
make test

# Format code
make format
```

## Requirements

- Python 3.11+
- OpenAI API key (or any OpenAI-compatible endpoint)

## Configuration

The system is pre-configured to use OpenAI's API. You can customize the model or use alternative providers by editing `src/think_only_once/config/config.yaml`:

**Default (OpenAI):**
```yaml
llm:
  model: "gpt-4o-mini"
  base_url: null  # Uses default OpenAI endpoint
  # Set OPENAI_API_KEY environment variable
```

**For local models (Ollama, vLLM, etc.):**
```yaml
llm:
  model: "llama3.1"
  base_url: "http://localhost:11434/v1"
  api_key: "not-needed"
```

## License

MIT License - See [LICENSE](LICENSE) for details.

---

*Built with LangChain and LangGraph — started as a demo, grew into something more.*
