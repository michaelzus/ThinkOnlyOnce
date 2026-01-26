"""HTML report generator with professional styling."""

import re
from datetime import datetime
from pathlib import Path

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Stock Analysis Report - {ticker}</title>
    <style>
        :root {{
            --primary: #1a73e8;
            --primary-dark: #1557b0;
            --success: #34a853;
            --warning: #fbbc04;
            --danger: #ea4335;
            --neutral: #5f6368;
            --bg-primary: #ffffff;
            --bg-secondary: #f8f9fa;
            --bg-card: #ffffff;
            --text-primary: #202124;
            --text-secondary: #5f6368;
            --border: #dadce0;
            --shadow: rgba(60, 64, 67, 0.15);
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 40px 20px;
            line-height: 1.6;
            color: var(--text-primary);
        }}

        .container {{
            max-width: 900px;
            margin: 0 auto;
        }}

        .report {{
            background: var(--bg-primary);
            border-radius: 16px;
            box-shadow: 0 20px 60px var(--shadow);
            overflow: hidden;
        }}

        .header {{
            background: linear-gradient(135deg, #1a73e8 0%, #4285f4 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}

        .header h1 {{
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 8px;
            letter-spacing: -0.5px;
        }}

        .ticker-badge {{
            display: inline-block;
            background: rgba(255, 255, 255, 0.2);
            padding: 8px 24px;
            border-radius: 50px;
            font-size: 1.25rem;
            font-weight: 600;
            margin-top: 12px;
            backdrop-filter: blur(10px);
        }}

        .meta {{
            display: flex;
            justify-content: center;
            gap: 24px;
            margin-top: 20px;
            font-size: 0.9rem;
            opacity: 0.9;
        }}

        .meta-item {{
            display: flex;
            align-items: center;
            gap: 6px;
        }}

        .content {{
            padding: 40px;
        }}

        .section {{
            margin-bottom: 32px;
            background: var(--bg-secondary);
            border-radius: 12px;
            overflow: hidden;
            border: 1px solid var(--border);
        }}

        .section:last-child {{
            margin-bottom: 0;
        }}

        .section-header {{
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 20px 24px;
            background: var(--bg-card);
            border-bottom: 1px solid var(--border);
        }}

        .section-icon {{
            width: 40px;
            height: 40px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.25rem;
        }}

        .section-icon.technical {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }}

        .section-icon.fundamental {{
            background: linear-gradient(135deg, #34a853 0%, #0d652d 100%);
        }}

        .section-icon.news {{
            background: linear-gradient(135deg, #fbbc04 0%, #ea8600 100%);
        }}

        .section-icon.outlook {{
            background: linear-gradient(135deg, #1a73e8 0%, #4285f4 100%);
        }}

        .section-title {{
            font-size: 1.25rem;
            font-weight: 600;
            color: var(--text-primary);
        }}

        .section-content {{
            padding: 24px;
            color: var(--text-secondary);
            font-size: 0.95rem;
        }}

        .section-content p {{
            margin-bottom: 16px;
        }}

        .section-content p:last-child {{
            margin-bottom: 0;
        }}

        .section-content strong {{
            color: var(--text-primary);
            font-weight: 600;
        }}

        .section-content ul, .section-content ol {{
            margin: 16px 0;
            padding-left: 24px;
        }}

        .section-content li {{
            margin-bottom: 8px;
        }}

        .recommendation {{
            display: inline-block;
            padding: 6px 16px;
            border-radius: 50px;
            font-weight: 600;
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        .recommendation.buy {{
            background: #e6f4ea;
            color: #137333;
        }}

        .recommendation.hold {{
            background: #fef7e0;
            color: #b06000;
        }}

        .recommendation.sell {{
            background: #fce8e6;
            color: #c5221f;
        }}

        .highlight-box {{
            background: linear-gradient(135deg, #e8f0fe 0%, #f3e8fd 100%);
            border-left: 4px solid var(--primary);
            padding: 16px 20px;
            margin: 16px 0;
            border-radius: 0 8px 8px 0;
        }}

        .footer {{
            text-align: center;
            padding: 24px 40px;
            background: var(--bg-secondary);
            border-top: 1px solid var(--border);
            color: var(--text-secondary);
            font-size: 0.85rem;
        }}

        .footer a {{
            color: var(--primary);
            text-decoration: none;
        }}

        .footer a:hover {{
            text-decoration: underline;
        }}

        @media (max-width: 640px) {{
            body {{
                padding: 20px 12px;
            }}

            .header {{
                padding: 30px 20px;
            }}

            .header h1 {{
                font-size: 1.75rem;
            }}

            .content {{
                padding: 20px;
            }}

            .section-header {{
                padding: 16px;
            }}

            .section-content {{
                padding: 16px;
            }}

            .meta {{
                flex-direction: column;
                gap: 8px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <article class="report">
            <header class="header">
                <h1>Stock Analysis Report</h1>
                <div class="ticker-badge">{ticker}</div>
                <div class="meta">
                    <span class="meta-item">📅 {date}</span>
                    <span class="meta-item">🕐 {time}</span>
                </div>
            </header>
            <div class="content">
                {sections}
            </div>
            <footer class="footer">
                Generated by <strong>ThinkOnlyOnce</strong> Multi-Agent Stock Analyzer
            </footer>
        </article>
    </div>
</body>
</html>
"""

SECTION_TEMPLATE = """
<section class="section">
    <div class="section-header">
        <div class="section-icon {icon_class}">{icon}</div>
        <h2 class="section-title">{title}</h2>
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

            # Regular paragraph
            if stripped:
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

    Args:
        markdown_report: The markdown formatted report.

    Returns:
        Tuple of (ticker, list of (section_title, section_content) pairs).
    """
    # Extract ticker from title
    ticker_match = re.search(r"# Stock Analysis Report:\s*(\w+)", markdown_report)
    ticker = ticker_match.group(1) if ticker_match else "UNKNOWN"

    # Split by ## headers
    sections: list[tuple[str, str]] = []
    current_title: str | None = None
    current_content: list[str] = []

    for line in markdown_report.split("\n"):
        if line.startswith("## "):
            # Save previous section if exists
            if current_title:
                sections.append((current_title, "\n".join(current_content).strip()))
            current_title = line[3:].strip()
            current_content = []
        elif line.startswith("# ") or line.startswith("---") or line.startswith("*Generated"):
            # Skip title, separator, and footer
            continue
        elif current_title:
            current_content.append(line)

    # Save last section
    if current_title:
        sections.append((current_title, "\n".join(current_content).strip()))

    return ticker, sections


def generate_html_report(markdown_report: str) -> str:
    """Generate a styled HTML report from markdown.

    Args:
        markdown_report: The markdown formatted analysis report.

    Returns:
        Complete HTML document as string.
    """
    ticker, sections = _parse_markdown_report(markdown_report)

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
        sections="\n".join(sections_html),
    )

    return html


def save_html_report(markdown_report: str, output_dir: Path | str | None = None) -> Path:
    """Save the analysis report as an HTML file.

    Args:
        markdown_report: The markdown formatted analysis report.
        output_dir: Directory to save the report. Defaults to 'reports' in project root.

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
    html_content = generate_html_report(markdown_report)
    output_path.write_text(html_content, encoding="utf-8")

    return output_path
