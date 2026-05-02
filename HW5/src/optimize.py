"""
Portfolio optimization utilities for HW5.

All optimizations build a dollar-neutral long/short portfolio with monthly
volatility capped at TARGET_ANNUAL_VOL / sqrt(12). Weights are dollar weights
(fractions of gross book value) such that sum(w)=0 and sum(|w|)=1 (gross=1).

We maximize expected return subject to:
    - sum(w) = 0                              (dollar neutral)
    - sum(|w|) <= 1                           (gross exposure cap)
    - w^T Omega w <= sigma_cap^2              (monthly variance cap)
    - + optional position bounds, factor/sector neutrality, turnover, etc.

The gross = 1 budget lets us interpret w_i directly as "fraction of gross
book". Dollar amounts for a $X book come from w_i * gross_X.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

import cvxpy as cp
import numpy as np
import pandas as pd

TARGET_ANNUAL_VOL = 0.10  # 10 % annualized
MONTHS = 12


@dataclass
class OptimizeResult:
    weights: np.ndarray
    status: str
    expected_return: float
    realized_return: float
    monthly_vol: float
    annual_vol: float
    gross: float
    net: float
    factor_exposure: dict
    sector_exposure: dict
    problem_value: Optional[float] = None
    meta: dict = field(default_factory=dict)

    def to_summary(self) -> dict:
        return {
            "status": self.status,
            "expected_return": self.expected_return,
            "realized_return": self.realized_return,
            "monthly_vol": self.monthly_vol,
            "annual_vol": self.annual_vol,
            "gross": self.gross,
            "net": self.net,
            **{f"factor_exp_{k}": v for k, v in self.factor_exposure.items()},
            **{f"sector_exp_{k}": v for k, v in self.sector_exposure.items()},
            **self.meta,
        }


def _make_problem(
    mu: np.ndarray,
    Sigma: np.ndarray,
    *,
    sigma_cap: float,
    box: Optional[float] = None,
    factor_loadings: Optional[np.ndarray] = None,  # n x K
    neutral_factor_idx: Optional[list[int]] = None,
    factor_tol: float = 1e-6,
    sector_indicator: Optional[np.ndarray] = None,  # n x S
    neutral_sectors: bool = False,
    sector_tol: float = 1e-6,
    max_weights: Optional[np.ndarray] = None,  # n, per-stock upper bounds
    min_weights: Optional[np.ndarray] = None,  # n, per-stock lower bounds
    l1_ball: float = 1.0,  # gross cap
    shock_caps: Optional[list[tuple[np.ndarray, float]]] = None,
):
    """Build the cvxpy problem used by solve_portfolio."""
    n = mu.shape[0]
    w = cp.Variable(n)
    constraints = [
        cp.sum(w) == 0,
        cp.norm1(w) <= l1_ball,
        cp.quad_form(w, cp.psd_wrap(Sigma)) <= sigma_cap ** 2,
    ]
    if box is not None:
        constraints += [w <= box, w >= -box]
    if max_weights is not None:
        constraints += [w <= max_weights]
    if min_weights is not None:
        constraints += [w >= min_weights]
    if factor_loadings is not None and neutral_factor_idx:
        B = factor_loadings
        for k in neutral_factor_idx:
            constraints += [
                B[:, k] @ w <= factor_tol,
                B[:, k] @ w >= -factor_tol,
            ]
    if sector_indicator is not None and neutral_sectors:
        S_mat = sector_indicator
        for s in range(S_mat.shape[1]):
            constraints += [
                S_mat[:, s] @ w <= sector_tol,
                S_mat[:, s] @ w >= -sector_tol,
            ]
    if shock_caps is not None:
        for shock_vec, cap in shock_caps:
            constraints += [shock_vec @ w <= cap, shock_vec @ w >= -cap]
    objective = cp.Maximize(mu @ w)
    return cp.Problem(objective, constraints), w


def solve_portfolio(
    mu: np.ndarray,
    Sigma: np.ndarray,
    realized: np.ndarray,
    factor_loadings: np.ndarray,
    sector_indicator: np.ndarray,
    sector_ids: list,
    *,
    target_annual_vol: float = TARGET_ANNUAL_VOL,
    box: Optional[float] = None,
    max_weights: Optional[np.ndarray] = None,
    min_weights: Optional[np.ndarray] = None,
    neutral_factor_idx: Optional[list[int]] = None,
    neutral_sectors: bool = False,
    factor_tol: float = 1e-6,
    sector_tol: float = 1e-6,
    shock_caps: Optional[list[tuple[np.ndarray, float]]] = None,
    solver: str = "CLARABEL",
    meta: Optional[dict] = None,
) -> OptimizeResult:
    """Build and solve the MVO problem, return summary + weights."""
    sigma_cap_monthly = target_annual_vol / np.sqrt(MONTHS)
    prob, w_var = _make_problem(
        mu,
        Sigma,
        sigma_cap=sigma_cap_monthly,
        box=box,
        factor_loadings=factor_loadings,
        neutral_factor_idx=neutral_factor_idx,
        factor_tol=factor_tol,
        sector_indicator=sector_indicator,
        neutral_sectors=neutral_sectors,
        sector_tol=sector_tol,
        max_weights=max_weights,
        min_weights=min_weights,
        shock_caps=shock_caps,
    )
    try:
        prob.solve(solver=solver)
    except Exception as exc:  # noqa: BLE001
        return OptimizeResult(
            weights=np.zeros_like(mu),
            status=f"solver_error: {exc}",
            expected_return=np.nan,
            realized_return=np.nan,
            monthly_vol=np.nan,
            annual_vol=np.nan,
            gross=np.nan,
            net=np.nan,
            factor_exposure={},
            sector_exposure={},
            problem_value=None,
            meta=meta or {},
        )
    w = w_var.value
    if w is None:
        return OptimizeResult(
            weights=np.zeros_like(mu),
            status=f"infeasible: {prob.status}",
            expected_return=np.nan,
            realized_return=np.nan,
            monthly_vol=np.nan,
            annual_vol=np.nan,
            gross=np.nan,
            net=np.nan,
            factor_exposure={},
            sector_exposure={},
            problem_value=None,
            meta=meta or {},
        )
    monthly_vol = float(np.sqrt(max(w @ Sigma @ w, 0.0)))
    factor_exp = {
        f"factor_{k+1}": float(factor_loadings[:, k] @ w) for k in range(factor_loadings.shape[1])
    }
    sector_exp = {
        str(s): float(sector_indicator[:, i] @ w) for i, s in enumerate(sector_ids)
    }
    return OptimizeResult(
        weights=np.asarray(w),
        status=prob.status,
        expected_return=float(mu @ w),
        realized_return=float(realized @ w),
        monthly_vol=monthly_vol,
        annual_vol=monthly_vol * np.sqrt(MONTHS),
        gross=float(np.sum(np.abs(w))),
        net=float(np.sum(w)),
        factor_exposure=factor_exp,
        sector_exposure=sector_exp,
        problem_value=float(prob.value) if prob.value is not None else None,
        meta=meta or {},
    )


def volume_based_max_weights(
    avg_monthly_shares: np.ndarray,
    price: np.ndarray,
    gross_dollars: float,
    vol_frac: float = 0.02,
) -> np.ndarray:
    """Convert a per-stock trading capacity to a max weight fraction.

    Max dollar trade per name = vol_frac * avg_monthly_shares * price.
    Expressed as fraction of gross book = that dollar amount / gross_dollars.
    """
    cap_dollars = vol_frac * avg_monthly_shares * price
    return cap_dollars / gross_dollars


def sector_indicator_matrix(sectors: np.ndarray, sector_ids: list) -> np.ndarray:
    """n x S indicator matrix (1 if stock i is in sector s)."""
    M = np.zeros((len(sectors), len(sector_ids)), dtype=float)
    for j, sid in enumerate(sector_ids):
        M[:, j] = (sectors == sid).astype(float)
    return M
