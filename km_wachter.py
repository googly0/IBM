"""KM-Waechter: decides when a Vossberg Mobility car needs a service."""

SERVICE_INTERVAL_KM = 15000
WARN_AT_PERCENT = 80


def wear_percent(km_since_service: float, interval: float) -> float:
    """Return how much of the service window has been used, as a percentage."""
    return km_since_service / interval * 100


def car_wear(car: dict) -> float | None:
    """Return a car's wear percentage, or None if it has no last-service reading."""
    last = car.get("last_service_km")
    if last is None:
        return None
    return wear_percent(car["odometer"] - last, SERVICE_INTERVAL_KM)


def needs_service(car: dict) -> bool:
    """Return True if the car has used at least WARN_AT_PERCENT of its service window.

    A car with no last-service reading is not flagged: its wear is unknown, not 100%.
    """
    wear = car_wear(car)
    return wear is not None and wear >= WARN_AT_PERCENT


def check_fleet(fleet: list[dict]) -> list[str]:
    """Print and return the ids of every car that is due for service."""
    flagged = [car["id"] for car in fleet if needs_service(car)]
    for car_id in flagged:
        print(f"SERVICE DUE: {car_id}")
    return flagged
