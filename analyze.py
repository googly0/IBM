# analyze.py
# SUMMARY: km_since_service, load_factor and avg_daily_km predict a breakdown; odometer_km and
# age_years do not (both groups average ~53,000 km and ~5.9 years). Wear AND how hard a car is worked.
#
# The 80% rule only warns once a car is nearly worn. This ranks cars by how likely they are to
# break down SOON, from fleet_history.csv (120 cars; broke_down = 1 means it later broke down),
# so the fleet team can fix the risky ones first.
#
# Method, no machine learning: split the cars into broke down / kept going, and compare the two
# groups column by column with a standardised gap (Cohen's d: difference in means divided by the
# pooled spread). Columns whose gap is large enough are standardised to z-scores and combined,
# each weighted by its gap, then scaled to a 0-100 risk score.

import pandas as pd

from km_wachter import SERVICE_INTERVAL_KM, WARN_AT_PERCENT

HISTORY_FILE = "fleet_history.csv"
TARGET = "broke_down"
MIN_GAP = 0.5            # |d| >= 0.5 is a "medium" effect; below that a column says too little


def group_gaps(df: pd.DataFrame) -> pd.DataFrame:
    """Compare broke-down and kept-going cars column by column."""
    features = df.drop(columns=["car_id", TARGET])
    broke, kept = features[df[TARGET] == 1], features[df[TARGET] == 0]
    pooled_sd = ((broke.var() * (len(broke) - 1) + kept.var() * (len(kept) - 1))
                 / (len(broke) + len(kept) - 2)) ** 0.5
    gaps = pd.DataFrame({
        "broke_down": broke.mean(),
        "kept_going": kept.mean(),
        "gap_d": (broke.mean() - kept.mean()) / pooled_sd,
    })
    return gaps.sort_values("gap_d", key=abs, ascending=False)


def risk_scores(df: pd.DataFrame, weights: pd.Series) -> pd.Series:
    """Weighted sum of z-scores over the predictive columns, scaled to 0-100."""
    z = (df[weights.index] - df[weights.index].mean()) / df[weights.index].std()
    raw = (z * weights).sum(axis=1)
    return ((raw - raw.min()) / (raw.max() - raw.min()) * 100).round(1)


def ranking_quality(score: pd.Series, outcome: pd.Series) -> float:
    """Chance that a random broke-down car scores above a random kept-going car (AUC)."""
    broke, kept = score[outcome == 1], score[outcome == 0]
    wins = sum((b > kept).sum() + 0.5 * (b == kept).sum() for b in broke)
    return wins / (len(broke) * len(kept))


def main() -> None:
    df = pd.read_csv(HISTORY_FILE)
    gaps = group_gaps(df)
    print(f"{len(df)} cars, {df[TARGET].sum()} broke down.\n")
    print("Broke down vs kept going (mean per group, standardised gap d):")
    print(gaps.round(2).to_string(), "\n")

    predictive = gaps[gaps["gap_d"].abs() >= MIN_GAP]
    print(f"Columns that separate the groups (|d| >= {MIN_GAP}): {', '.join(predictive.index)}")
    print(f"Columns that do not: {', '.join(gaps.index.difference(predictive.index))}\n")

    df["risk"] = risk_scores(df, predictive["gap_d"])
    df["wear_pct"] = (df["km_since_service"] / SERVICE_INTERVAL_KM * 100).round(0)
    df["rule_flags"] = df["wear_pct"] >= WARN_AT_PERCENT
    print(f"Ranking quality (AUC): risk score {ranking_quality(df['risk'], df[TARGET]):.2f}, "
          f"km_since_service alone {ranking_quality(df['km_since_service'], df[TARGET]):.2f}, "
          f"odometer_km alone {ranking_quality(df['odometer_km'], df[TARGET]):.2f} (0.5 = coin flip)")

    top = df.nlargest(len(df) // 4, "risk")
    early = top[~top["rule_flags"]]
    print(f"Top quarter by risk: {len(top)} cars, {top[TARGET].sum()} of which broke down; "
          f"{len(early)} of them the 80% rule does not flag yet.\n")

    columns = ["car_id", "risk", "wear_pct", "rule_flags", *predictive.index, TARGET]
    print("Cars ranked by risk, highest first:")
    print(df.sort_values("risk", ascending=False)[columns].to_string(index=False))


if __name__ == "__main__":
    main()
