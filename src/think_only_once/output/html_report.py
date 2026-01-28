"""HTML report generator with professional styling."""

import re
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from think_only_once.models import PriceHistory

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Stock Analysis Report - {ticker}</title>
    <style>
        :root {{
            --apple-blue: #0071e3;
            --apple-blue-hover: #0077ed;
            --apple-gray: #f5f5f7;
            --apple-dark: #1d1d1f;
            --apple-text: #1d1d1f;
            --apple-text-secondary: #86868b;
            --apple-border: #d2d2d7;
            --apple-card: #ffffff;
            --success: #34c759;
            --warning: #ff9500;
            --danger: #ff3b30;
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'SF Pro Text', 'Helvetica Neue', Helvetica, Arial, sans-serif;
            background: var(--apple-gray);
            min-height: 100vh;
            padding: 60px 24px;
            line-height: 1.47059;
            color: var(--apple-text);
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
        }}

        .container {{
            max-width: 980px;
            margin: 0 auto;
        }}

        .report {{
            background: var(--apple-card);
            border-radius: 18px;
            box-shadow: 0 4px 24px rgba(0, 0, 0, 0.08);
            overflow: hidden;
        }}

        .header {{
            background: var(--apple-dark);
            color: white;
            padding: 80px 48px 60px;
            text-align: center;
        }}

        .brand-title {{
            font-size: 4rem;
            font-weight: 700;
            letter-spacing: -0.02em;
            margin-bottom: 8px;
            background: linear-gradient(90deg, #fff 0%, #a1a1a6 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}

        .header h1 {{
            font-size: 1.5rem;
            font-weight: 400;
            margin-bottom: 24px;
            color: #a1a1a6;
            letter-spacing: -0.01em;
        }}

        .ticker-badge {{
            display: inline-block;
            background: var(--apple-blue);
            padding: 12px 32px;
            border-radius: 980px;
            font-size: 1.5rem;
            font-weight: 600;
            letter-spacing: 0.02em;
        }}

        .meta {{
            display: flex;
            justify-content: center;
            gap: 32px;
            margin-top: 32px;
            font-size: 0.875rem;
            color: #a1a1a6;
        }}

        .meta-item {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        .content {{
            padding: 48px;
        }}

        .toggle-controls {{
            display: flex;
            justify-content: flex-end;
            gap: 12px;
            margin-bottom: 24px;
        }}

        .toggle-btn {{
            background: transparent;
            border: none;
            border-radius: 980px;
            padding: 12px 20px;
            font-size: 0.875rem;
            font-weight: 400;
            color: var(--apple-blue);
            cursor: pointer;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            font-family: inherit;
        }}

        .toggle-btn:hover {{
            background: rgba(0, 113, 227, 0.1);
        }}

        .recommendation-summary {{
            background: var(--apple-card);
            border: none;
            border-radius: 18px;
            padding: 32px 40px;
            margin-bottom: 32px;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 16px;
            box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
        }}

        .recommendation-summary .label {{
            font-size: 1.25rem;
            font-weight: 600;
            color: var(--apple-text);
            letter-spacing: -0.01em;
        }}

        .recommendation-summary .recommendation {{
            font-size: 1.25rem;
            padding: 10px 24px;
            font-weight: 600;
        }}

        .section {{
            margin-bottom: 16px;
            background: var(--apple-card);
            border-radius: 18px;
            overflow: hidden;
            box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
            border: none;
        }}

        .section:last-child {{
            margin-bottom: 0;
        }}

        .section-header {{
            display: flex;
            align-items: center;
            gap: 16px;
            padding: 24px 28px;
            background: var(--apple-card);
            border-bottom: 1px solid var(--apple-border);
            cursor: pointer;
            user-select: none;
            transition: background-color 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }}

        .section-header:hover {{
            background: var(--apple-gray);
        }}

        .section-toggle {{
            margin-left: auto;
            width: 28px;
            height: 28px;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            color: var(--apple-text-secondary);
            font-size: 0.875rem;
        }}

        .section.collapsed .section-toggle {{
            transform: rotate(-90deg);
        }}

        .section-icon {{
            width: 44px;
            height: 44px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.375rem;
        }}

        .section-icon.technical {{
            background: linear-gradient(135deg, #5e5ce6 0%, #bf5af2 100%);
        }}

        .section-icon.fundamental {{
            background: linear-gradient(135deg, #30d158 0%, #34c759 100%);
        }}

        .section-icon.news {{
            background: linear-gradient(135deg, #ff9f0a 0%, #ff9500 100%);
        }}

        .section-icon.outlook {{
            background: linear-gradient(135deg, #0a84ff 0%, #0071e3 100%);
        }}

        .section-title {{
            font-size: 1.25rem;
            font-weight: 600;
            color: var(--apple-text);
            letter-spacing: -0.01em;
        }}

        .section-content {{
            padding: 28px;
            color: var(--apple-text-secondary);
            font-size: 1rem;
            line-height: 1.5;
            max-height: 3000px;
            overflow: hidden;
            transition: max-height 0.4s cubic-bezier(0.4, 0, 0.2, 1),
                        padding 0.3s cubic-bezier(0.4, 0, 0.2, 1),
                        opacity 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            opacity: 1;
        }}

        .section.collapsed .section-content {{
            max-height: 0;
            padding-top: 0;
            padding-bottom: 0;
            opacity: 0;
        }}

        .section.collapsed .section-header {{
            border-bottom: none;
        }}

        .section-content p {{
            margin-bottom: 16px;
            color: var(--apple-text);
        }}

        .section-content p:last-child {{
            margin-bottom: 0;
        }}

        .section-content strong {{
            color: var(--apple-text);
            font-weight: 600;
        }}

        .section-content ul, .section-content ol {{
            margin: 16px 0;
            padding-left: 24px;
            color: var(--apple-text);
        }}

        .section-content li {{
            margin-bottom: 10px;
        }}

        .section-content .subsection-title {{
            font-size: 1.125rem;
            font-weight: 600;
            color: var(--apple-text);
            margin: 32px 0 16px 0;
            padding-bottom: 12px;
            border-bottom: 1px solid var(--apple-border);
            letter-spacing: -0.01em;
        }}

        .section-content .subsection-title:first-child {{
            margin-top: 0;
        }}

        .recommendation {{
            display: inline-block;
            padding: 8px 20px;
            border-radius: 980px;
            font-weight: 600;
            font-size: 0.9375rem;
            text-transform: uppercase;
            letter-spacing: 0.02em;
        }}

        .recommendation.buy {{
            background: rgba(52, 199, 89, 0.12);
            color: #248a3d;
        }}

        .recommendation.hold {{
            background: rgba(255, 149, 0, 0.12);
            color: #c93400;
        }}

        .recommendation.sell {{
            background: rgba(255, 59, 48, 0.12);
            color: #d70015;
        }}

        .highlight-box {{
            background: var(--apple-gray);
            border-left: 4px solid var(--apple-blue);
            padding: 20px 24px;
            margin: 20px 0;
            border-radius: 0 12px 12px 0;
        }}

        .footer {{
            text-align: center;
            padding: 32px 48px;
            background: var(--apple-gray);
            color: var(--apple-text-secondary);
            font-size: 0.875rem;
        }}

        .footer strong {{
            color: var(--apple-text);
        }}

        .price-chart-container {{
            background: var(--apple-card);
            border-radius: 18px;
            padding: 28px;
            margin-bottom: 16px;
            box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
        }}

        .price-chart-header {{
            display: flex;
            align-items: center;
            gap: 16px;
            margin-bottom: 24px;
        }}

        .price-chart-icon {{
            width: 44px;
            height: 44px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.375rem;
            background: linear-gradient(135deg, #0a84ff 0%, #5e5ce6 100%);
        }}

        .price-chart-title {{
            font-size: 1.25rem;
            font-weight: 600;
            color: var(--apple-text);
            letter-spacing: -0.01em;
        }}

        .price-chart-subtitle {{
            font-size: 0.875rem;
            color: var(--apple-text-secondary);
            margin-top: 4px;
        }}

        .chart-svg {{
            width: 100%;
            height: auto;
            display: block;
        }}

        .chart-price-info {{
            display: flex;
            justify-content: space-between;
            margin-top: 20px;
            padding-top: 20px;
            border-top: 1px solid var(--apple-border);
        }}

        .chart-stat {{
            text-align: center;
        }}

        .chart-stat-label {{
            font-size: 0.75rem;
            color: var(--apple-text-secondary);
            text-transform: uppercase;
            letter-spacing: 0.04em;
            margin-bottom: 4px;
        }}

        .chart-stat-value {{
            font-size: 1.125rem;
            font-weight: 600;
            color: var(--apple-text);
        }}

        .chart-stat-value.positive {{
            color: var(--success);
        }}

        .chart-stat-value.negative {{
            color: var(--danger);
        }}

        @media (max-width: 734px) {{
            body {{
                padding: 24px 16px;
            }}

            .header {{
                padding: 48px 24px 40px;
            }}

            .brand-title {{
                font-size: 2.5rem;
            }}

            .header h1 {{
                font-size: 1.125rem;
            }}

            .ticker-badge {{
                font-size: 1.125rem;
                padding: 10px 24px;
            }}

            .content {{
                padding: 24px;
            }}

            .section-header {{
                padding: 20px;
            }}

            .section-content {{
                padding: 20px;
            }}

            .meta {{
                flex-direction: column;
                gap: 12px;
            }}

            .recommendation-summary {{
                flex-direction: column;
                padding: 24px;
                gap: 12px;
            }}

            .price-chart-container {{
                padding: 20px;
            }}

            .chart-price-info {{
                flex-wrap: wrap;
                gap: 16px;
            }}

            .chart-stat {{
                flex: 1 1 40%;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <article class="report">
            <header class="header">
                <div class="brand-title">ThinkOnlyOnce</div>
                <h1>Stock Analysis Report</h1>
                <div class="ticker-badge">{ticker}</div>
                <div class="meta">
                    <span class="meta-item">📅 {date}</span>
                    <span class="meta-item">🕐 {time}</span>
                </div>
            </header>
            <div class="content">
                <div class="toggle-controls">
                    <button class="toggle-btn" onclick="expandAll()">Expand All</button>
                    <button class="toggle-btn" onclick="collapseAll()">Collapse All</button>
                </div>
                {recommendation_summary}
                {price_chart}
                {sections}
            </div>
            <footer class="footer">
                Generated by <strong>ThinkOnlyOnce</strong> Multi-Agent Stock Analyzer
            </footer>
        </article>
    </div>
    <script>
        function toggleSection(section) {{
            section.classList.toggle('collapsed');
        }}

        function expandAll() {{
            document.querySelectorAll('.section').forEach(s => s.classList.remove('collapsed'));
        }}

        function collapseAll() {{
            document.querySelectorAll('.section').forEach(s => s.classList.add('collapsed'));
        }}
    </script>
</body>
</html>
"""

SECTION_TEMPLATE = """
<section class="section collapsed">
    <div class="section-header" onclick="toggleSection(this.parentElement)">
        <div class="section-icon {icon_class}">{icon}</div>
        <h2 class="section-title">{title}</h2>
        <div class="section-toggle">▼</div>
    </div>
    <div class="section-content">
        {content}
    </div>
</section>
"""

SECTION_CONFIG = {
    "Technical Analysis": {"icon": "📈", "icon_class": "technical"},
    "Fundamental Analysis": {"icon": "📊", "icon_class": "fundamental"},
    "News & Sentiment Analysis": {"icon": "📰", "icon_class": "news"},
    "AI Investment Outlook": {"icon": "🎯", "icon_class": "outlook"},
}

PRICE_CHART_TEMPLATE = """
<div class="price-chart-container">
    <div class="price-chart-header">
        <div class="price-chart-icon">📉</div>
        <div>
            <div class="price-chart-title">Price History</div>
            <div class="price-chart-subtitle">{period_label} • {ticker}</div>
        </div>
    </div>
    {svg_chart}
    <div class="chart-price-info">
        <div class="chart-stat">
            <div class="chart-stat-label">Current</div>
            <div class="chart-stat-value">${current_price:.2f}</div>
        </div>
        <div class="chart-stat">
            <div class="chart-stat-label">Period High</div>
            <div class="chart-stat-value">${high_price:.2f}</div>
        </div>
        <div class="chart-stat">
            <div class="chart-stat-label">Period Low</div>
            <div class="chart-stat-value">${low_price:.2f}</div>
        </div>
        <div class="chart-stat">
            <div class="chart-stat-label">Change</div>
            <div class="chart-stat-value {change_class}">{change_sign}{change_pct:.1f}%</div>
        </div>
    </div>
</div>
"""


def _generate_svg_chart(price_history: "PriceHistory") -> str:
    """Generate an SVG line chart from price history data.

    Args:
        price_history: PriceHistory model with OHLCV data points.

    Returns:
        SVG string for the price chart.
    """
    if not price_history.data:
        return ""

    # Chart dimensions
    width = 900
    height = 300
    padding_left = 60
    padding_right = 20
    padding_top = 20
    padding_bottom = 40

    chart_width = width - padding_left - padding_right
    chart_height = height - padding_top - padding_bottom

    # Extract closing prices and dates
    closes = [p.close for p in price_history.data]
    dates = [p.date for p in price_history.data]

    min_price = min(closes) * 0.98  # Add 2% padding
    max_price = max(closes) * 1.02

    price_range = max_price - min_price
    if price_range == 0:
        price_range = 1  # Avoid division by zero

    # Calculate points for the line
    points = []
    for i, close in enumerate(closes):
        x = padding_left + (i / (len(closes) - 1)) * chart_width if len(closes) > 1 else padding_left + chart_width / 2
        y = padding_top + (1 - (close - min_price) / price_range) * chart_height
        points.append((x, y))

    # Create path for the line
    path_d = f"M {points[0][0]:.1f} {points[0][1]:.1f}"
    for x, y in points[1:]:
        path_d += f" L {x:.1f} {y:.1f}"

    # Create gradient fill path
    fill_path_d = path_d + f" L {points[-1][0]:.1f} {padding_top + chart_height} L {points[0][0]:.1f} {padding_top + chart_height} Z"

    # Determine chart color based on price trend
    start_price = closes[0]
    end_price = closes[-1]
    is_positive = end_price >= start_price
    line_color = "#34c759" if is_positive else "#ff3b30"
    gradient_id = "chartGradient"

    # Generate Y-axis labels (5 labels)
    y_labels = []
    for i in range(5):
        price = min_price + (price_range * i / 4)
        y = padding_top + chart_height - (i / 4) * chart_height
        y_labels.append((y, price))

    # Generate X-axis labels (show ~5 dates)
    x_labels = []
    step = max(1, len(dates) // 4)
    for i in range(0, len(dates), step):
        x = padding_left + (i / (len(dates) - 1)) * chart_width if len(dates) > 1 else padding_left + chart_width / 2
        date_str = dates[i][5:]  # MM-DD format
        x_labels.append((x, date_str))

    # Build SVG
    svg = f"""<svg class="chart-svg" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">
    <defs>
        <linearGradient id="{gradient_id}" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" style="stop-color:{line_color};stop-opacity:0.3" />
            <stop offset="100%" style="stop-color:{line_color};stop-opacity:0.05" />
        </linearGradient>
    </defs>

    <!-- Grid lines -->
    <g stroke="#e5e5e7" stroke-width="1">"""

    for y, _ in y_labels:
        svg += f'\n        <line x1="{padding_left}" y1="{y:.1f}" x2="{width - padding_right}" y2="{y:.1f}" />'

    svg += """
    </g>

    <!-- Y-axis labels -->
    <g fill="#86868b" font-size="11" font-family="-apple-system, BlinkMacSystemFont, sans-serif" text-anchor="end">"""

    for y, price in y_labels:
        svg += f'\n        <text x="{padding_left - 10}" y="{y + 4:.1f}">${price:,.0f}</text>'

    svg += """
    </g>

    <!-- X-axis labels -->
    <g fill="#86868b" font-size="11" font-family="-apple-system, BlinkMacSystemFont, sans-serif" text-anchor="middle">"""

    for x, date_str in x_labels:
        svg += f'\n        <text x="{x:.1f}" y="{height - 10}">{date_str}</text>'

    svg += f"""
    </g>

    <!-- Gradient fill -->
    <path d="{fill_path_d}" fill="url(#{gradient_id})" />

    <!-- Price line -->
    <path d="{path_d}" fill="none" stroke="{line_color}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" />

    <!-- End point dot -->
    <circle cx="{points[-1][0]:.1f}" cy="{points[-1][1]:.1f}" r="5" fill="{line_color}" />
    <circle cx="{points[-1][0]:.1f}" cy="{points[-1][1]:.1f}" r="3" fill="white" />
</svg>"""

    return svg


def _generate_price_chart_html(price_history: "PriceHistory") -> str:
    """Generate complete price chart HTML section.

    Args:
        price_history: PriceHistory model with OHLCV data points.

    Returns:
        HTML string for the price chart section, or empty string if no data.
    """
    if not price_history or not price_history.data:
        return ""

    svg_chart = _generate_svg_chart(price_history)
    if not svg_chart:
        return ""

    closes = [p.close for p in price_history.data]
    current_price = closes[-1]
    high_price = max(closes)
    low_price = min(closes)
    start_price = closes[0]

    change_pct = ((current_price - start_price) / start_price) * 100 if start_price else 0
    change_class = "positive" if change_pct >= 0 else "negative"
    change_sign = "+" if change_pct >= 0 else ""

    # Period label mapping
    period_labels = {
        "1mo": "1 Month",
        "3mo": "3 Months",
        "6mo": "6 Months",
        "1y": "1 Year",
        "2y": "2 Years",
    }
    period_label = period_labels.get(price_history.period, price_history.period)

    return PRICE_CHART_TEMPLATE.format(
        ticker=price_history.ticker,
        period_label=period_label,
        svg_chart=svg_chart,
        current_price=current_price,
        high_price=high_price,
        low_price=low_price,
        change_pct=abs(change_pct),
        change_class=change_class,
        change_sign=change_sign,
    )


def _markdown_to_html(text: str) -> str:
    """Convert markdown text to HTML.

    Args:
        text: Markdown formatted text.

    Returns:
        HTML formatted string.
    """
    if not text:
        return ""

    # Escape HTML special characters first
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    # Bold text: **text** or __text__
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"__(.+?)__", r"<strong>\1</strong>", text)

    # Italic text: *text* or _text_
    text = re.sub(r"\*(.+?)\*", r"<em>\1</em>", text)
    text = re.sub(r"_(.+?)_", r"<em>\1</em>", text)

    # Convert bullet lists
    lines = text.split("\n")
    result_lines = []
    in_list = False

    for line in lines:
        stripped = line.strip()

        # Check for bullet points
        if stripped.startswith("- ") or stripped.startswith("* "):
            if not in_list:
                result_lines.append("<ul>")
                in_list = True
            result_lines.append(f"<li>{stripped[2:]}</li>")
        # Check for numbered lists
        elif re.match(r"^\d+\.\s", stripped):
            if not in_list:
                result_lines.append("<ol>")
                in_list = True
            content = re.sub(r"^\d+\.\s", "", stripped)
            result_lines.append(f"<li>{content}</li>")
        else:
            if in_list:
                # Close the list
                if result_lines and "<ol>" in "".join(result_lines[-10:]):
                    result_lines.append("</ol>")
                else:
                    result_lines.append("</ul>")
                in_list = False

            # Check for ### subsection headers
            if stripped.startswith("### "):
                result_lines.append(f'<h3 class="subsection-title">{stripped[4:]}</h3>')
            # Regular paragraph
            elif stripped:
                result_lines.append(f"<p>{stripped}</p>")

    # Close any open list
    if in_list:
        if "<ol>" in "".join(result_lines[-10:]):
            result_lines.append("</ol>")
        else:
            result_lines.append("</ul>")

    html = "\n".join(result_lines)

    # Add recommendation styling
    html = re.sub(
        r"<strong>Recommendation:</strong>\s*(BUY)",
        r'<strong>Recommendation:</strong> <span class="recommendation buy">\1</span>',
        html,
        flags=re.IGNORECASE,
    )
    html = re.sub(
        r"<strong>Recommendation:</strong>\s*(HOLD)",
        r'<strong>Recommendation:</strong> <span class="recommendation hold">\1</span>',
        html,
        flags=re.IGNORECASE,
    )
    html = re.sub(
        r"<strong>Recommendation:</strong>\s*(SELL)",
        r'<strong>Recommendation:</strong> <span class="recommendation sell">\1</span>',
        html,
        flags=re.IGNORECASE,
    )

    return html


def _parse_markdown_report(markdown_report: str) -> tuple[str, list[tuple[str, str]]]:
    """Parse markdown report into ticker and sections.

    Only recognizes the 4 main section headers. Any other ## headers within the content
    are converted to ### subsections to avoid creating extra section cards.

    Args:
        markdown_report: The markdown formatted report.

    Returns:
        Tuple of (ticker, list of (section_title, section_content) pairs).
    """
    # Extract ticker from title
    ticker_match = re.search(r"# Stock Analysis Report:\s*(\w+)", markdown_report)
    ticker = ticker_match.group(1) if ticker_match else "UNKNOWN"

    # Only these 4 are recognized as main sections
    main_sections = set(SECTION_CONFIG.keys())

    # Split by ## headers
    sections: list[tuple[str, str]] = []
    current_title: str | None = None
    current_content: list[str] = []

    for line in markdown_report.split("\n"):
        if line.startswith("## "):
            header_title = line[3:].strip()
            if header_title in main_sections:
                # This is a main section - save previous and start new
                if current_title:
                    sections.append((current_title, "\n".join(current_content).strip()))
                current_title = header_title
                current_content = []
            elif current_title:
                # This is a subsection within a main section - convert to ### and keep as content
                current_content.append(f"### {header_title}")
            # If no current_title yet, skip unrecognized headers before first main section
        elif line.startswith("# ") or line.startswith("---") or line.startswith("*Generated"):
            # Skip title, separator, and footer
            continue
        elif current_title:
            current_content.append(line)

    # Save last section
    if current_title:
        sections.append((current_title, "\n".join(current_content).strip()))

    return ticker, sections


def _extract_recommendation(sections: list[tuple[str, str]]) -> str:
    """Extract recommendation from AI Investment Outlook section.

    Args:
        sections: List of (title, content) tuples.

    Returns:
        HTML string for recommendation summary, or empty string if not found.
    """
    for title, content in sections:
        if title == "AI Investment Outlook":
            # Look for "Recommendation:" pattern
            match = re.search(r"\*\*Recommendation:\*\*\s*(.+?)(?:\n|$)", content)
            if match:
                rec_text = match.group(1).strip()
                # Determine badge class
                rec_lower = rec_text.lower()
                if "buy" in rec_lower:
                    badge_class = "buy"
                elif "sell" in rec_lower:
                    badge_class = "sell"
                else:
                    badge_class = "hold"
                return f'''<div class="recommendation-summary">
                    <span class="label">Recommendation:</span>
                    <span class="recommendation {badge_class}">{rec_text}</span>
                </div>'''
    return ""


def generate_html_report(markdown_report: str, price_history: "PriceHistory | None" = None) -> str:
    """Generate a styled HTML report from markdown.

    Args:
        markdown_report: The markdown formatted analysis report.
        price_history: Optional price history data for chart visualization.

    Returns:
        Complete HTML document as string.
    """
    ticker, sections = _parse_markdown_report(markdown_report)

    # Extract recommendation summary
    recommendation_summary = _extract_recommendation(sections)

    # Generate price chart HTML
    price_chart_html = _generate_price_chart_html(price_history) if price_history else ""

    # Generate section HTML
    sections_html = []
    for title, content in sections:
        config = SECTION_CONFIG.get(title, {"icon": "📋", "icon_class": "technical"})
        html_content = _markdown_to_html(content)

        section_html = SECTION_TEMPLATE.format(
            icon=config["icon"],
            icon_class=config["icon_class"],
            title=title,
            content=html_content,
        )
        sections_html.append(section_html)

    # Generate timestamp
    now = datetime.now()
    date_str = now.strftime("%B %d, %Y")
    time_str = now.strftime("%H:%M")

    # Generate final HTML
    html = HTML_TEMPLATE.format(
        ticker=ticker,
        date=date_str,
        time=time_str,
        recommendation_summary=recommendation_summary,
        price_chart=price_chart_html,
        sections="\n".join(sections_html),
    )

    return html


def save_html_report(
    markdown_report: str,
    output_dir: Path | str | None = None,
    price_history: "PriceHistory | None" = None,
) -> Path:
    """Save the analysis report as an HTML file.

    Args:
        markdown_report: The markdown formatted analysis report.
        output_dir: Directory to save the report. Defaults to 'reports' in project root.
        price_history: Optional price history data for chart visualization.

    Returns:
        Path to the saved HTML file.
    """
    # Parse ticker for filename
    ticker, _ = _parse_markdown_report(markdown_report)

    # Setup output directory
    if output_dir is None:
        output_dir = Path(__file__).parent.parent.parent.parent / "reports"
    else:
        output_dir = Path(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    filename = f"{ticker}_analysis_{timestamp}.html"
    output_path = output_dir / filename

    # Generate and save HTML
    html_content = generate_html_report(markdown_report, price_history=price_history)
    output_path.write_text(html_content, encoding="utf-8")

    return output_path
