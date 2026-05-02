"""
Per-stock joint time-series regression: r_i = B_i F + eps_i.

The homework specifies eps = R - BF (no intercept), so the OLS is run
without an intercept. Each stock is fit on its available months.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def fit_loadings(
    R_df: pd.DataFrame, F: np.ndarray, *, min_obs: int = 24, fill_missing: float = 0.0
) -> pd.DataFrame:
    """Fit B where r_i(t) = B_i F(t) + eps_i(t), no intercept.

    Stocks with fewer than `min_obs` valid months get their betas set to
    `fill_missing` (default 0.0) so the downstream covariance algebra stays
    well-defined — their variance then shows up entirely in Ω_ε.

    Parameters
    ----------
    R_df : DataFrame n x T indexed by mrap_id with columns as dates.
    F    : ndarray 5 x T.

    Returns
    -------
    B_df : DataFrame n x 5 of factor loadings (columns factor_1..factor_5).
    """
    T = F.shape[1]
    assert R_df.shape[1] == T, "R_df columns must match F columns (dates)"
    B_rows = {}
    F_T = F.T  # T x 5
    for mrap_id, row in R_df.iterrows():
        r = row.to_numpy(dtype=float)
        mask = ~np.isnan(r)
        if mask.sum() < min_obs:
            B_rows[mrap_id] = np.full(F.shape[0], fill_missing)
            continue
        X = F_T[mask]          # (T_i x 5)
        y = r[mask]            # (T_i,)
        beta, *_ = np.linalg.lstsq(X, y, rcond=None)
        B_rows[mrap_id] = beta
    B_df = pd.DataFrame.from_dict(
        B_rows, orient="index", columns=[f"factor_{i+1}" for i in range(F.shape[0])]
    )
    B_df.index.name = "mrap_id"
    return B_df


def fitted_and_residuals(
    R_df: pd.DataFrame, F: np.ndarray, B_df: pd.DataFrame
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return fitted matrix Rhat = BF and residuals eps = R - BF (same shape as R_df)."""
    B = B_df.reindex(R_df.index).to_numpy()
    Rhat = B @ F
    Rhat_df = pd.DataFrame(Rhat, index=R_df.index, columns=R_df.columns)
    eps_df = R_df - Rhat_df
    return Rhat_df, eps_df
