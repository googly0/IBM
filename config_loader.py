"""Reads settings.cfg, a flat file of "key = value" lines with # comments."""

import warnings

SETTINGS_FILE = "settings.cfg"

KNOWN_KEYS = {
    "service_interval_km",
    "warn_at_percent",
    "report_title",
    "history_file",
    "log_file",
    "mileage_unit",
}


def load_settings(path: str = SETTINGS_FILE) -> dict[str, str]:
    """Return the known settings as strings. Unknown keys and broken lines raise a warning."""
    settings = {}
    with open(path, encoding="utf-8") as f:
        for number, raw in enumerate(f, start=1):
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                warnings.warn(f"{path}:{number}: ignoring line without '=': {line!r}")
                continue
            key, value = (part.strip() for part in line.split("=", 1))
            if key not in KNOWN_KEYS:
                warnings.warn(f"{path}:{number}: ignoring unknown key {key!r} (typo?)")
                continue
            settings[key] = value
    return settings


def get_int(settings: dict[str, str], key: str, fallback: int) -> int:
    """Return settings[key] as an int, or fallback if it is missing or not a number."""
    try:
        return int(settings[key])
    except (KeyError, ValueError):
        return fallback
