# Demo Guide

## Presentation to Colleagues

**Purpose:** Educational demonstration of agentic coding concepts  
**Target Audience:** Colleagues unfamiliar with LangChain/LangGraph  
**Demo Duration:** 10-13 minutes

---

## Demo Agenda

| Segment | Duration | Content |
|---------|----------|---------|
| LangChain Introduction | 2-3 min | What are agents, tools, chains |
| LangGraph Introduction | 2-3 min | State machines, nodes, edges, orchestration |
| Live Implementation | 5-7 min | Build the 3-agent stock analyzer |
| **Total** | **10-13 min** | |

---

## Presentation Talking Points

### Part 1: LangChain Introduction (2-3 min)

1. **What is LangChain?**
   - Framework for building LLM-powered applications
   - Provides abstractions for common patterns

2. **Core Concepts:**
   - **LLM**: The brain (GPT-4, Claude, etc.)
   - **Tools**: Functions the LLM can call (APIs, databases, search)
   - **Agents**: LLM + Tools + Reasoning loop
   - **Chains**: Sequential pipelines of operations

3. **Visual Example:**

   ```mermaid
   flowchart LR
       A[User Query] --> B[Agent]
       B --> C[Thinks]
       C --> D[Calls Tool]
       D --> E[Gets Data]
       E --> F[Responds]
   ```

### Part 2: LangGraph Introduction (2-3 min)

1. **What is LangGraph?**
   - Orchestration framework built on LangChain
   - Enables multi-agent workflows as graphs

2. **Core Concepts:**
   - **State**: Shared data container passed between nodes
   - **Nodes**: Processing units (agents, functions)
   - **Edges**: Connections defining flow
   - **Router/Supervisor**: Special node that decides which agents to invoke
   - **Graph**: The complete workflow

3. **Why LangGraph?**
   - Complex workflows with branching/loops
   - Multiple agents working together
   - **Smart routing** - only invoke agents when needed
   - Stateful, observable, debuggable

4. **Supervisor Pattern (what we'll build):**

   ```mermaid
   flowchart LR
       A[Query] --> B[Router - LLM]
       B --> C[Decides agents]
       C --> D[Run selected]
       D --> E[Aggregate]
   ```

### Part 3: Live Implementation (5-7 min)

1. **Show the architecture diagram** (30 sec)
   - Highlight the Smart Router at the top
   - Explain conditional routing to agents

2. **Walk through code:**
   - Define tools (1 min)
   - Create specialist agents (1 min)
   - Create smart router with structured output (1 min)
   - Build graph with routing (1.5 min)
   - Run demo with different queries (1.5 min)

3. **Execute demos showing routing:**
   ```bash
   thinkonlyonce "Analyze NVDA"           # → All 3 agents
   thinkonlyonce "What's the news on AAPL?"  # → News agent only
   thinkonlyonce "Is TSLA overvalued?"    # → Fundamental only
   ```

4. **Show output:** Compare reports - notice which sections appear based on query

---

## Demo Commands

### Setup (Before Presentation)

```bash
# Install dependencies
make install

# Activate virtual environment
source venv/bin/activate

# Set API key
export OPENAI_API_KEY=your-openai-api-key

# Verify setup
make help             # Show all available commands
make check            # Run linting and type checks
```

### During Presentation

```bash
# Full analysis (all agents invoked)
thinkonlyonce "Analyze NVDA stock"

# News only (router skips technical/fundamental)
thinkonlyonce "What's the latest news on AAPL?"

# Technical only
thinkonlyonce "Check TSLA price and trends"

# Fundamental only
thinkonlyonce "Is MSFT overvalued?"

# Combined (technical + news)
thinkonlyonce "GOOGL price action and recent headlines"
```

---

## Key Takeaways for Audience

Ensure attendees leave understanding:

1. **Agents** = LLM + Tools + Reasoning loop
2. **Tools** = Functions the LLM can call to interact with external systems
3. **LangGraph** = Orchestration layer that coordinates multiple agents
4. **State** = Shared context that flows between agents

---

## Q&A Preparation: Extensibility Ideas

If audience asks "what's next?", mention:

1. **Add more agents:**
   - Risk Assessment Agent
   - Portfolio Optimization Agent
   - Earnings Calendar Agent
   - Competitor Analysis Agent

2. **Enhanced routing:**
   - Multi-turn conversations (router tracks context)
   - Confidence scores in routing decisions
   - Fallback to full analysis if uncertain

3. **Parallel execution:**
   - Run selected agents concurrently
   - Use `asyncio` for better performance
   - Reduce latency from ~30s to ~10s

4. **Human-in-the-loop:**
   - Router asks clarifying questions
   - User confirms before expensive analyses
   - Feedback loop for router improvement

5. **Persistence:**
   - Save analysis history
   - Cache frequent queries
   - Track routing accuracy

---

## Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| `OPENAI_API_KEY not set` | Export the key: `export OPENAI_API_KEY=your-openai-api-key` |
| `401 Unauthorized` | Verify OPENAI_API_KEY is valid |
| `yfinance rate limited` | Add delays between calls or use caching |
| `DuckDuckGo no results` | Check ticker is valid, try different query |
| `Agent verbose output` | Set `verbose: false` in config.yaml |
| `Model not found` | Verify model name in config.yaml (default: `gpt-4o-mini`) |

---

*Demo Guide Version: 1.0*
