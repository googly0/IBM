"""Small formatting and unit helpers for the fleet report."""

KM_PER_MILE = 1.609344


def km_to_miles(km: float) -> float:
    """Convert kilometres to miles (used for the UK partner report)."""
    return km / KM_PER_MILE


def format_number(value: float) -> str:
    """Format a number with one decimal place."""
    return f"{value:.1f}"
