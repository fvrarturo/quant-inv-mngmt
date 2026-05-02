"""
Covariance builders for the factor risk model.

Omega_R = B Omega_F B^T + Omega_eps.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def factor_covariance(F: np.ndarray, demean: bool = False) -> np.ndarray:
    """Omega_F = (1/T) F F^T (problem statement uses second-moment form).

    If demean=True, use the sample covariance (demeaned) instead.
    """
    T = F.shape[1]
    if demean:
        Fc = F - F.mean(axis=1, keepdims=True)
        return (Fc @ Fc.T) / (T - 1)
    return (F @ F.T) / T


def idio_covariance(eps_df: pd.DataFrame, shrink_to_diag: bool = True) -> np.ndarray:
    """Omega_eps = E[eps eps^T]. Uses the same 1/T second-moment form.

    Missing cells are treated as 0 contribution. `shrink_to_diag` keeps only
    the diagonal of the idiosyncratic covariance which is the standard
    assumption in a factor risk model (residuals are assumed cross-sectionally
    uncorrelated); set to False to retain the full sample estimate.
    """
    eps = eps_df.to_numpy(dtype=float)
    eps = np.where(np.isnan(eps), 0.0, eps)
    T = eps.shape[1]
    cov = (eps @ eps.T) / T
    if shrink_to_diag:
        cov = np.diag(np.diag(cov))
    return cov


def total_covariance(B: np.ndarray, Omega_F: np.ndarray, Omega_eps: np.ndarray) -> np.ndarray:
    """Omega_R = B Omega_F B^T + Omega_eps."""
    return B @ Omega_F @ B.T + Omega_eps


def correlation_from_covariance(cov: np.ndarray) -> np.ndarray:
    std = np.sqrt(np.clip(np.diag(cov), 0.0, None))
    std[std == 0] = np.nan
    inv = 1.0 / std
    corr = (cov * inv[:, None]) * inv[None, :]
    return np.nan_to_num(corr, nan=0.0, posinf=0.0, neginf=0.0)


def nearest_psd(M: np.ndarray, eps: float = 1e-10) -> np.ndarray:
    """Project a symmetric matrix to the nearest PSD by clipping eigenvalues."""
    S = (M + M.T) / 2.0
    w, V = np.linalg.eigh(S)
    w_clipped = np.clip(w, eps, None)
    return (V * w_clipped) @ V.T
