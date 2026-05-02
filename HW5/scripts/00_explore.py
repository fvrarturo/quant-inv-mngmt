#!/usr/bin/env python3
"""
Quick exploration of the three HW5 inputs. Writes a short markdown summary and
a few sanity-check CSVs under results/.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

HW5 = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HW5))

from src.io import (
    build_returns_matrix,
    load_estimates,
    load_factors,
    load_panel,
)

RESULTS = HW5 / "results"
MD = HW5 / "md_files"


def main() -> None:
    RESULTS.mkdir(exist_ok=True)
    MD.mkdir(exist_ok=True)

    panel = load_panel()
    factors = load_factors()
    estimates = load_estimates()

    R_df, F, dates = build_returns_matrix(panel, factors)

    months_per_stock = panel.groupby("mrap_id").size()
    n_full = int((months_per_stock == factors.shape[0]).sum())
    n_partial = int((months_per_stock < factors.shape[0]).sum())

    sector_counts = estimates["sector"].value_counts().sort_index()

    summary = {
        "panel_rows": len(panel),
        "panel_cols": list(panel.columns),
        "n_mrap_ids": panel["mrap_id"].nunique(),
        "n_dates": panel["date"].nunique(),
        "first_date": str(panel["date"].min()),
        "last_date": str(panel["date"].max()),
        "n_factors": 5,
        "n_full_stocks": n_full,
        "n_partial_stocks": n_partial,
        "returns_matrix_shape": tuple(R_df.shape),
        "factor_matrix_shape": tuple(F.shape),
        "estimates_rows": len(estimates),
        "n_sectors": estimates["sector"].nunique(),
    }

    for k, v in summary.items():
        print(f"{k:30s} {v}")

    out = pd.Series(summary).rename("value").to_frame()
    out.to_csv(RESULTS / "00_summary.csv")
    sector_counts.to_csv(RESULTS / "00_sector_counts.csv", header=["n_stocks"])

    md = [
        "# HW5 data exploration",
        "",
        "## Panel (`data.xlsx`)",
        "",
        f"- rows: {len(panel):,}",
        f"- unique `mrap_id`: {panel['mrap_id'].nunique()}",
        f"- unique dates: {panel['date'].nunique()} ({panel['date'].min().date()} → {panel['date'].max().date()})",
        f"- stocks with full 108-month history: {n_full}",
        f"- stocks with partial history: {n_partial}",
        "",
        "## Factors (`factors.xlsx`)",
        "",
        f"- 5 factor columns + risk-free rate, {factors.shape[0]} monthly observations.",
        "",
        "## Estimates (`estimates.xlsx`)",
        "",
        f"- rows: {len(estimates)}; Jan 2041 snapshot with realized `ret` and predicted `pred`.",
        f"- sectors (first two NAICS digits): {estimates['sector'].nunique()} unique sectors.",
        "",
        "See `results/00_sector_counts.csv` for the sector distribution.",
        "",
    ]
    (MD / "00_explore.md").write_text("\n".join(md), encoding="utf-8")
    print("wrote md_files/00_explore.md")


if __name__ == "__main__":
    main()
