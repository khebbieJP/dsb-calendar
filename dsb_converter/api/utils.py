"""
Utility functions for DSB ticket conversion
"""


def parse_danish_month(month_abbr: str) -> int | None:
    """
    Convert Danish month abbreviation to month number.

    Args:
        month_abbr: Danish month abbreviation (e.g., 'jan', 'maj')

    Returns:
        Month number (1-12) or None if not recognized
    """
    months = {
        'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4,
        'maj': 5, 'jun': 6, 'jul': 7, 'aug': 8,
        'sep': 9, 'okt': 10, 'nov': 11, 'dec': 12
    }
    return months.get(month_abbr.lower(), None)
