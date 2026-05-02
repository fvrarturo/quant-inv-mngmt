#!/usr/bin/env python3
"""
Problem 1: joint per-stock time-series regression on the 5 factors.

For each stock i, fits r_i(t) = B_i F(t) + eps_i(t) (no intercept, per the
formula in the handout: eps = R - BF). Saves:
  - results/01_B_loadings.csv      (n x 5)
  - results/01_R_returns.csv       (n x T), pivoted returns matrix
  - results/01_regression_stats.csv  per-stock R^2 and residual variance
  - results/figures/01_actual_vs_fitted_{mrap_id}.png for 8568, 39541
  - results/figures/01_cumulative_factor_returns.png
  - md_files/01_loadings.md summary
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

HW5 = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HW5))

from src.io import FACTOR_COLS, build_returns_matrix, load_factors, load_panel
from src.plotting import actual_vs_fitted, cumulative_returns
from src.regression import fit_loadings, fitted_and_residuals

RESULTS = HW5 / "results"
FIGURES = RESULTS / "figures"
MD = HW5 / "md_files"

TARGETS = [8568, 39541]


def per_stock_stats(R_df: pd.DataFrame, eps_df: pd.DataFrame) -> pd.DataFrame:
    stats = []
    for mid in R_df.index:
        r = R_df.loc[mid].to_numpy(dtype=float)
        e = eps_df.loc[mid].to_numpy(dtype=float)
        mask = ~np.isnan(r)
        r_ = r[mask]
        e_ = e[mask]
        if len(r_) < 10:
            stats.append((mid, np.nan, np.nan, np.nan, len(r_)))
            continue
        ss_res = float(np.sum(e_ ** 2))
        ss_tot = float(np.sum((r_ - r_.mean()) ** 2))
        r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else np.nan
        stats.append((mid, r2, float(np.std(e_, ddof=0)), float(np.mean(e_)), len(r_)))
    return pd.DataFrame(stats, columns=["mrap_id", "r_squared", "resid_std", "resid_mean", "n_obs"])


def main() -> None:
    RESULTS.mkdir(exist_ok=True)
    FIGURES.mkdir(exist_ok=True)
    MD.mkdir(exist_ok=True)

    panel = load_panel()
    factors = load_factors()
    R_df, F, dates = build_returns_matrix(panel, factors)

    print(f"R shape: {R_df.shape}; F shape: {F.shape}")

    print("Fitting per-stock OLS (no intercept) on 5 factors ...")
    B_df = fit_loadings(R_df, F)
    print(f"B shape: {B_df.shape}. First few rows:\n{B_df.head()}")

    Rhat_df, eps_df = fitted_and_residuals(R_df, F, B_df)

    # Save core matrices.
    B_df.to_csv(RESULTS / "01_B_loadings.csv")
    R_df.to_csv(RESULTS / "01_R_returns.csv")
    Rhat_df.to_csv(RESULTS / "01_Rhat_fitted.csv")
    eps_df.to_csv(RESULTS / "01_eps_residuals.csv")

    stats = per_stock_stats(R_df, eps_df)
    stats.to_csv(RESULTS / "01_regression_stats.csv", index=False)

    # Actual vs fitted plots for requested IDs.
    for mid in TARGETS:
        if mid not in R_df.index:
            print(f"mrap_id {mid} missing from R_df — skipping plot")
            continue
        actual = R_df.loc[mid].to_numpy(dtype=float)
        fitted = Rhat_df.loc[mid].to_numpy(dtype=float)
        actual_vs_fitted(
            dates,
            actual,
            fitted,
            title=f"MRAP {mid}: actual vs fitted monthly return (5-factor model)",
            path=FIGURES / f"01_actual_vs_fitted_{mid}.png",
        )

    # Cumulative factor returns plot.
    fac_df = factors.set_index("date")[FACTOR_COLS]
    cumulative_returns(
        factors["date"].to_numpy(),
        fac_df.reset_index(drop=True),
        FIGURES / "01_cumulative_factor_returns.png",
        title="Cumulative factor returns (compounded)",
    )

    # Per-factor mean/std.
    fac_summary = pd.DataFrame(
        {
            "mean_monthly": fac_df.mean(),
            "std_monthly": fac_df.std(ddof=0),
            "annual_mean": fac_df.mean() * 12,
            "annual_vol": fac_df.std(ddof=0) * np.sqrt(12),
            "total_return": (1 + fac_df).prod() - 1,
        }
    )
    fac_summary.to_csv(RESULTS / "01_factor_summary.csv")

    print("median R^2:", stats["r_squared"].median())
    print("mean R^2:", stats["r_squared"].mean())

    # Markdown summary.
    md = [
        "# Problem 1 — factor loadings",
        "",
        "For each of the 1 000 stocks we fit the no-intercept OLS",
        "$r_i(t) = B_i F(t) + \\varepsilon_i(t)$ on the 108 monthly observations the",
        "stock is present (some names have < 108 months because of entry/exit).",
        "",
        f"- Loadings matrix `B` shape: {B_df.shape}",
        f"- Median per-stock $R^2$: {stats['r_squared'].median():.3f}",
        f"- Mean per-stock $R^2$:   {stats['r_squared'].mean():.3f}",
        "",
        "## Loadings summary (mean and std across stocks)",
        "",
        "| factor | mean | std |",
        "|---|---|---|",
    ]
    for col in B_df.columns:
        md.append(f"| {col} | {B_df[col].mean():.4f} | {B_df[col].std(ddof=0):.4f} |")
    md += [
        "",
        "## Factor cumulative / annualised stats",
        "",
        "See `results/01_factor_summary.csv`. Plot in `results/figures/01_cumulative_factor_returns.png`.",
        "",
        "## Actual vs fitted plots",
        "",
        "- MRAP 8568:  `results/figures/01_actual_vs_fitted_8568.png`",
        "- MRAP 39541: `results/figures/01_actual_vs_fitted_39541.png`",
        "",
    ]
    (MD / "01_loadings.md").write_text("\n".join(md), encoding="utf-8")
    print("wrote md_files/01_loadings.md")


if __name__ == "__main__":
    main()
