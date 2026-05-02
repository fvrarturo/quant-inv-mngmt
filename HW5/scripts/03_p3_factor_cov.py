#!/usr/bin/env python3
"""
Problem 3: factor covariance and correlation heatmap.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

HW5 = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HW5))

from src.covariance import correlation_from_covariance, factor_covariance
from src.io import FACTOR_COLS, load_factors
from src.plotting import corr_heatmap

RESULTS = HW5 / "results"
FIGURES = RESULTS / "figures"
MD = HW5 / "md_files"


def main() -> None:
    RESULTS.mkdir(exist_ok=True)
    FIGURES.mkdir(exist_ok=True)
    MD.mkdir(exist_ok=True)

    factors = load_factors()
    F = factors[FACTOR_COLS].to_numpy().T  # 5 x T

    Omega_F = factor_covariance(F, demean=False)  # as per problem statement
    Omega_F_demeaned = factor_covariance(F, demean=True)  # reported for reference

    corr_F = correlation_from_covariance(Omega_F)
    corr_F_demeaned = correlation_from_covariance(Omega_F_demeaned)

    pd.DataFrame(Omega_F, index=FACTOR_COLS, columns=FACTOR_COLS).to_csv(
        RESULTS / "03_omega_F.csv"
    )
    pd.DataFrame(corr_F, index=FACTOR_COLS, columns=FACTOR_COLS).to_csv(
        RESULTS / "03_corr_F.csv"
    )

    corr_heatmap(
        corr_F,
        FACTOR_COLS,
        path=FIGURES / "03_corr_factors.png",
        title="Correlation of factor returns (Ω_F = E[FFᵀ])",
    )
    corr_heatmap(
        corr_F_demeaned,
        FACTOR_COLS,
        path=FIGURES / "03_corr_factors_demeaned.png",
        title="Correlation of factor returns (sample covariance)",
    )

    # Find the most correlated pair (off-diagonal, |rho|).
    abs_corr = np.abs(corr_F.copy())
    np.fill_diagonal(abs_corr, 0.0)
    i, j = np.unravel_index(np.argmax(abs_corr), abs_corr.shape)
    best_pair = (FACTOR_COLS[i], FACTOR_COLS[j], float(corr_F[i, j]))
    print(f"most correlated pair (|ρ|): {best_pair[0]}/{best_pair[1]} ρ = {best_pair[2]:.3f}")

    def df_to_md(df: pd.DataFrame, ndigits: int = 3) -> str:
        header = "| | " + " | ".join(df.columns) + " |"
        sep = "|---" * (len(df.columns) + 1) + "|"
        rows = [f"| {idx} | " + " | ".join(f"{v:.{ndigits}f}" for v in row) + " |"
                for idx, row in df.iterrows()]
        return "\n".join([header, sep, *rows])

    md = [
        "# Problem 3 — factor covariance",
        "",
        "Ω_F = E[FFᵀ]  (as defined in the handout).",
        "Correlation derived with σ_i = √Ω_F[i,i].",
        "",
        "## Ω_F (monthly)",
        "",
        df_to_md(pd.DataFrame(Omega_F, index=FACTOR_COLS, columns=FACTOR_COLS), 6),
        "",
        "## Correlation matrix",
        "",
        df_to_md(pd.DataFrame(corr_F, index=FACTOR_COLS, columns=FACTOR_COLS), 3),
        "",
        f"**Most-correlated pair:** `{best_pair[0]}` / `{best_pair[1]}` with ρ = {best_pair[2]:.3f}.",
        "",
        "Figures: `results/figures/03_corr_factors.png` (and the demeaned variant).",
        "",
    ]
    (MD / "03_factor_cov.md").write_text("\n".join(md), encoding="utf-8")
    print("wrote md_files/03_factor_cov.md")


if __name__ == "__main__":
    main()
