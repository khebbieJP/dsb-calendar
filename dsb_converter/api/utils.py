"""
Utility functions for DSB ticket conversion
"""

from .constants import DANISH_MONTHS


def parse_danish_month(month_abbr: str) -> int | None:
    """
    Convert Danish month abbreviation to month number.

    Args:
        month_abbr: Danish month abbreviation (e.g., 'jan', 'maj')

    Returns:
        Month number (1-12) or None if not recognized
    """
    return DANISH_MONTHS.get(month_abbr.lower(), None)
