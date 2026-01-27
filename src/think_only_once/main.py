"""Entry point for ThinkOnlyOnce demo application."""

import sys

from think_only_once.graph.orchestrator import AnalysisResult, get_orchestrator
from think_only_once.output import save_html_report


def analyze_stock(query: str) -> AnalysisResult:
    """Analyze a stock using the multi-agent system with smart routing.

    Args:
        query: Natural language query (e.g., "What's the news on NVDA?",
            "Full analysis of AAPL", "Is TSLA overvalued?")

    Returns:
        AnalysisResult with report, summary, and ticker.
    """
    orchestrator = get_orchestrator()
    return orchestrator.invoke(query)


def print_summary(result: AnalysisResult) -> None:
    """Print the investment summary to stdout.

    Args:
        result: Analysis result containing the investment summary.
    """
    summary = result.summary
    print("\n" + "=" * 50)
    print(f"  {result.ticker} - INVESTMENT SUMMARY")
    print("=" * 50)
    print(f"  Recommendation: {summary.recommendation} ({summary.confidence} Confidence)")
    print(f"  Price Target:   {summary.price_target}")
    print("-" * 50)
    print(f"  Outlook: {summary.thesis}")
    print("=" * 50 + "\n")


def main() -> None:
    """Entry point for the CLI."""
    query = sys.argv[1] if len(sys.argv) > 1 else "Analyze NVDA stock"

    print(f"Analyzing: {query}")
    print("Running multi-agent analysis...")

    result = analyze_stock(query)
    output_path = save_html_report(result.final_report)

    print_summary(result)
    print(f"Full report saved to: {output_path}")


if __name__ == "__main__":
    main()
