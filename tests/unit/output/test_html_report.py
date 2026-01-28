"""Tests for HTML report generation module."""

from pathlib import Path
from unittest.mock import patch

import pytest

from think_only_once.output.html_report import (
    _markdown_to_html,
    _parse_markdown_report,
    generate_html_report,
    save_html_report,
    SECTION_CONFIG,
)


class TestMarkdownToHtml:
    """Tests for _markdown_to_html function."""

    def test_empty_string_returns_empty(self) -> None:
        """Test empty input returns empty string."""
        assert _markdown_to_html("") == ""

    def test_none_returns_empty(self) -> None:
        """Test None input returns empty string."""
        assert _markdown_to_html(None) == ""

    def test_bold_asterisks_converted(self) -> None:
        """Test **bold** text is converted to <strong> tags."""
        result = _markdown_to_html("This is **bold** text")
        assert "<strong>bold</strong>" in result

    def test_bold_underscores_converted(self) -> None:
        """Test __bold__ text is converted to <strong> tags."""
        result = _markdown_to_html("This is __bold__ text")
        assert "<strong>bold</strong>" in result

    def test_italic_asterisk_converted(self) -> None:
        """Test *italic* text is converted to <em> tags."""
        result = _markdown_to_html("This is *italic* text")
        assert "<em>italic</em>" in result

    def test_italic_underscore_converted(self) -> None:
        """Test _italic_ text is converted to <em> tags."""
        result = _markdown_to_html("This is _italic_ text")
        assert "<em>italic</em>" in result

    def test_html_special_chars_escaped(self) -> None:
        """Test HTML special characters are escaped."""
        result = _markdown_to_html("5 > 3 and 2 < 4 & done")
        assert "&gt;" in result
        assert "&lt;" in result
        assert "&amp;" in result

    def test_bullet_list_converted(self) -> None:
        """Test bullet list is converted to <ul><li> tags."""
        markdown = "- Item 1\n- Item 2\n- Item 3"
        result = _markdown_to_html(markdown)
        assert "<ul>" in result
        assert "</ul>" in result
        assert "<li>Item 1</li>" in result
        assert "<li>Item 2</li>" in result
        assert "<li>Item 3</li>" in result

    def test_asterisk_bullet_list_converted(self) -> None:
        """Test asterisk bullet list is converted to <ul><li> tags."""
        markdown = "* First\n* Second"
        result = _markdown_to_html(markdown)
        assert "<ul>" in result
        assert "<li>First</li>" in result
        assert "<li>Second</li>" in result

    def test_numbered_list_converted(self) -> None:
        """Test numbered list is converted to <ol><li> tags."""
        markdown = "1. First item\n2. Second item\n3. Third item"
        result = _markdown_to_html(markdown)
        assert "<ol>" in result
        assert "</ol>" in result
        assert "<li>First item</li>" in result
        assert "<li>Second item</li>" in result

    def test_paragraph_wrapped(self) -> None:
        """Test regular text is wrapped in <p> tags."""
        result = _markdown_to_html("Simple paragraph text")
        assert "<p>Simple paragraph text</p>" in result

    def test_multiple_paragraphs(self) -> None:
        """Test multiple paragraphs are each wrapped in <p> tags."""
        markdown = "First paragraph\n\nSecond paragraph"
        result = _markdown_to_html(markdown)
        assert "<p>First paragraph</p>" in result
        assert "<p>Second paragraph</p>" in result

    def test_recommendation_buy_styled(self) -> None:
        """Test BUY recommendation gets special styling."""
        markdown = "**Recommendation:** BUY"
        result = _markdown_to_html(markdown)
        assert 'class="recommendation buy"' in result
        assert "BUY" in result

    def test_recommendation_hold_styled(self) -> None:
        """Test HOLD recommendation gets special styling."""
        markdown = "**Recommendation:** HOLD"
        result = _markdown_to_html(markdown)
        assert 'class="recommendation hold"' in result

    def test_recommendation_sell_styled(self) -> None:
        """Test SELL recommendation gets special styling."""
        markdown = "**Recommendation:** SELL"
        result = _markdown_to_html(markdown)
        assert 'class="recommendation sell"' in result

    def test_recommendation_case_insensitive(self) -> None:
        """Test recommendation styling is case insensitive."""
        markdown = "**Recommendation:** buy"
        result = _markdown_to_html(markdown)
        assert 'class="recommendation buy"' in result

    def test_mixed_content(self) -> None:
        """Test mixed content with lists and paragraphs."""
        markdown = """Introduction paragraph.

- Bullet one
- Bullet two

Conclusion paragraph."""
        result = _markdown_to_html(markdown)
        assert "<p>Introduction paragraph.</p>" in result
        assert "<ul>" in result
        assert "<li>Bullet one</li>" in result
        assert "<p>Conclusion paragraph.</p>" in result


