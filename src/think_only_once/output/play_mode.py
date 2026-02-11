"""Matrix rain + ticker tape console animation for stock analysis.

Provides a full-screen terminal animation that runs while the multi-agent
analysis is in progress, combining a Matrix-style rain background with a
scrolling stock ticker tape and live agent status panel.
"""

import random
import threading
import time
from typing import Any, Callable, TypeVar

import pyfiglet
import yfinance as yf
from asciimatics.screen import Screen

from think_only_once.enums import AgentEnum, StatusEnum

# Popular tickers to display in the scrolling tape
_TAPE_TICKERS = ["AAPL", "NVDA", "TSLA", "GOOGL", "MSFT", "AMZN", "META"]

# Agent display names (order matches the graph execution flow)
_AGENT_LABELS: list[tuple[AgentEnum, str]] = [
    (AgentEnum.ROUTER, "Router"),
    (AgentEnum.TECHNICAL_ANALYST, "Technical"),
    (AgentEnum.FUNDAMENTAL_ANALYST, "Fundamental"),
    (AgentEnum.NEWS_ANALYST, "News"),
    (AgentEnum.MACRO_ANALYST, "Macro"),
    (AgentEnum.INVESTMENT_ANALYST, "Investment"),
]


def _fetch_tape_data() -> list[dict]:
    """Fetch current prices for popular tickers.

    Returns:
        List of dicts with ticker, price, and change_pct.
    """
    tape: list[dict] = []
    for symbol in _TAPE_TICKERS:
        try:
            tk = yf.Ticker(symbol)
            info = tk.fast_info
            price = getattr(info, "last_price", None) or 0.0
            prev = getattr(info, "previous_close", None) or price
            change_pct = ((price - prev) / prev * 100) if prev else 0.0
            tape.append({"ticker": symbol, "price": price, "change_pct": change_pct})
        except Exception:
            tape.append({"ticker": symbol, "price": 0.0, "change_pct": 0.0})
    return tape


def _build_tape_string(tape_data: list[dict]) -> str:
    """Build the scrolling ticker tape text.

    Args:
        tape_data: List of ticker price dicts.

    Returns:
        Formatted ticker tape string.
    """
    parts: list[str] = []
    for item in tape_data:
        sign = "+" if item["change_pct"] >= 0 else ""
        parts.append(f"  {item['ticker']} ${item['price']:.2f} ({sign}{item['change_pct']:.1f}%)  ")
    return " | ".join(parts) if parts else "  Loading market data...  "


# ---------------------------------------------------------------------------
# Matrix rain state -- simple column-based falling characters
# ---------------------------------------------------------------------------

_MATRIX_CHARS = "abcdefghijklmnopqrstuvwxyz0123456789@#$%&*"


