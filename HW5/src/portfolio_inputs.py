"""
Assembles the common set of optimisation inputs used by every Problem 7 run.

Returned `Inputs` dataclass carries aligned arrays on the 1 000-name universe
from `estimates.xlsx`: μ, realised returns, loadings B, covariance Ω_R, sector
indicator matrix and the per-stock capacity (share volume + price → dollars).
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from .covariance import factor_covariance, idio_covariance, total_covariance
from .io import (
    FACTOR_COLS,
    TARGET_SECTORS,
    average_monthly_volume,
    build_returns_matrix,
    load_estimates,
    load_factors,
    load_panel,
)
from .optimize import sector_indicator_matrix
from .regression import fit_loadings, fitted_and_residuals


@dataclass
class Inputs:
    mrap_ids: np.ndarray
    mu: np.ndarray
    realized: np.ndarray
    B: np.ndarray  # n x 5
    Omega_F: np.ndarray  # 5 x 5
    Omega_eps_diag: np.ndarray  # n x n diag
    Omega_R: np.ndarray
    factor_cols: list
    sectors: np.ndarray
    sector_ids: list
    sector_indicator: np.ndarray
    naics: np.ndarray
    price: np.ndarray
    shrout: np.ndarray
    adv_shares: np.ndarray

    @property
    def n(self) -> int:
        return len(self.mrap_ids)


def build_inputs(
    *,
    sector_ids=None,
    use_shrinkage: bool = False,
    shrink_lambda: float = 0.1,
) -> Inputs:
    """Returns optimisation inputs aligned to the 1 000 names in estimates.xlsx.

    Optionally apply a light shrinkage on Ω_R toward λ σ² I to stabilise the QP.
    """
    if sector_ids is None:
        sector_ids = list(TARGET_SECTORS)

    panel = load_panel()
    factors = load_factors()
    est = load_estimates()

    R_df, F, dates = build_returns_matrix(panel, factors)
    B_df = fit_loadings(R_df, F)
    _, eps_df = fitted_and_residuals(R_df, F, B_df)

    Omega_F = factor_covariance(F, demean=False)
    Omega_eps_diag = idio_covariance(eps_df, shrink_to_diag=True)

    # Align everything to estimates' universe order.
    est = est.sort_values("mrap_id").reset_index(drop=True)
    est_ids = est["mrap_id"].to_numpy()

    B_aligned = B_df.reindex(est_ids).fillna(0.0).to_numpy()

    # idio variances aligned
    idio_var = pd.Series(np.diag(Omega_eps_diag), index=B_df.index).reindex(est_ids).fillna(np.nanmean(np.diag(Omega_eps_diag))).to_numpy()
    Omega_eps_aligned = np.diag(idio_var)

    Omega_R = total_covariance(B_aligned, Omega_F, Omega_eps_aligned)

    if use_shrinkage:
        avg_var = float(np.mean(np.diag(Omega_R)))
        Omega_R = (1 - shrink_lambda) * Omega_R + shrink_lambda * avg_var * np.eye(Omega_R.shape[0])

    sectors = est["naics"].astype(int).astype(str).str[:2].astype(int).to_numpy()
    S_ind = sector_indicator_matrix(sectors, sector_ids)

    # Capacity inputs.
    adv_shares = average_monthly_volume(panel)
    adv_aligned = pd.Series(adv_shares).reindex(est_ids).fillna(adv_shares.median()).to_numpy()

    return Inputs(
        mrap_ids=est_ids,
        mu=est["pred"].to_numpy(),
        realized=est["ret"].to_numpy(),
        B=B_aligned,
        Omega_F=Omega_F,
        Omega_eps_diag=Omega_eps_aligned,
        Omega_R=Omega_R,
        factor_cols=FACTOR_COLS,
        sectors=sectors,
        sector_ids=sector_ids,
        sector_indicator=S_ind,
        naics=est["naics"].astype(int).to_numpy(),
        price=est["price"].to_numpy(),
        shrout=est["shrout"].to_numpy(),
        adv_shares=adv_aligned,
    )


def save_weights(inputs: Inputs, weights: np.ndarray, path: Path, *, book: float) -> pd.DataFrame:
    """Tabulate weights alongside the identifier / sector / dollar position."""
    n_shares_long = np.where(weights > 0, weights * book / np.maximum(inputs.price, 1e-6), 0.0)
    n_shares_short = np.where(weights < 0, -weights * book / np.maximum(inputs.price, 1e-6), 0.0)
    df = pd.DataFrame({
        "mrap_id": inputs.mrap_ids,
        "naics": inputs.naics,
        "sector": inputs.sectors,
        "weight": weights,
        "dollar_position": weights * book,
        "shares_long": n_shares_long,
        "shares_short": n_shares_short,
        "price": inputs.price,
        "alpha": inputs.mu,
        "realized": inputs.realized,
        "adv_shares": inputs.adv_shares,
    })
    df.to_csv(path, index=False)
    return df