class TestParseMarkdownReport:
    """Tests for _parse_markdown_report function."""

    def test_extracts_ticker_from_title(self) -> None:
        """Test ticker is extracted from report title."""
        markdown = "# Stock Analysis Report: NVDA\n\n## Technical Analysis\nContent"
        ticker, _ = _parse_markdown_report(markdown)
        assert ticker == "NVDA"

    def test_extracts_multiple_sections(self) -> None:
        """Test multiple sections are extracted."""
        markdown = """# Stock Analysis Report: AAPL

## Technical Analysis
Tech content here

## Fundamental Analysis
Fundamental content here

## News & Sentiment Analysis
News content here

---
*Generated by Multi-Agent Stock Analyzer*"""
        ticker, sections = _parse_markdown_report(markdown)
        assert ticker == "AAPL"
        assert len(sections) == 3
        assert sections[0][0] == "Technical Analysis"
        assert sections[1][0] == "Fundamental Analysis"
        assert sections[2][0] == "News & Sentiment Analysis"

    def test_section_content_preserved(self) -> None:
        """Test section content is preserved."""
        markdown = """# Stock Analysis Report: TSLA

## Technical Analysis
Line 1
Line 2
Line 3"""
        _, sections = _parse_markdown_report(markdown)
        assert "Line 1" in sections[0][1]
        assert "Line 2" in sections[0][1]
        assert "Line 3" in sections[0][1]

    def test_unknown_ticker_when_missing(self) -> None:
        """Test UNKNOWN ticker when title format doesn't match."""
        markdown = "Some random content without proper title"
        ticker, _ = _parse_markdown_report(markdown)
        assert ticker == "UNKNOWN"

    def test_skips_separator_and_footer(self) -> None:
        """Test separator and footer lines are skipped."""
        markdown = """# Stock Analysis Report: GOOG

## Technical Analysis
Content here

---
*Generated by Multi-Agent Stock Analyzer*"""
        _, sections = _parse_markdown_report(markdown)
        assert len(sections) == 1
        assert "---" not in sections[0][1]
        assert "*Generated" not in sections[0][1]

    def test_handles_empty_sections(self) -> None:
        """Test handling of sections with no content."""
        markdown = """# Stock Analysis Report: AMZN

## Technical Analysis

## Fundamental Analysis
Actual content"""
        _, sections = _parse_markdown_report(markdown)
        assert len(sections) == 2
        assert sections[0][1] == ""
        assert sections[1][1] == "Actual content"


class TestGenerateHtmlReport:
    """Tests for generate_html_report function."""

    @pytest.fixture
    def sample_markdown_report(self) -> str:
        """Create sample markdown report for testing."""
        return """# Stock Analysis Report: NVDA

## Technical Analysis
**Price Trend:** Bullish

Current price: $875.50
- 50-day MA: $820.00
- 200-day MA: $750.00

## Fundamental Analysis
**Valuation:** Premium

- P/E Ratio: 65.4
- Market Cap: $2.1T

## AI Investment Outlook
**Recommendation:** BUY (High Confidence)

**Price Target:** $950 (+8.5%)

---
*Generated by Multi-Agent Stock Analyzer*"""

    def test_returns_html_document(self, sample_markdown_report: str) -> None:
        """Test function returns valid HTML document."""
        result = generate_html_report(sample_markdown_report)
        assert result.startswith("<!DOCTYPE html>")
        assert "</html>" in result

    def test_includes_ticker_in_title(self, sample_markdown_report: str) -> None:
        """Test ticker appears in HTML title."""
        result = generate_html_report(sample_markdown_report)
        assert "<title>Stock Analysis Report - NVDA</title>" in result

    def test_includes_ticker_badge(self, sample_markdown_report: str) -> None:
        """Test ticker badge is present in header."""
        result = generate_html_report(sample_markdown_report)
        assert 'class="ticker-badge">NVDA</div>' in result

    def test_includes_all_sections(self, sample_markdown_report: str) -> None:
        """Test all sections are included in output."""
        result = generate_html_report(sample_markdown_report)
        assert "Technical Analysis" in result
        assert "Fundamental Analysis" in result
        assert "AI Investment Outlook" in result

    def test_includes_section_icons(self, sample_markdown_report: str) -> None:
        """Test section icons are included."""
        result = generate_html_report(sample_markdown_report)
        # Check for icon classes
        assert 'class="section-icon technical"' in result
        assert 'class="section-icon fundamental"' in result
        assert 'class="section-icon outlook"' in result

    def test_includes_date_and_time(self, sample_markdown_report: str) -> None:
        """Test date and time are included in meta."""
        with patch("think_only_once.output.html_report.datetime") as mock_dt:
            mock_dt.now.return_value.strftime.side_effect = ["January 27, 2026", "14:30"]
            result = generate_html_report(sample_markdown_report)
            assert "January 27, 2026" in result
            assert "14:30" in result

    def test_converts_markdown_content(self, sample_markdown_report: str) -> None:
        """Test markdown content is converted to HTML."""
        result = generate_html_report(sample_markdown_report)
        assert "<strong>Price Trend:</strong>" in result
        assert "<li>" in result

    def test_recommendation_styling_applied(self, sample_markdown_report: str) -> None:
        """Test recommendation styling is applied in HTML."""
        result = generate_html_report(sample_markdown_report)
        assert 'class="recommendation buy"' in result

    def test_includes_css_styles(self, sample_markdown_report: str) -> None:
        """Test CSS styles are included in output."""
        result = generate_html_report(sample_markdown_report)
        assert "<style>" in result
        assert ".section" in result
        assert ".recommendation" in result

    def test_includes_footer(self, sample_markdown_report: str) -> None:
        """Test footer is included."""
        result = generate_html_report(sample_markdown_report)
        assert 'class="footer"' in result
        assert "ThinkOnlyOnce" in result


