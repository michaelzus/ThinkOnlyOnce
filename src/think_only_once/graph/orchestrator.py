"""LangGraph orchestrator for the multi-agent stock analysis workflow."""

from dataclasses import dataclass
from typing import Any, Callable

from langchain_core.messages import HumanMessage
from langgraph.graph import END, START, StateGraph

from think_only_once.agents.fundamental_analyst import create_fundamental_analyst
from think_only_once.agents.investment_analyst import generate_investment_outlook
from think_only_once.agents.macro_analyst import create_macro_analyst
from think_only_once.agents.news_analyst import create_news_analyst
from think_only_once.agents.router import RouterDecision, route_query
from think_only_once.agents.technical_analyst import create_technical_analyst
from think_only_once.enums import AgentEnum, StatusEnum
from think_only_once.graph.state import AnalysisState
from think_only_once.models import InvestmentSummary, parse_investment_outlook

# Type alias for the status callback used by the orchestrator and animation layer.
StatusCallback = Callable[[AgentEnum, StatusEnum], None]


@dataclass
class AnalysisResult:
    """Result of the stock analysis workflow."""

    final_report: str
    summary: InvestmentSummary
    ticker: str


def print_graph_structure(graph: Any) -> None:
    """Print the LangGraph structure to stdout.

    Args:
        graph: Compiled LangGraph workflow.
    """
    print("\n" + "=" * 60)
    print("LANGGRAPH WORKFLOW STRUCTURE")
    print("=" * 60)
    try:
        mermaid_syntax = graph.get_graph().draw_ascii()
        print(mermaid_syntax)
    except Exception as e:
        print(f"Could not generate graph visualization: {e}")
    print("=" * 60 + "\n")


def print_router_decision(decision: RouterDecision) -> None:
    """Print the router decision to stdout.

    Args:
        decision: Router decision with ticker and analysis flags.
    """
    print("\n" + "-" * 60)
    print("ROUTER DECISION")
    print("-" * 60)
    print(f"Ticker: {decision.ticker}")
    print(f"Run Technical Analysis: {'Yes' if decision.run_technical else 'No'}")
    print(f"Run Fundamental Analysis: {'Yes' if decision.run_fundamental else 'No'}")
    print(f"Run News Analysis: {'Yes' if decision.run_news else 'No'}")
    print(f"Run Macro Analysis: {'Yes' if decision.run_macro else 'No'}")
    print(f"Reasoning: {decision.reasoning}")
    print("-" * 60 + "\n")


