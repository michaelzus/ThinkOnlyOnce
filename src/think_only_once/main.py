"""Entry point for ThinkOnlyOnce demo application."""

import sys

from think_only_once.graph.orchestrator import get_orchestrator
from think_only_once.output import save_html_report


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
    query = sys.argv[1] if len(sys.argv) > 1 else "Analyze NVDA stock"

    print(f"Analyzing: {query}")
    print("Running multi-agent analysis...")

    report = analyze_stock(query)
    output_path = save_html_report(report)

    print(f"Report saved to: {output_path}")


if __name__ == "__main__":
    main()