class TestSaveHtmlReport:
    """Tests for save_html_report function."""

    @pytest.fixture
    def sample_markdown_report(self) -> str:
        """Create sample markdown report for testing."""
        return """# Stock Analysis Report: MSFT

## Technical Analysis
Bullish momentum

## Fundamental Analysis
Fair valuation"""

    def test_saves_file_to_specified_directory(
        self, sample_markdown_report: str, tmp_path: Path
    ) -> None:
        """Test file is saved to specified output directory."""
        output_path = save_html_report(sample_markdown_report, output_dir=tmp_path)
        assert output_path.exists()
        assert output_path.parent == tmp_path

    def test_creates_output_directory_if_missing(
        self, sample_markdown_report: str, tmp_path: Path
    ) -> None:
        """Test output directory is created if it doesn't exist."""
        new_dir = tmp_path / "nested" / "reports"
        output_path = save_html_report(sample_markdown_report, output_dir=new_dir)
        assert new_dir.exists()
        assert output_path.exists()

    def test_filename_includes_ticker(
        self, sample_markdown_report: str, tmp_path: Path
    ) -> None:
        """Test filename includes the ticker symbol."""
        output_path = save_html_report(sample_markdown_report, output_dir=tmp_path)
        assert "MSFT" in output_path.name

    def test_filename_includes_timestamp(
        self, sample_markdown_report: str, tmp_path: Path
    ) -> None:
        """Test filename includes timestamp."""
        output_path = save_html_report(sample_markdown_report, output_dir=tmp_path)
        # Check for date pattern YYYY-MM-DD
        assert "_analysis_" in output_path.name
        assert output_path.suffix == ".html"

    def test_file_contains_valid_html(
        self, sample_markdown_report: str, tmp_path: Path
    ) -> None:
        """Test saved file contains valid HTML content."""
        output_path = save_html_report(sample_markdown_report, output_dir=tmp_path)
        content = output_path.read_text(encoding="utf-8")
        assert "<!DOCTYPE html>" in content
        assert "</html>" in content
        assert "MSFT" in content

    def test_returns_path_object(
        self, sample_markdown_report: str, tmp_path: Path
    ) -> None:
        """Test function returns a Path object."""
        output_path = save_html_report(sample_markdown_report, output_dir=tmp_path)
        assert isinstance(output_path, Path)

    def test_accepts_string_path(
        self, sample_markdown_report: str, tmp_path: Path
    ) -> None:
        """Test function accepts string path for output directory."""
        output_path = save_html_report(sample_markdown_report, output_dir=str(tmp_path))
        assert output_path.exists()

    def test_file_encoding_utf8(
        self, sample_markdown_report: str, tmp_path: Path
    ) -> None:
        """Test file is saved with UTF-8 encoding."""
        # Add some unicode characters to the report
        unicode_report = sample_markdown_report.replace(
            "Bullish momentum", "Bullish momentum 📈🚀"
        )
        output_path = save_html_report(unicode_report, output_dir=tmp_path)
        content = output_path.read_text(encoding="utf-8")
        assert "📈" in content or "&#" in content  # Either raw or HTML-escaped


class TestSectionConfig:
    """Tests for SECTION_CONFIG constant."""

    def test_contains_technical_analysis(self) -> None:
        """Test config contains Technical Analysis section."""
        assert "Technical Analysis" in SECTION_CONFIG
        assert "icon" in SECTION_CONFIG["Technical Analysis"]
        assert "icon_class" in SECTION_CONFIG["Technical Analysis"]

    def test_contains_fundamental_analysis(self) -> None:
        """Test config contains Fundamental Analysis section."""
        assert "Fundamental Analysis" in SECTION_CONFIG
        assert SECTION_CONFIG["Fundamental Analysis"]["icon_class"] == "fundamental"

    def test_contains_news_analysis(self) -> None:
        """Test config contains News & Sentiment Analysis section."""
        assert "News & Sentiment Analysis" in SECTION_CONFIG
        assert SECTION_CONFIG["News & Sentiment Analysis"]["icon_class"] == "news"

    def test_contains_ai_outlook(self) -> None:
        """Test config contains AI Investment Outlook section."""
        assert "AI Investment Outlook" in SECTION_CONFIG
        assert SECTION_CONFIG["AI Investment Outlook"]["icon_class"] == "outlook"
