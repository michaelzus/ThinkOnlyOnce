"""Enums shared across the ThinkOnlyOnce package."""

from enum import StrEnum, auto


class AgentEnum(StrEnum):
    """Agent identifiers used across the graph workflow."""

    ROUTER = auto()
    TECHNICAL_ANALYST = auto()
    FUNDAMENTAL_ANALYST = auto()
    NEWS_ANALYST = auto()
    MACRO_ANALYST = auto()
    INVESTMENT_ANALYST = auto()


class StatusEnum(StrEnum):
    """Status values for agent lifecycle tracking."""

    WAIT = auto()
    RUNNING = auto()
    DONE = auto()
    SKIPPED = auto()
