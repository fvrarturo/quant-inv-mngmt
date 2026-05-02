#!/usr/bin/env python3
"""
Exploratory analysis of SP500Raw.xlsx.
Loads data via src.io, reports shape, dtypes, date range, nulls,
companies per date, unique permnos, and companies present over entire sample.
Writes summary to results/ and md_files/.
"""
import sys
from pathlib import Path

import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parent
HW2_DIR = SCRIPT_DIR.parent
DATA_PATH = HW2_DIR / "SP500Raw.xlsx"
RESULTS_DIR = HW2_DIR / "results"
MD_DIR = HW2_DIR / "md_files"

sys.path.insert(0, str(HW2_DIR))

from src.io import load_sp500


def main() -> None:
    data_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DATA_PATH
    if not data_path.exists():
        print(f"Data file not found: {data_path}")
        sys.exit(1)

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    MD_DIR.mkdir(parents=True, exist_ok=True)

    print("Loading SP500Raw.xlsx...")
    df = load_sp500(data_path)
    print(f"Loaded {len(df):,} rows, {len(df.columns)} columns.\n")

    # --- Basic info ---
    print("=" * 60)
    print("BASIC INFO")
    print("=" * 60)
    print("Columns:", list(df.columns))
    print("\nDtypes:")
    print(df.dtypes)
    print("\nNull counts:")
    nulls = df.isnull().sum()
    for c in df.columns:
        print(f"  {c}: {nulls[c]:,}")

    # --- Date range ---
    dates = pd.to_datetime(df["date"], errors="coerce").dropna()
    print("\nDate range:", dates.min(), "to", dates.max())
    print("Unique dates:", df["date"].nunique())

    # --- Companies per date ---
    n_per_date = df.groupby("date").size()
    print("\nCompanies per date:")
    print("  min:", int(n_per_date.min()), "  max:", int(n_per_date.max()))
    print("  mean: {:.1f}  median: {:.0f}".format(n_per_date.mean(), n_per_date.median()))
    n_per_date.to_csv(RESULTS_DIR / "companies_per_date.csv", header=["n_companies"])

    # --- Unique companies ---
    all_permnos = set(df["permno"].dropna().astype(int))
    n_unique = len(all_permnos)
    print("\nUnique PERMNOs (companies) in sample:", n_unique)

    # Companies present in every month
    n_dates = df["date"].nunique()
    permno_date_counts = df.groupby("permno")["date"].nunique()
    full_sample_permnos = permno_date_counts[permno_date_counts >= n_dates].index.tolist()
    n_full = len(full_sample_permnos)
    print("Companies present in every month (full sample):", n_full)

    # --- Numeric summaries ---
    print("\nNumeric summaries (raw):")
    print(df[["price", "shrout", "prc", "mcap"]].describe().to_string())

    # --- Price vs PRC sanity (preview for Q2) ---
    df_sorted = df.sort_values(["permno", "date"])
    df_sorted["price_lag"] = df_sorted.groupby("permno")["price"].shift(1)
    df_sorted["price_ret_t1"] = (df_sorted["price"] / df_sorted["price_lag"]) - 1
    diff = (df_sorted["price_ret_t1"] - df_sorted["prc"]).abs()
    print("\nPrice_Ret(T1) vs PRC (preview for Q2):")
    print("  Rows with both valid:", (df_sorted["price_ret_t1"].notna() & df_sorted["prc"].notna()).sum())
    print("  Rows where equal (within 1e-6):", (diff < 1e-6).sum())
    print("  Rows where different:", (diff >= 1e-6).sum())

    # --- Save summary for md ---
    summary = {
        "n_rows": len(df),
        "n_columns": len(df.columns),
        "date_min": str(dates.min()),
        "date_max": str(dates.max()),
        "n_unique_dates": int(df["date"].nunique()),
        "n_unique_permno": n_unique,
        "n_permno_full_sample": n_full,
        "n_companies_min_per_date": int(n_per_date.min()),
        "n_companies_max_per_date": int(n_per_date.max()),
        "n_companies_median_per_date": int(n_per_date.median()),
    }
    summary_df = pd.DataFrame([summary])
    summary_df.T.to_csv(RESULTS_DIR / "explore_summary.csv", header=["value"])
    print("\nSummary saved to results/explore_summary.csv")

    # --- Update md ---
    md_path = MD_DIR / "explore_data.md"
    md_lines = [
        "# Data exploration: SP500Raw.xlsx",
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "|--------|-------|",
    ]
    for k, v in summary.items():
        md_lines.append(f"| {k} | {v} |")
    md_lines.extend([
        "",
        "## Columns",
        "",
        "- **permno**: identifier (CRSP permanent number)",
        "- **date**: month-end date",
        "- **price**: average of bid/ask at close",
        "- **shrout**: shares outstanding (000's)",
        "- **prc**: total return from prior period (e.g. prior month return)",
        "- **mcap**: market cap (000's)",
        "",
        "## Companies per date",
        "",
        f"Count of constituents per month: min={n_per_date.min()}, max={n_per_date.max()}, median={n_per_date.median():.0f}. "
        "Not always 500 due to index reconstitution and data availability.",
        "",
        "## Outputs",
        "",
        "- `results/companies_per_date.csv`: number of companies per date",
        "- `results/explore_summary.csv`: one-row summary of exploration",
        "",
    ])
    md_path.write_text("\n".join(md_lines), encoding="utf-8")
    print(f"Markdown written to {md_path}")

    print("\nDone.")


if __name__ == "__main__":
    main()
