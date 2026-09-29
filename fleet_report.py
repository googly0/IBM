"""Prints the nightly fleet-health summary for Vossberg Mobility."""

from km_wachter import car_wear, needs_service
from config_loader import load_settings
from log_util import log, flush_log
import fleet_utils


def fleet_summary(fleet: list[dict]) -> dict:
    """Count the cars, the cars due for service, and the average wear.

    Cars with no last-service reading are left out of the average (their wear is
    unknown) and counted separately under "missing_reading".
    """
    wears = [w for w in (car_wear(car) for car in fleet) if w is not None]
    average = sum(wears) / len(wears) if wears else 0.0
    return {
        "count": len(fleet),
        "due": sum(needs_service(car) for car in fleet),
        "missing_reading": len(fleet) - len(wears),
        "average_wear": average,
    }


def print_report(fleet: list[dict]) -> None:
    """Print the nightly report and append the log lines to the log file."""
    settings = load_settings()
    log(settings.get("report_title", "Nightly fleet report"))
    s = fleet_summary(fleet)
    print(f"Fleet: {s['count']} cars")
    print(f"Due for service: {s['due']}")
    print(f"No last-service reading: {s['missing_reading']}")
    print(f"Average wear: {s['average_wear']:.1f}%")
    total_km = sum(car["odometer"] for car in fleet)
    # The partner garage in England wants the distance in miles (since 2015).
    miles = fleet_utils.format_number(fleet_utils.km_to_miles(total_km))
    print(f"Fleet distance: {miles} miles")
    flush_log(settings.get("log_file", "km_wachter.log"))
