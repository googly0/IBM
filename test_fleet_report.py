# test_fleet_report.py
import pytest

from fleet_report import fleet_summary

SAMPLE = [
    {"id": "VOS-4471", "odometer": 14900, "last_service_km": 0},
    {"id": "VOS-2210", "odometer": 48400, "last_service_km": 45000},
]


def test_summary_counts_due_cars():
    # Only VOS-4471 is nearly worn, so exactly one car is due.
    assert fleet_summary(SAMPLE)["due"] == 1


def test_car_without_reading_does_not_crash_the_report():
    # VOS-7788 has no "last_service_km" reading. The report must still run, must not count it
    # as due, and must leave it out of the average instead of treating it as 0 km or fully worn.
    fleet = SAMPLE + [{"id": "VOS-7788", "odometer": 92000}]
    summary = fleet_summary(fleet)
    assert summary["count"] == 3
    assert summary["due"] == 1
    assert summary["missing_reading"] == 1
    assert summary["average_wear"] == pytest.approx(fleet_summary(SAMPLE)["average_wear"])


def test_average_wear_is_not_floored():
    fleet = [
        {"id": "A", "odometer": 14900, "last_service_km": 0},
        {"id": "B", "odometer": 3000, "last_service_km": 0},
    ]
    assert fleet_summary(fleet)["average_wear"] == pytest.approx(59.667, abs=0.01)


def test_empty_fleet_does_not_crash():
    assert fleet_summary([]) == {"count": 0, "due": 0, "missing_reading": 0, "average_wear": 0.0}
