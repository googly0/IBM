# What I checked, and what the agent got wrong

## What the agent got wrong

The agent's first version of `km_wachter.py` floored wear to 0 using `max(0, ...)`, which meant a
car with 14,900 km on a 15,000 km interval showed 0% wear instead of ~99%. I caught it by reading
the diff and noticing the `max` call — it made no logical sense to clip wear at zero, because
negative wear is impossible in practice and the clamp was hiding real readings.

The agent also left `fleet_report.py` crashing on cars that had no `last_service_km` reading.
It was calling `wear_percent` directly on raw odometer math without checking for `None` first.
The fix was to route everything through `car_wear`, which returns `None` for missing readings,
and handle that case in the report rather than crash.

## What I checked before I accepted its work

I ran `python3 verify.py` after each change. For the wear fix specifically, I confirmed that a car
with `odometer=14900` and `last_service_km=0` returns 99.3% — not 0% — from `car_wear`. I also
checked that the constants `SERVICE_INTERVAL_KM = 15000` and `WARN_AT_PERCENT = 80` in
`km_wachter.py` and in `settings.cfg` were both untouched (the verify script checks this too, and
both passed). I ran `python3 analyze.py` to confirm the risk-ranking output looked reasonable
before accepting the analysis code.

## What the data actually said

Three columns actually separated the cars that broke down from those that kept going:
- `km_since_service` (d = 1.06) — by far the strongest signal: broken-down cars averaged ~11,700 km
  since their last service vs ~7,300 km for healthy ones.
- `avg_daily_km` (d = 0.63) — harder-driven cars broke down more.
- `load_factor` (d = 0.53) — heavier loads pushed cars over the edge.

The two columns that looked obvious but were not:
- `odometer_km` — both groups averaged almost exactly 53,300 km. Total mileage tells you nothing.
- `age_years` — both groups averaged ~5.9 years. Age alone is not the problem.

The combined risk score reaches AUC 0.85 (85% chance it ranks a broken-down car above a healthy
one). Odometer alone is effectively a coin flip (0.49). The lesson: it is wear-since-last-service
and how hard the car is being worked that matter, not how old or how many total km it has.