class _MatrixColumn:
    """State for one column of the Matrix rain."""

    def __init__(self, height: int) -> None:
        self.height = height
        self.pos = random.randint(-height, 0)
        self.speed = random.randint(1, 3)
        self.length = random.randint(4, height // 2)

    def advance(self) -> None:
        """Move the rain drop down one step."""
        self.pos += self.speed
        if self.pos - self.length > self.height:
            self.pos = random.randint(-self.height // 2, 0)
            self.speed = random.randint(1, 3)
            self.length = random.randint(4, self.height // 2)


# ---------------------------------------------------------------------------
# Drawing helpers -- called directly in our render loop
# ---------------------------------------------------------------------------


def _draw_matrix(screen: Screen, columns: list[_MatrixColumn]) -> None:
    """Draw one frame of Matrix rain.

    Args:
        screen: Asciimatics screen.
        columns: Per-column rain state.
    """
    width = screen.width
    height = screen.height
    for x in range(min(width, len(columns))):
        col = columns[x]
        for dy in range(col.length):
            y = col.pos - dy
            if 2 <= y < height:
                ch = random.choice(_MATRIX_CHARS)
                brightness = Screen.COLOUR_GREEN if dy > 0 else Screen.COLOUR_WHITE
                attr = Screen.A_BOLD if dy == 0 else Screen.A_NORMAL
                try:
                    screen.print_at(ch, x, y, colour=brightness, attr=attr)
                except Exception:
                    pass
        col.advance()


def _draw_ticker_tape(screen: Screen, tape: str, offset: int) -> None:
    """Draw the scrolling ticker tape on row 0.

    Args:
        screen: Asciimatics screen.
        tape: Double-length tape string for seamless wrapping.
        offset: Current scroll offset.
    """
    width = screen.width
    half = len(tape) // 2
    for i in range(width):
        idx = (offset + i) % half
        ch = tape[idx] if idx < len(tape) else " "
        try:
            screen.print_at(ch, i, 0, colour=Screen.COLOUR_CYAN, attr=Screen.A_BOLD)
        except Exception:
            pass
    # Separator line
    try:
        screen.print_at("\u2500" * width, 0, 1, colour=Screen.COLOUR_GREEN)
    except Exception:
        pass


def _compute_panel_geometry(
    screen_width: int,
    screen_height: int,
    figlet_lines: list[str],
    status_box_w: int = 38,
) -> tuple[int, int, int, int, int, int]:
    """Compute the bounding rectangle for the figlet + status box panel.

    Args:
        screen_width: Terminal width.
        screen_height: Terminal height.
        figlet_lines: Stripped figlet text lines.
        status_box_w: Width of the status box.

    Returns:
        (panel_x, panel_y, panel_w, panel_h, figlet_start_y, figlet_base_x)
    """
    max_figlet_w = max((len(ln.rstrip()) for ln in figlet_lines), default=0)
    if max_figlet_w >= screen_width:
        max_figlet_w = screen_width - 1
    panel_content_w = max(max_figlet_w, status_box_w)
    panel_w = panel_content_w + 4  # 2-char padding on each side

    figlet_start_y = max(3, screen_height // 4 - len(figlet_lines) // 2)
    # figlet lines + 2 gap + 1 top border + agents + 1 bottom border + 2 gap + status msg + 1 pad
    panel_h = len(figlet_lines) + 2 + 1 + len(_AGENT_LABELS) + 1 + 2 + 1 + 1

    panel_x = max(0, (screen_width - panel_w) // 2)
    panel_y = figlet_start_y - 1  # 1 row above figlet for top border

    figlet_base_x = max(0, (screen_width - max_figlet_w) // 2)

    return panel_x, panel_y, panel_w, panel_h, figlet_start_y, figlet_base_x


def _draw_panel_bg(screen: Screen, px: int, py: int, pw: int, ph: int) -> None:
    """Draw a dark background panel with a subtle border for the HUD overlay.

    Clears a rectangular region and draws a thin border, giving the
    figlet + status box a readable dark backdrop while rain fills the rest.

    Args:
        screen: Asciimatics screen.
        px: Panel top-left x.
        py: Panel top-left y.
        pw: Panel width.
        ph: Panel height.
    """
    width = screen.width
    height = screen.height
    # Clamp to screen
    x1 = max(0, px)
    y1 = max(2, py)
    x2 = min(width - 1, px + pw - 1)
    y2 = min(height - 1, py + ph - 1)

    # Fill interior with spaces (black background)
    blank = " " * (x2 - x1 + 1)
    for y in range(y1, y2 + 1):
        try:
            screen.print_at(blank, x1, y, colour=Screen.COLOUR_BLACK)
        except Exception:
            pass

    # Draw subtle border
    h_bar = "\u2500" * (x2 - x1 - 1)
    try:
        screen.print_at("\u250c" + h_bar + "\u2510", x1, y1, colour=Screen.COLOUR_GREEN, attr=Screen.A_NORMAL)
        screen.print_at("\u2514" + h_bar + "\u2518", x1, y2, colour=Screen.COLOUR_GREEN, attr=Screen.A_NORMAL)
    except Exception:
        pass
    for y in range(y1 + 1, y2):
        try:
            screen.print_at("\u2502", x1, y, colour=Screen.COLOUR_GREEN, attr=Screen.A_NORMAL)
            screen.print_at("\u2502", x2, y, colour=Screen.COLOUR_GREEN, attr=Screen.A_NORMAL)
        except Exception:
            pass


def _draw_figlet(screen: Screen, lines: list[str], base_x: int, start_y: int) -> int:
    """Draw pyfiglet ASCII art at specified position.

    Args:
        screen: Asciimatics screen.
        lines: Figlet text split into lines.
        base_x: Left x coordinate for drawing.
        start_y: Top y coordinate for drawing.

    Returns:
        Y position after the last figlet line.
    """
    width = screen.width
    height = screen.height

    for i, line in enumerate(lines):
        y = start_y + i
        if 2 <= y < height - 1:
            stripped = line.rstrip()
            if len(stripped) >= width:
                stripped = stripped[: width - 1]
            try:
                screen.print_at(stripped, base_x, y, colour=Screen.COLOUR_CYAN, attr=Screen.A_BOLD)
            except Exception:
                pass
    return start_y + len(lines)


def _draw_status_box(
    screen: Screen,
    top_y: int,
    status_dict: dict[AgentEnum, StatusEnum],
    spinner_char: str,
    is_complete: bool,
) -> None:
    """Draw the agent status box.

    Args:
        screen: Asciimatics screen.
        top_y: Y position for the top of the box.
        status_dict: Agent enum -> status enum mapping.
        spinner_char: Current spinner frame character.
        is_complete: Whether analysis is complete.
    """
    width = screen.width
    height = screen.height
    box_w = 38
    box_x = max(0, (width - box_w) // 2)
    box_y = top_y + 2

    # Top border
    title = " Agent Status "
    left_pad = (box_w - 2 - len(title)) // 2
    border_top = "\u250c" + "\u2500" * left_pad + title
    border_top += "\u2500" * (box_w - 1 - len(border_top)) + "\u2510"
    if box_y < height - 1:
        try:
            screen.print_at(border_top, box_x, box_y, colour=Screen.COLOUR_GREEN)
        except Exception:
            pass

    # Agent rows
    _LABEL_PAD = 14  # fixed column width for agent names
    for idx, (key, label) in enumerate(_AGENT_LABELS):
        row_y = box_y + 1 + idx
        if row_y >= height - 1:
            break
        status = status_dict.get(key, StatusEnum.WAIT)
        if status == StatusEnum.RUNNING:
            status_text = f" {spinner_char} RUNNING"
            colour = Screen.COLOUR_YELLOW
        elif status == StatusEnum.DONE:
            status_text = " \u2713 DONE   "
            colour = Screen.COLOUR_GREEN
        elif status == StatusEnum.SKIPPED:
            status_text = " \u2013 SKIP   "
            colour = Screen.COLOUR_MAGENTA
        else:
            status_text = " \u00b7 WAIT   "
            colour = Screen.COLOUR_WHITE
        # "│ " (2) + label_pad (14) + dots + status_text + " │" (2) = box_w
        label_part = f"\u2502 {label:<{_LABEL_PAD}}"
        dots_len = max(0, box_w - 2 - _LABEL_PAD - len(status_text) - 2)
        line = f"{label_part}{'.' * dots_len}{status_text} \u2502"
        try:
            screen.print_at(line, box_x, row_y, colour=colour)
        except Exception:
            pass

    # Bottom border
    bot_y = box_y + 1 + len(_AGENT_LABELS)
    if bot_y < height - 1:
        border_bot = "\u2514" + "\u2500" * (box_w - 2) + "\u2518"
        try:
            screen.print_at(border_bot, box_x, bot_y, colour=Screen.COLOUR_GREEN)
        except Exception:
            pass

    # Status message
    msg_y = bot_y + 2
    if msg_y < height - 1:
        if is_complete:
            msg = "  \u2713 ANALYSIS COMPLETE  "
            colour = Screen.COLOUR_GREEN
        else:
            msg = f"  {spinner_char} Analyzing...  "
            colour = Screen.COLOUR_CYAN
        msg_x = max(0, (width - len(msg)) // 2)
        try:
            screen.print_at(msg, msg_x, msg_y, colour=colour, attr=Screen.A_BOLD)
        except Exception:
            pass


# ---------------------------------------------------------------------------
# PlayAnimation -- the public API
# ---------------------------------------------------------------------------

_SPINNER = ["|", "/", "-", "\\"]
_T = TypeVar("_T")


class PlayAnimation:
    """Full-screen Matrix rain + ticker tape animation controller.

    The animation (Screen.wrapper) runs in the **main** thread so that
    signal handlers work. The analysis callable is executed in a background
    thread and its result is returned by :meth:`run`.

    Usage::

        anim = PlayAnimation("NVDA", tape_data=tape_data)
        result = anim.run(lambda: orchestrator.invoke(...))
    """

    def __init__(self, ticker: str, tape_data: list[dict] | None = None) -> None:
        """Prepare the animation.

        Args:
            ticker: Stock ticker symbol to display as ASCII art.
            tape_data: Pre-fetched ticker tape data. If None, a placeholder is used.
        """
        self._ticker = ticker.upper() if ticker else "????"
        raw_tape = _build_tape_string(tape_data or [])
        self._tape = raw_tape + "   " + raw_tape  # doubled for wrap
        self._status: dict[AgentEnum, StatusEnum] = {key: StatusEnum.WAIT for key, _ in _AGENT_LABELS}
        self._stop_event = threading.Event()
        self._failed = False
        self._figlet_lines = [
            ln for ln in pyfiglet.figlet_format("ThinkOnlyOnce", font="small").splitlines() if ln.strip()
        ]

        # Populated by run() / _render_loop
        self._analysis_fn: Callable[[], Any] | None = None
        self._analysis_result: Any = None
        self._analysis_error: BaseException | None = None

    def update_status(self, agent: AgentEnum, status: StatusEnum) -> None:
        """Update an agent's status (thread-safe via dict assignment).

        Args:
            agent: Agent identifier enum value.
            status: Status enum value.
        """
        self._status[agent] = status

    @property
    def failed(self) -> bool:
        """Whether the animation failed to start.

        Returns:
            True if the terminal does not support animation.
        """
        return self._failed

    def run(self, analysis_fn: Callable[[], _T]) -> _T:
        """Run *analysis_fn* in a background thread while animating.

        ``Screen.wrapper`` executes in the **main** thread (required by
        asciimatics for signal-handler registration).  *analysis_fn* is
        launched inside the render-loop callback so the screen is already
        active when the analysis starts.

        Args:
            analysis_fn: Zero-arg callable that performs the analysis and
                returns an ``AnalysisResult``.

        Returns:
            Whatever *analysis_fn* returned.
        """
        self._analysis_fn = analysis_fn

        try:
            Screen.wrapper(self._render_loop, catch_interrupt=True, unicode_aware=True)
        except Exception:
            self._failed = True

        self._raise_if_failed()
        return self._analysis_result

    def _raise_if_failed(self) -> None:
        """Re-raise any exception captured from the analysis thread."""  # noqa: DAR401,DAR402
        if self._analysis_error is not None:
            raise self._analysis_error

    def _render_loop(self, screen: Screen) -> None:
        """Custom render loop with full control over timing and exit.

        Args:
            screen: Asciimatics screen provided by Screen.wrapper.
        """
        # Build matrix rain columns
        columns = [_MatrixColumn(screen.height) for _ in range(screen.width)]
        tape_offset = 0
        frame = 0

        # Pre-compute the floating HUD panel geometry
        px, py, pw, ph, fig_y, fig_x = _compute_panel_geometry(
            screen.width, screen.height, self._figlet_lines,
        )

        # --- launch analysis in a background thread ---
        def _worker() -> None:
            try:
                self._analysis_result = self._analysis_fn()  # type: ignore[misc]
            except Exception as exc:
                self._analysis_error = exc
            finally:
                # Mark remaining agents done (preserve "skipped" status)
                for key, _ in _AGENT_LABELS:
                    if self._status.get(key) not in (StatusEnum.DONE, StatusEnum.SKIPPED):
                        self._status[key] = StatusEnum.DONE
                self._stop_event.set()

        worker = threading.Thread(target=_worker, daemon=True)
        worker.start()

        while True:
            # Check for stop
            if self._stop_event.is_set():
                # Show "COMPLETE" for ~1 second then exit
                for _ in range(20):
                    screen.clear_buffer(Screen.COLOUR_BLACK, Screen.A_NORMAL, Screen.COLOUR_BLACK)
                    _draw_matrix(screen, columns)
                    _draw_ticker_tape(screen, self._tape, tape_offset)
                    _draw_panel_bg(screen, px, py, pw, ph)
                    figlet_end = _draw_figlet(screen, self._figlet_lines, fig_x, fig_y)
                    _draw_status_box(screen, figlet_end, self._status, "\u2713", True)
                    screen.refresh()
                    time.sleep(0.05)
                    frame += 1
                    tape_offset += 1
                break

            # Normal frame
            try:
                screen.clear_buffer(Screen.COLOUR_BLACK, Screen.A_NORMAL, Screen.COLOUR_BLACK)
                _draw_matrix(screen, columns)
                _draw_ticker_tape(screen, self._tape, tape_offset)
                _draw_panel_bg(screen, px, py, pw, ph)
                figlet_end = _draw_figlet(screen, self._figlet_lines, fig_x, fig_y)
                spinner = _SPINNER[(frame // 5) % len(_SPINNER)]
                _draw_status_box(screen, figlet_end, self._status, spinner, False)
                screen.refresh()
            except Exception:
                break

            frame += 1
            if frame % 2 == 0:
                tape_offset += 1

            time.sleep(0.05)  # ~20 fps

        # Wait for analysis thread to finish before Screen.wrapper restores terminal
        worker.join(timeout=5)


def fetch_tape_data_async() -> tuple[Callable[[], list[dict]], threading.Thread]:
    """Start fetching ticker tape data in a background thread.

    Returns:
        A tuple of (getter_function, thread). Call the getter after
        thread.join() to retrieve the results.
    """
    result: list[dict] = []

    def _fetch() -> None:
        nonlocal result
        result = _fetch_tape_data()

    thread = threading.Thread(target=_fetch, daemon=True)
    thread.start()
    return lambda: result, thread