class StockAnalyzerOrchestrator:
    """Orchestrator for the multi-agent stock analysis workflow.

    This class encapsulates the LangGraph workflow, managing agent lifecycle
    and defining the graph structure for stock analysis.
    """

    def __init__(self) -> None:
        """Initialize the orchestrator with lazy agent initialization."""
        self._technical_agent = None
        self._fundamental_agent = None
        self._news_agent = None
        self._macro_agent = None
        self._graph: Any | None = None
        self._on_status: StatusCallback | None = None
        self._quiet = False

    @property
    def technical_agent(self):
        """Get or create the technical analyst agent.

        Returns:
            Compiled technical analyst agent.
        """
        if self._technical_agent is None:
            self._technical_agent = create_technical_analyst()
        return self._technical_agent

    @property
    def fundamental_agent(self):
        """Get or create the fundamental analyst agent.

        Returns:
            Compiled fundamental analyst agent.
        """
        if self._fundamental_agent is None:
            self._fundamental_agent = create_fundamental_analyst()
        return self._fundamental_agent

    @property
    def news_agent(self):
        """Get or create the news analyst agent.

        Returns:
            Compiled news analyst agent.
        """
        if self._news_agent is None:
            self._news_agent = create_news_analyst()
        return self._news_agent

    @property
    def macro_agent(self):
        """Get or create the macro analyst agent.

        Returns:
            Compiled macro analyst agent.
        """
        if self._macro_agent is None:
            self._macro_agent = create_macro_analyst()
        return self._macro_agent

    def _notify(self, agent: AgentEnum, status: StatusEnum) -> None:
        """Fire the status callback if one is registered.

        Args:
            agent: Agent identifier enum value.
            status: Status enum value.
        """
        if self._on_status is not None:
            try:
                self._on_status(agent, status)
            except Exception:
                pass  # Don't let callback errors crash the workflow

    def router_node(self, state: AnalysisState) -> dict:
        """Smart router: analyze query and decide which agents to invoke.

        Args:
            state: Current analysis state containing the user query.

        Returns:
            Dictionary with routing decisions (ticker and analysis flags).
        """
        self._notify(AgentEnum.ROUTER, StatusEnum.RUNNING)
        decision = route_query(state["query"])
        if not self._quiet:
            print_router_decision(decision)
        self._notify(AgentEnum.ROUTER, StatusEnum.DONE)
        return {
            "ticker": decision.ticker,
            "run_technical": decision.run_technical,
            "run_fundamental": decision.run_fundamental,
            "run_news": decision.run_news,
            "run_macro": decision.run_macro,
        }

    def technical_analysis_node(self, state: AnalysisState) -> dict:
        """Run technical analysis if requested by router.

        Args:
            state: Current analysis state.

        Returns:
            Dictionary with technical_analysis result or None.
        """
        self._notify(AgentEnum.TECHNICAL_ANALYST, StatusEnum.RUNNING)
        if not state.get("run_technical"):
            self._notify(AgentEnum.TECHNICAL_ANALYST, StatusEnum.SKIPPED)
            return {"technical_analysis": None}

        result = self.technical_agent.invoke({
            "messages": [HumanMessage(content=f"Analyze {state['ticker']}")]
        })
        content = result["messages"][-1].content
        self._notify(AgentEnum.TECHNICAL_ANALYST, StatusEnum.DONE)
        return {"technical_analysis": content}

    def fundamental_analysis_node(self, state: AnalysisState) -> dict:
        """Run fundamental analysis if requested by router.

        Args:
            state: Current analysis state.

        Returns:
            Dictionary with fundamental_analysis result or None.
        """
        self._notify(AgentEnum.FUNDAMENTAL_ANALYST, StatusEnum.RUNNING)
        if not state.get("run_fundamental"):
            self._notify(AgentEnum.FUNDAMENTAL_ANALYST, StatusEnum.SKIPPED)
            return {"fundamental_analysis": None}

        result = self.fundamental_agent.invoke({
            "messages": [HumanMessage(content=f"Analyze {state['ticker']}")]
        })
        content = result["messages"][-1].content
        self._notify(AgentEnum.FUNDAMENTAL_ANALYST, StatusEnum.DONE)
        return {"fundamental_analysis": content}

    def news_analysis_node(self, state: AnalysisState) -> dict:
        """Run news analysis if requested by router.

        Args:
            state: Current analysis state.

        Returns:
            Dictionary with news_analysis result or None.
        """
        self._notify(AgentEnum.NEWS_ANALYST, StatusEnum.RUNNING)
        if not state.get("run_news"):
            self._notify(AgentEnum.NEWS_ANALYST, StatusEnum.SKIPPED)
            return {"news_analysis": None}

        result = self.news_agent.invoke({
            "messages": [HumanMessage(content=f"Analyze news for {state['ticker']}")]
        })
        content = result["messages"][-1].content
        self._notify(AgentEnum.NEWS_ANALYST, StatusEnum.DONE)
        return {"news_analysis": content}

    def macro_analysis_node(self, state: AnalysisState) -> dict:
        """Run macro analysis if requested by router.

        Args:
            state: Current analysis state.

        Returns:
            Dictionary with macro_analysis prose.
        """
        self._notify(AgentEnum.MACRO_ANALYST, StatusEnum.RUNNING)
        if not state.get("run_macro"):
            self._notify(AgentEnum.MACRO_ANALYST, StatusEnum.SKIPPED)
            return {"macro_analysis": None}

        # Run macro agent for context (LLM-based analysis)
        # The agent has get_market_indices tool and will fetch sector ETF data automatically
        result = self.macro_agent.invoke({
            "messages": [HumanMessage(content=f"Assess macro conditions for {state['ticker']}")]
        })
        content = result["messages"][-1].content

        self._notify(AgentEnum.MACRO_ANALYST, StatusEnum.DONE)
        return {"macro_analysis": content}

    @staticmethod
    def _build_report(result: dict) -> str:
        """Compile final report from all analysis results.

        Args:
            result: Graph output containing analysis sections and ticker.

        Returns:
            Formatted markdown report string.
        """
        sections: list[str] = []

        if result.get("technical_analysis"):
            sections.append(f"## Technical Analysis\n{result['technical_analysis']}")

        if result.get("fundamental_analysis"):
            sections.append(f"## Fundamental Analysis\n{result['fundamental_analysis']}")

        if result.get("news_analysis"):
            sections.append(f"## News & Sentiment Analysis\n{result['news_analysis']}")

        if result.get("macro_analysis"):
            sections.append(f"## Macro Analysis\n{result['macro_analysis']}")

        if result.get("ai_outlook"):
            sections.append(f"## AI Investment Outlook\n{result['ai_outlook']}")

        return f"""# Stock Analysis Report: {result["ticker"]}

{chr(10).join(sections)}

---
*Generated by Multi-Agent Stock Analyzer*
"""

    def investment_analyst_node(self, state: AnalysisState) -> dict:
        """Generate AI investment outlook.

        Args:
            state: Current analysis state with all completed analyses.

        Returns:
            Dictionary with ai_outlook.
        """
        self._notify(AgentEnum.INVESTMENT_ANALYST, StatusEnum.RUNNING)
        ticker = (state.get("ticker") or "").strip()
        if not ticker or ticker.upper() == "UNKNOWN":
            ai_outlook = (
                "**Recommendation:** N/A (Low Confidence)\n\n"
                "**Price Target:** N/A (N/A from current)\n"
                "- Ticker was not provided or could not be identified. Please specify a stock ticker (e.g., NVDA, AAPL).\n\n"
                "**Risk Assessment:** HIGH\n"
                "- Key Risks:\n"
                "  1. Unknown ticker / ambiguous query\n"
                "  2. Missing inputs for analysis\n"
                "  3. Potentially incorrect assumptions if we proceed\n\n"
                "**Investment Thesis:**\n"
                "Provide a ticker and (optionally) what you care about (valuation, trend, news, macro) to generate an actionable outlook.\n"
            )
            self._notify(AgentEnum.INVESTMENT_ANALYST, StatusEnum.DONE)
            return {"ai_outlook": ai_outlook}

        ai_outlook = generate_investment_outlook(
            ticker=state["ticker"],
            technical_analysis=state.get("technical_analysis"),
            fundamental_analysis=state.get("fundamental_analysis"),
            news_analysis=state.get("news_analysis"),
            macro_analysis=state.get("macro_analysis"),
        )
        self._notify(AgentEnum.INVESTMENT_ANALYST, StatusEnum.DONE)
        return {"ai_outlook": ai_outlook}

    def build(self, verbose: bool = True) -> Any:
        """Build and compile the LangGraph workflow.

        Args:
            verbose: If True, prints the graph structure to stdout.

        Returns:
            Compiled LangGraph workflow ready for invocation.
        """
        if self._graph is not None:
            return self._graph

        workflow = StateGraph(AnalysisState)

        workflow.add_node(AgentEnum.ROUTER, self.router_node)
        workflow.add_node(AgentEnum.TECHNICAL_ANALYST, self.technical_analysis_node)
        workflow.add_node(AgentEnum.FUNDAMENTAL_ANALYST, self.fundamental_analysis_node)
        workflow.add_node(AgentEnum.NEWS_ANALYST, self.news_analysis_node)
        workflow.add_node(AgentEnum.MACRO_ANALYST, self.macro_analysis_node)
        workflow.add_node(AgentEnum.INVESTMENT_ANALYST, self.investment_analyst_node)

        # Sequential: START → router
        workflow.add_edge(START, AgentEnum.ROUTER)

        # Fan-out: router → all analysts in parallel
        workflow.add_edge(AgentEnum.ROUTER, AgentEnum.TECHNICAL_ANALYST)
        workflow.add_edge(AgentEnum.ROUTER, AgentEnum.FUNDAMENTAL_ANALYST)
        workflow.add_edge(AgentEnum.ROUTER, AgentEnum.NEWS_ANALYST)
        workflow.add_edge(AgentEnum.ROUTER, AgentEnum.MACRO_ANALYST)

        # Fan-in: all analysts → investment_analyst
        workflow.add_edge(AgentEnum.TECHNICAL_ANALYST, AgentEnum.INVESTMENT_ANALYST)
        workflow.add_edge(AgentEnum.FUNDAMENTAL_ANALYST, AgentEnum.INVESTMENT_ANALYST)
        workflow.add_edge(AgentEnum.NEWS_ANALYST, AgentEnum.INVESTMENT_ANALYST)
        workflow.add_edge(AgentEnum.MACRO_ANALYST, AgentEnum.INVESTMENT_ANALYST)

        # Sequential: investment_analyst → END
        workflow.add_edge(AgentEnum.INVESTMENT_ANALYST, END)

        self._graph = workflow.compile()

        if verbose:
            print_graph_structure(self._graph)

        return self._graph

    def invoke(
        self,
        query: str,
        on_status: StatusCallback | None = None,
        quiet: bool = False,
    ) -> AnalysisResult:
        """Run the analysis workflow for a given query.

        Args:
            query: User's stock analysis query.
            on_status: Optional callback fired as (agent_name, status) when
                each node starts ('running') and finishes ('done').
            quiet: If True, suppress all print output during execution.

        Returns:
            AnalysisResult with report, summary, and ticker.
        """
        self._on_status = on_status
        self._quiet = quiet
        graph = self.build(verbose=not quiet)

        initial_state: AnalysisState = {
            "query": query,
            "ticker": "",
            "run_technical": False,
            "run_fundamental": False,
            "run_news": False,
            "run_macro": False,
            "technical_analysis": None,
            "fundamental_analysis": None,
            "news_analysis": None,
            "macro_analysis": None,
            "ai_outlook": None,
            "messages": [],
        }

        result = graph.invoke(initial_state)
        self._on_status = None
        self._quiet = False

        summary = parse_investment_outlook(result["ai_outlook"] or "")
        final_report = self._build_report(result)

        return AnalysisResult(
            final_report=final_report,
            summary=summary,
            ticker=result["ticker"],
        )


_orchestrator: StockAnalyzerOrchestrator | None = None


def get_orchestrator() -> StockAnalyzerOrchestrator:
    """Get or create the singleton orchestrator instance.

    Returns:
        Singleton StockAnalyzerOrchestrator instance.
    """
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = StockAnalyzerOrchestrator()
    return _orchestrator
