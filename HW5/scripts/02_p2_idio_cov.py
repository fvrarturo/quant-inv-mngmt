#!/usr/bin/env python3
"""
Problem 2: Idiosyncratic returns and covariance.

  eps = R - BF
  Omega_eps = E[eps eps^T] = (1/T) eps eps^T

The factor-risk-model convention keeps only the diagonal of Omega_eps
(residuals assumed cross-sectionally uncorrelated). We save both the full
sample estimate and the diagonal version so we can inspect what shrinkage
does in problem 4.

Outputs:
  - results/02_omega_eps_diag.csv      (n x n, diagonal)
  - results/02_omega_eps_full.csv      (n x n, full sample — large)
  - results/02_idio_variance.csv       per-stock residual variance/std
  - md_files/02_idio_cov.md            discussion
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

HW5 = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HW5))

from src.covariance import idio_covariance
from src.io import build_returns_matrix, load_factors, load_panel
from src.regression import fit_loadings, fitted_and_residuals

RESULTS = HW5 / "results"
MD = HW5 / "md_files"


def main() -> None:
    RESULTS.mkdir(exist_ok=True)
    MD.mkdir(exist_ok=True)

    panel = load_panel()
    factors = load_factors()
    R_df, F, dates = build_returns_matrix(panel, factors)
    B_df = fit_loadings(R_df, F)
    _, eps_df = fitted_and_residuals(R_df, F, B_df)

    # Diagonal and full idiosyncratic covariance.
    Omega_eps_diag = idio_covariance(eps_df, shrink_to_diag=True)
    Omega_eps_full = idio_covariance(eps_df, shrink_to_diag=False)
    idx = eps_df.index

    pd.DataFrame(np.diag(Omega_eps_diag), index=idx, columns=["idio_var"]).to_csv(
        RESULTS / "02_idio_variance.csv"
    )
    pd.DataFrame(Omega_eps_diag, index=idx, columns=idx).to_csv(RESULTS / "02_omega_eps_diag.csv")
    # Full matrix is large (1000 x 1000); we save as npz for compactness too.
    np.savez_compressed(RESULTS / "02_omega_eps_full.npz", matrix=Omega_eps_full,
                        mrap_ids=np.asarray(idx, dtype=np.int64))
    # And a CSV for completeness — ~1000x1000 floats, ok.
    pd.DataFrame(Omega_eps_full, index=idx, columns=idx).to_csv(RESULTS / "02_omega_eps_full.csv")

    idio_std = np.sqrt(np.diag(Omega_eps_full))
    print("idio std — min / median / mean / max:",
          float(np.nanmin(idio_std)), float(np.nanmedian(idio_std)),
          float(np.nanmean(idio_std)), float(np.nanmax(idio_std)))

    md = [
        "# Problem 2 — idiosyncratic covariance",
        "",
        "## ε = R − BF",
        "",
        "With per-stock OLS loadings `B` from problem 1 we computed",
        "ε = R − BF and Ω_ε = (1/T) ε ε^T.",
        "",
        f"- ε shape: {eps_df.shape}.",
        f"- Median idiosyncratic monthly σ: {np.nanmedian(idio_std):.4f} ({np.nanmedian(idio_std)*np.sqrt(12):.3f} annualised).",
        f"- Mean idiosyncratic monthly σ:   {np.nanmean(idio_std):.4f}.",
        f"- Max idiosyncratic monthly σ:    {np.nanmax(idio_std):.4f}.",
        "",
        "## What is `BF` doing?",
        "",
        "`BF` is the **systematic-return** reconstruction of the n × T return panel:",
        "each stock's n × 5 loading row `B_i` multiplies the 5 × T factor path `F`",
        "to give the part of that stock's time series that is explained by the",
        "five common factors. Equivalently, `BF` is the orthogonal projection of",
        "`R` onto the factor subspace in time-series sense (for a per-stock OLS",
        "without intercept). It collapses cross-sectional co-movement into five",
        "shared drivers; whatever remains in ε = R − BF is the stock-specific",
        "residual that the factor model does not capture and that we take to be",
        "(approximately) uncorrelated across names.",
        "",
        "## File outputs",
        "",
        "- `results/02_idio_variance.csv` — per-stock idiosyncratic variance.",
        "- `results/02_omega_eps_diag.csv` — Ω_ε with zeroed off-diagonals (the",
        "  convention used in the Ω_R decomposition of problem 4).",
        "- `results/02_omega_eps_full.csv` / `.npz` — the un-shrunk sample Ω_ε.",
        "",
    ]
    (MD / "02_idio_cov.md").write_text("\n".join(md), encoding="utf-8")
    print("wrote md_files/02_idio_cov.md")


if __name__ == "__main__":
    main()
