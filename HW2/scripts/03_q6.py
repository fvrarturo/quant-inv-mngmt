#!/usr/bin/env python3
"""
Q6: Trailing returns (i–vi), forward returns (F1M, F3M, F6M); one time series graph per variable
    with Percentile Sets; median of each percentile over time.
"""
import os
import re
import sys
from pathlib import Path

import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parent
HW2_DIR = SCRIPT_DIR.parent
os.environ.setdefault("MPLCONFIGDIR", str(HW2_DIR / ".mpl_cache"))
(HW2_DIR / ".mpl_cache").mkdir(exist_ok=True)
DATA_PATH = HW2_DIR / "SP500Raw.xlsx"
RESULTS_DIR = HW2_DIR / "results"
FIGURES_DIR = RESULTS_DIR / "figures"
MD_DIR = HW2_DIR / "md_files"
PANEL_PATH = RESULTS_DIR / "full_panel.csv"

sys.path.insert(0, str(HW2_DIR))

from src.io import load_sp500
from src.returns import build_full_panel
from src.percentiles import (
    percentile_series_by_date,
    plot_percentile_timeseries,
    median_of_percentiles,
    PERCENTILE_LABELS,
)

# All variables for Percentile Sets (column names in panel)
Q6_VARS = [
    "Price_Ret_T1",
    "PRC_Ret_T12",
    "Prices_Ret_T12",
    "PRC_Ret_T12M1",
    "Prices_Ret_T12M1",
    "PRC_Ret_T12_1M",
    "Prices_Ret_T12_1M",
    "Vol_Prices_Ret_T12M1",
    "SR_Prices_Ret_T12M1",
    "PRC_Ret_F1M",
    "PRC_Ret_F3M",
    "PRC_Ret_F6M",
]


def _safe_filename(name: str) -> str:
    return re.sub(r"[^\w\-]", "_", name)


def main() -> None:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else DATA_PATH
    if not path.exists():
        print(f"Data file not found: {path}")
        sys.exit(1)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    MD_DIR.mkdir(parents=True, exist_ok=True)

    print("Loading and building full panel...")
    df = load_sp500(path)
    panel = build_full_panel(df)
    panel.to_csv(PANEL_PATH, index=False)
    print(f"Full panel saved to {PANEL_PATH}")

    median_rows = []
    for var in Q6_VARS:
        if var not in panel.columns:
            print(f"  Skip {var} (missing)")
            continue
        series_by_date = percentile_series_by_date(panel, var, "date")
        plot_percentile_timeseries(
            series_by_date,
            f"{var} — Percentile Sets",
            FIGURES_DIR / f"{_safe_filename(var)}_percentiles.png",
        )
        med = median_of_percentiles(series_by_date)
        median_rows.append({"variable": var, **med.to_dict()})
        print(f"  {var}: plot and medians done")

    table = pd.DataFrame(median_rows)
    table = table.set_index("variable")
    table.to_csv(RESULTS_DIR / "q6_median_of_percentiles.csv")
    print(f"Median-of-percentiles table saved to results/q6_median_of_percentiles.csv")

    notes = f"""# Q6 notes

## Variables

{chr(10).join('- ' + v for v in Q6_VARS)}

## Outputs

- **Full panel (cached):** `results/full_panel.csv`
- **Plots:** `results/figures/<var>_percentiles.png` for each variable
- **Median of each percentile (over time):** `results/q6_median_of_percentiles.csv`
"""
    (MD_DIR / "Q6_notes.md").write_text(notes, encoding="utf-8")
    print("Wrote md_files/Q6_notes.md")


if __name__ == "__main__":
    main()
