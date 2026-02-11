"""Entry point for ThinkOnlyOnce demo application."""

import contextlib
import sys

from think_only_once.graph.orchestrator import AnalysisResult, get_orchestrator
from think_only_once.output import save_html_report
from think_only_once.tools.yfinance_tools import get_price_history


def analyze_stock(query: str, on_status=None) -> AnalysisResult:
    """Analyze a stock using the multi-agent system with smart routing.

    Args:
        query: Natural language query (e.g., "What's the news on NVDA?",
            "Full analysis of AAPL", "Is TSLA overvalued?")
        on_status: Optional callback fired as (agent_name, status).

    Returns:
        AnalysisResult with report, summary, and ticker.
    """
    orchestrator = get_orchestrator()
    return orchestrator.invoke(query, on_status=on_status)


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


def _parse_args(argv: list[str]) -> tuple[str, bool]:
    """Parse CLI arguments.

    Args:
        argv: Command-line arguments (sys.argv).

    Returns:
        Tuple of (query, quiet_mode).
    """
    quiet = "--quiet" in argv or "-q" in argv
    # Filter out flags to get the query
    positional = [a for a in argv[1:] if a not in ("--quiet", "-q")]
    query = positional[0] if positional else "Analyze NVDA stock"
    return query, quiet


def _run_quiet(query: str) -> None:
    """Run analysis with plain-text output (original behaviour).

    Args:
        query: User's analysis query.
    """
    print(f"Analyzing: {query}")
    print("Running multi-agent analysis...")

    result = analyze_stock(query)

    print("Fetching price history...")
    price_history = get_price_history(result.ticker, period="6mo")

    output_path = save_html_report(result.final_report, price_history=price_history)

    print_summary(result)
    print(f"Full report saved to: {output_path}")


@contextlib.contextmanager
def _suppress_stdout():
    """Suppress stdout to silence prints from route_query before animation.

    Yields:
        None after redirecting stdout.
    """
    import io

    with contextlib.redirect_stdout(io.StringIO()):
        yield


def _run_animated(query: str) -> None:
    """Run analysis with Matrix rain + ticker tape animation (default).

    Args:
        query: User's analysis query.
    """
    from think_only_once.output.play_mode import PlayAnimation, fetch_tape_data_async

    # Start fetching ticker tape prices in background while we set up
    tape_getter, tape_thread = fetch_tape_data_async()

    # Run the router silently to get the ticker for ASCII art display
    from think_only_once.agents.router import route_query

    with _suppress_stdout():
        decision = route_query(query)
    ticker = decision.ticker if decision.ticker.upper() != "UNKNOWN" else "????"

    # Wait for tape data (should be done by now)
    tape_thread.join(timeout=10)
    tape_data = tape_getter()

    # Build the animation controller
    anim = PlayAnimation(ticker=ticker, tape_data=tape_data)
    orchestrator = get_orchestrator()

    # Screen.wrapper runs in the MAIN thread (required by asciimatics for
    # signal handlers).  The analysis runs in a background thread inside
    # the render loop.
    result = anim.run(
        lambda: orchestrator.invoke(query, on_status=anim.update_status, quiet=True)
    )

    # If the terminal didn't support full-screen, fall back to quiet mode
    if anim.failed:
        print("(Terminal does not support animation, falling back to plain output)")
        _run_quiet(query)
        return

    # Generate report and open it in the default browser
    import webbrowser

    price_history = get_price_history(result.ticker, period="6mo")
    output_path = save_html_report(result.final_report, price_history=price_history)
    webbrowser.open(f"file://{output_path}")


def main() -> None:
    """Entry point for the CLI."""
    query, quiet = _parse_args(sys.argv)

    if quiet:
        _run_quiet(query)
    else:
        _run_animated(query)


if __name__ == "__main__":
    main()
