"""Entry point for ThinkOnlyOnce demo application."""

from think_only_once.graph.orchestrator import get_orchestrator


def analyze_stock(query: str) -> str:
    """Analyze a stock using the multi-agent system with smart routing.

    Args:
        query: Natural language query (e.g., "What's the news on NVDA?",
            "Full analysis of AAPL", "Is TSLA overvalued?")

    Returns:
        Analysis report (only includes requested analyses).
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
