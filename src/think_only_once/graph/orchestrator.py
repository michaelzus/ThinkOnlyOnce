"""LangGraph orchestrator for the multi-agent stock analysis workflow."""

from typing import Any

from langgraph.graph import END, START, StateGraph

from think_only_once.agents.fundamental_analyst import create_fundamental_analyst
from think_only_once.agents.investment_analyst import generate_investment_outlook
from think_only_once.agents.news_analyst import create_news_analyst
from think_only_once.agents.router import RouterDecision, route_query
from think_only_once.agents.technical_analyst import create_technical_analyst
from think_only_once.graph.state import AnalysisState


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
        self._graph: Any | None = None

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

    def router_node(self, state: AnalysisState) -> dict:
        """Smart router: analyze query and decide which agents to invoke.

        Args:
            state: Current analysis state containing the user query.

        Returns:
            Dictionary with routing decisions (ticker and analysis flags).
        """
        decision = route_query(state["query"])
        print_router_decision(decision)
        return {
            "ticker": decision.ticker,
            "run_technical": decision.run_technical,
            "run_fundamental": decision.run_fundamental,
            "run_news": decision.run_news,
        }

    def technical_analysis_node(self, state: AnalysisState) -> dict:
        """Run technical analysis if requested by router.

        Args:
            state: Current analysis state.

        Returns:
            Dictionary with technical_analysis result or None.
        """
        if not state.get("run_technical"):
            return {"technical_analysis": None}

        result = self.technical_agent.invoke({
            "messages": [{"role": "user", "content": f"Analyze {state['ticker']}"}]
        })
        content = result["messages"][-1].content
        return {"technical_analysis": content}

    def fundamental_analysis_node(self, state: AnalysisState) -> dict:
        """Run fundamental analysis if requested by router.

        Args:
            state: Current analysis state.

        Returns:
            Dictionary with fundamental_analysis result or None.
        """
        if not state.get("run_fundamental"):
            return {"fundamental_analysis": None}

        result = self.fundamental_agent.invoke({
            "messages": [{"role": "user", "content": f"Analyze {state['ticker']}"}]
        })
        content = result["messages"][-1].content
        return {"fundamental_analysis": content}

    def news_analysis_node(self, state: AnalysisState) -> dict:
        """Run news analysis if requested by router.

        Args:
            state: Current analysis state.

        Returns:
            Dictionary with news_analysis result or None.
        """
        if not state.get("run_news"):
            return {"news_analysis": None}

        result = self.news_agent.invoke({
            "messages": [{"role": "user", "content": f"Analyze news for {state['ticker']}"}]
        })
        content = result["messages"][-1].content
        return {"news_analysis": content}

    def aggregator_node(self, state: AnalysisState) -> dict:
        """Aggregate all analyses into sections for the report.

        Args:
            state: Current analysis state with completed analyses.

        Returns:
            Dictionary with aggregated_sections list.
        """
        sections: list[str] = []

        if state.get("technical_analysis"):
            sections.append(f"## Technical Analysis\n{state['technical_analysis']}")

        if state.get("fundamental_analysis"):
            sections.append(f"## Fundamental Analysis\n{state['fundamental_analysis']}")

        if state.get("news_analysis"):
            sections.append(f"## News & Sentiment Analysis\n{state['news_analysis']}")

        return {"aggregated_sections": sections}

    def investment_analyst_node(self, state: AnalysisState) -> dict:
        """Generate AI investment outlook and compile final report.

        Args:
            state: Current analysis state with all completed analyses.

        Returns:
            Dictionary with ai_outlook and final_report.
        """
        ai_outlook = generate_investment_outlook(
            ticker=state["ticker"],
            technical_analysis=state.get("technical_analysis"),
            fundamental_analysis=state.get("fundamental_analysis"),
            news_analysis=state.get("news_analysis"),
        )

        sections = state.get("aggregated_sections", [])
        sections.append(f"## AI Investment Outlook\n{ai_outlook}")

        report = f"""# Stock Analysis Report: {state["ticker"]}

{chr(10).join(sections)}

---
*Generated by Multi-Agent Stock Analyzer*
"""
        return {"ai_outlook": ai_outlook, "final_report": report}

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

        workflow.add_node("router", self.router_node)
        workflow.add_node("technical_analyst", self.technical_analysis_node)
        workflow.add_node("fundamental_analyst", self.fundamental_analysis_node)
        workflow.add_node("news_analyst", self.news_analysis_node)
        workflow.add_node("aggregator", self.aggregator_node)
        workflow.add_node("investment_analyst", self.investment_analyst_node)

        # Sequential: START → router
        workflow.add_edge(START, "router")

        # Fan-out: router → all analysts in parallel
        workflow.add_edge("router", "technical_analyst")
        workflow.add_edge("router", "fundamental_analyst")
        workflow.add_edge("router", "news_analyst")

        # Fan-in: all analysts → aggregator
        workflow.add_edge("technical_analyst", "aggregator")
        workflow.add_edge("fundamental_analyst", "aggregator")
        workflow.add_edge("news_analyst", "aggregator")

        # Sequential: aggregator → investment_analyst → END
        workflow.add_edge("aggregator", "investment_analyst")
        workflow.add_edge("investment_analyst", END)

        self._graph = workflow.compile()

        if verbose:
            print_graph_structure(self._graph)

        return self._graph

    def invoke(self, query: str) -> str:
        """Run the analysis workflow for a given query.

        Args:
            query: User's stock analysis query.

        Returns:
            Formatted stock analysis report.
        """
        graph = self.build()

        initial_state: AnalysisState = {
            "query": query,
            "ticker": "",
            "run_technical": False,
            "run_fundamental": False,
            "run_news": False,
            "technical_analysis": None,
            "fundamental_analysis": None,
            "news_analysis": None,
            "aggregated_sections": [],
            "ai_outlook": None,
            "final_report": None,
            "messages": [],
        }

        result = graph.invoke(initial_state)
        return result["final_report"]


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
