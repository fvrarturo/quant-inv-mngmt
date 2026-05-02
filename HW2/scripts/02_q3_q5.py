#!/usr/bin/env python3
"""
Q3: Count companies per date; why not always 500?
Q4: Companies present over entire sample; unique companies.
Q5: Percentile sets (max, 95, 75, median, 25, 5, min) of mcap by date;
    5a: month prior to leaving; 5b: month of entry.
"""
import os
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
HW2_DIR = SCRIPT_DIR.parent
os.environ.setdefault("MPLCONFIGDIR", str(HW2_DIR / ".mpl_cache"))
(HW2_DIR / ".mpl_cache").mkdir(exist_ok=True)
DATA_PATH = HW2_DIR / "SP500Raw.xlsx"
RESULTS_DIR = HW2_DIR / "results"
FIGURES_DIR = RESULTS_DIR / "figures"
MD_DIR = HW2_DIR / "md_files"

sys.path.insert(0, str(HW2_DIR))

from src.io import load_sp500
from src.percentiles import (
    percentile_series_by_date,
    plot_percentile_timeseries,
    panel_entry_exit_dates,
    subset_month_before_exit,
    subset_month_of_entry,
    percentile_set_cross_section,
    PERCENTILE_LABELS,
)


def main() -> None:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else DATA_PATH
    if not path.exists():
        print(f"Data file not found: {path}")
        sys.exit(1)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    MD_DIR.mkdir(parents=True, exist_ok=True)

    df = load_sp500(path)

    # Q3 / Q4
    n_per_date = df.groupby("date").size()
    n_dates = df["date"].nunique()
    permno_dates = df.groupby("permno")["date"].nunique()
    full_sample = permno_dates[permno_dates >= n_dates].index.tolist()
    print("Q3: Companies per date — min:", n_per_date.min(), "max:", n_per_date.max())
    print("Q4: Unique PERMNOs:", df["permno"].nunique(), "| Full sample (all months):", len(full_sample))

    # Q5: mcap percentile time series (all dates)
    by_date = percentile_series_by_date(df, "mcap", "date")
    by_date.to_csv(RESULTS_DIR / "mcap_percentiles_by_date.csv")
    plot_percentile_timeseries(
        by_date,
        "Market cap percentile set by date",
        FIGURES_DIR / "mcap_percentiles_by_date.png",
    )
    print("Q5: mcap percentile series and plot saved.")

    # Q5a / Q5b: entry and exit subsets
    entry_exit = panel_entry_exit_dates(df, "date")
    month_before_exit = subset_month_before_exit(df, entry_exit, "date")
    month_of_entry = subset_month_of_entry(df, entry_exit, "date")

    pct_before_exit = percentile_set_cross_section(month_before_exit, "mcap")
    pct_of_entry = percentile_set_cross_section(month_of_entry, "mcap")
    pct_before_exit.to_csv(RESULTS_DIR / "mcap_percentiles_month_before_exit.csv", header=["mcap"])
    pct_of_entry.to_csv(RESULTS_DIR / "mcap_percentiles_month_of_entry.csv", header=["mcap"])
    print("Q5a: mcap percentiles (month prior to leaving) saved.")
    print("Q5b: mcap percentiles (month of entry) saved.")

    # Q3_Q5_notes.md
    notes = f"""# Q3–Q5 notes

## Q3: Why is the number of companies not always 500?

The S&P 500 is reconstituted periodically; constituents are added and removed. Data may also have more than 500 names in some months (e.g. 506) due to timing of additions and deletions. So the count varies (min={n_per_date.min()}, max={n_per_date.max()} in this sample).

## Q4: Unique and full-sample companies

- **Unique PERMNOs in sample:** {df["permno"].nunique()}
- **Companies present in every month (full sample):** {len(full_sample)}

## Q5: Percentile sets

- **Main time series:** `results/mcap_percentiles_by_date.csv`, `results/figures/mcap_percentiles_by_date.png`
- **Month prior to leaving:** `results/mcap_percentiles_month_before_exit.csv`
- **Month of entry:** `results/mcap_percentiles_month_of_entry.csv`
"""
    (MD_DIR / "Q3_Q5_notes.md").write_text(notes, encoding="utf-8")
    print("Wrote md_files/Q3_Q5_notes.md")


if __name__ == "__main__":
    main()
