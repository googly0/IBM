# test_helpers.py — guards for the quiet bugs in the helper modules.
import pytest

import km_wachter
from config_loader import get_int, load_settings
from fleet_utils import km_to_miles


def test_km_to_miles():
    assert km_to_miles(100) == pytest.approx(62.137, abs=0.01)


def test_settings_cfg_matches_the_rules_in_code():
    # km_wachter.py and settings.cfg each carry the rule values. They must never drift apart.
    settings = load_settings()
    assert get_int(settings, "service_interval_km", -1) == km_wachter.SERVICE_INTERVAL_KM == 15000
    assert get_int(settings, "warn_at_percent", -1) == km_wachter.WARN_AT_PERCENT == 80


def test_value_containing_equals_sign_is_kept_whole(tmp_path):
    cfg = tmp_path / "s.cfg"
    cfg.write_text("report_title = Fleet a=b report\n")
    assert load_settings(str(cfg))["report_title"] == "Fleet a=b report"


def test_unknown_key_is_reported_not_silently_dropped(tmp_path):
    cfg = tmp_path / "s.cfg"
    cfg.write_text("warn_at_precent = 80\n")
    with pytest.warns(UserWarning, match="warn_at_precent"):
        assert load_settings(str(cfg)) == {}
