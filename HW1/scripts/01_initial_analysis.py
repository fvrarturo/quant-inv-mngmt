#!/usr/bin/env python3
"""
Run all 17 initial data quality checks. Loads data once, runs each check in order.
"""
import os
import sys
from pathlib import Path

# Paths
SCRIPT_DIR = Path(__file__).resolve().parent
HW1_DIR = SCRIPT_DIR.parent
DATA_PATH = HW1_DIR / "WKKWNT Data Sample (HomeWork #1 15-439).csv"
TREATED_CSV = HW1_DIR / "Treated_datasample.csv"
RESULTS_DIR = HW1_DIR / "results"
FIGURES_DIR = RESULTS_DIR / "figures"

# Writable matplotlib config
os.environ.setdefault("MPLCONFIGDIR", str(HW1_DIR / ".mpl_cache"))
(HW1_DIR / ".mpl_cache").mkdir(exist_ok=True)

sys.path.insert(0, str(HW1_DIR))

import matplotlib
matplotlib.use("Agg")

from src.io import load_data, normalize_columns


def main() -> None:
    if len(sys.argv) > 1:
        data_path = Path(sys.argv[1])
    else:
        data_path = DATA_PATH
    if not data_path.exists():
        print(f"Data file not found: {data_path}")
        sys.exit(1)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    print("Loading data...")
    df = normalize_columns(load_data(data_path))
    df.to_csv(TREATED_CSV, index=False)
    print(f"Loaded {len(df)} rows, {len(df.columns)} columns.")
    print(f"Treated data written to {TREATED_CSV}\n")

    checks = [
        ("1. Null counts", "check_nulls"),
        ("2. Duplicate dates", "check_duplicate_dates"),
        ("3. Duplicate content audit", "check_duplicate_content"),
        ("4. Monotonic dates", "check_monotonic_dates"),
        ("5. Date coverage", "check_date_coverage"),
        ("6. Weekend / holiday", "check_weekend_holiday"),
        ("7. Negative / zero prices", "check_negative_zero_prices"),
        ("8. OHLC bracket", "check_ohlc_bracket"),
        ("9. Adj Close vs Close", "check_adj_vs_close"),
        ("10. Return outliers", "check_return_outliers"),
        ("11. Signal sentinels", "check_signal_sentinels"),
        ("12. Signal z-score", "check_signal_zscore"),
        ("13. Signal day jumps", "check_signal_day_jumps"),
        ("14. Corporate action ratio", "check_corporate_action_ratio"),
        ("15. Schema dtypes", "check_schema_dtypes"),
        ("16. Gaps", "check_gaps"),
        ("17. Issue summary", "check_issue_summary"),
    ]

    for title, mod_name in checks:
        try:
            mod = __import__(f"src.{mod_name}", fromlist=["run"])
            mod.run(df, RESULTS_DIR, FIGURES_DIR)
        except Exception as e:
            print(f"Check failed ({title}): {e}\n")
            import traceback
            traceback.print_exc()

    print("Done. Results in", RESULTS_DIR, "| Figures in", FIGURES_DIR)


if __name__ == "__main__":
    main()
