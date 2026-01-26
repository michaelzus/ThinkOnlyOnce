"""Agent definitions for stock analysis."""

from think_only_once.agents.base import get_llm
from think_only_once.agents.investment_analyst import generate_investment_outlook

__all__ = ["get_llm", "generate_investment_outlook"]
