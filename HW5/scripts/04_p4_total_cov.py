#!/usr/bin/env python3
"""
Problem 4: total covariance matrix of returns.
  Omega_R = B Omega_F B^T + Omega_eps.

Also saves the correlation heatmap and reports the ρ between mrap_id 24541
and 91309. Discusses sources of estimation error.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

HW5 = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HW5))

from src.covariance import (
    correlation_from_covariance,
    factor_covariance,
    idio_covariance,
    total_covariance,
)
from src.io import FACTOR_COLS, build_returns_matrix, load_factors, load_panel
from src.plotting import large_corr_heatmap
from src.regression import fit_loadings, fitted_and_residuals

RESULTS = HW5 / "results"
FIGURES = RESULTS / "figures"
MD = HW5 / "md_files"

REPORT_PAIR = (24541, 91309)


def main() -> None:
    RESULTS.mkdir(exist_ok=True)
    FIGURES.mkdir(exist_ok=True)
    MD.mkdir(exist_ok=True)

    panel = load_panel()
    factors = load_factors()
    R_df, F, dates = build_returns_matrix(panel, factors)
    B_df = fit_loadings(R_df, F)
    _, eps_df = fitted_and_residuals(R_df, F, B_df)

    B = B_df.to_numpy()
    Omega_F = factor_covariance(F, demean=False)
    Omega_eps_diag = idio_covariance(eps_df, shrink_to_diag=True)
    Omega_R = total_covariance(B, Omega_F, Omega_eps_diag)
    corr_R = correlation_from_covariance(Omega_R)

    idx = B_df.index
    np.savez_compressed(RESULTS / "04_omega_R.npz",
                        matrix=Omega_R, mrap_ids=np.asarray(idx, dtype=np.int64))
    # also save CSV — can be large (1000x1000) but manageable
    pd.DataFrame(Omega_R, index=idx, columns=idx).to_csv(RESULTS / "04_omega_R.csv")
    pd.DataFrame(corr_R, index=idx, columns=idx).to_csv(RESULTS / "04_corr_R.csv")

    large_corr_heatmap(corr_R, FIGURES / "04_corr_R.png",
                       title=f"Correlation of returns Ω_R ({corr_R.shape[0]} x {corr_R.shape[0]})")

    # Specific pair.
    pos_map = {mid: i for i, mid in enumerate(idx)}
    a, b = REPORT_PAIR
    if a in pos_map and b in pos_map:
        ia, ib = pos_map[a], pos_map[b]
        rho_ab = float(corr_R[ia, ib])
        cov_ab = float(Omega_R[ia, ib])
        sigma_a = float(np.sqrt(Omega_R[ia, ia]))
        sigma_b = float(np.sqrt(Omega_R[ib, ib]))
    else:
        rho_ab = cov_ab = sigma_a = sigma_b = float("nan")
    print(f"rho({a}, {b}) = {rho_ab:.4f}")

    # min eigenvalue with graceful fallback
    try:
        min_eig = float(np.linalg.eigvalsh((Omega_R + Omega_R.T) / 2).min())
        min_eig_str = f"{min_eig:.3e}"
    except np.linalg.LinAlgError:
        min_eig_str = "did not converge (near-singular)"

    md = [
        "# Problem 4 — total covariance Ω_R",
        "",
        "Ω_R = B Ω_F Bᵀ + Ω_ε.",
        f"- Shape: {Omega_R.shape}.",
        f"- min eigenvalue: {min_eig_str}",
        "",
        f"## Reported pair",
        "",
        f"- ρ(MRAP {a}, MRAP {b}) = **{rho_ab:.4f}**",
        f"- σ(MRAP {a}) = {sigma_a:.4f}/mo, σ(MRAP {b}) = {sigma_b:.4f}/mo, cov = {cov_ab:.6f}",
        "",
        "Heatmap of Ω_R correlations: `results/figures/04_corr_R.png`.",
        "",
        "## What errors could have crept in, and what could be improved?",
        "",
        "1. **OLS loadings are noisy.** Per-stock OLS with only 108 observations (and",
        "   fewer for names that enter/exit mid-sample) produces betas with large",
        "   standard errors, especially when factors are correlated. Shrinking each",
        "   stock's β toward the cross-sectional mean (James–Stein) or using a",
        "   Bayesian/ridge fit would stabilise B.",
        "2. **No alpha term.** The no-intercept convention `R = BF + ε` forces any",
        "   level return into the residual. If a factor is not return-dollar-neutral",
        "   this can bias loadings. Centring F (and including an intercept) is a",
        "   standard fix.",
        "3. **Ω_F uses 108 months** — point-in-time estimate that is slow to respond",
        "   to regime shifts; an EWMA or DCC estimator, or separate specific/",
        "   systemic time horizons (Barra-style) would be preferable.",
        "4. **Diagonal Ω_ε assumption.** Residuals are not perfectly cross-",
        "   sectionally uncorrelated, especially within industries. Keeping a",
        "   block-diagonal Ω_ε by sector, or shrinking to the diagonal with a",
        "   Ledoit–Wolf-style target, is an improvement.",
        "5. **Stale factor definitions** — Ω_R does not adjust for turnover in the",
        "   factor construction; if the factors' own weighting schemes drift, Ω_F",
        "   moves too.",
        "6. **Non-synchronous data / outliers.** Price spikes (splits, corporate",
        "   actions) blow up individual residuals. Robust regression (Huber) or",
        "   winsorisation would reduce leverage of a few big residual months.",
        "7. **Small-T / large-N.** 1 000 names × 108 months ≈ rank-deficient sample",
        "   covariance; Ω_R gets structure only from B Ω_F Bᵀ (rank ≤ 5). Augmenting",
        "   with a statistical factor pull (PCA on ε) could catch missing factors.",
        "",
    ]
    (MD / "04_total_cov.md").write_text("\n".join(md), encoding="utf-8")
    print("wrote md_files/04_total_cov.md")


if __name__ == "__main__":
    main()
