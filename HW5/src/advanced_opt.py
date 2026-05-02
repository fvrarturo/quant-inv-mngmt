"""
Advanced portfolio-construction methods used by 11_advanced_extensions.py.

These are layered on top of the baseline MVO implemented in src/optimize.py
to show how deliverable expected/realised-return trade-offs move when we
change *what* we are optimising rather than the constraint set.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import cvxpy as cp
import numpy as np


@dataclass
class AdvResult:
    weights: np.ndarray
    status: str
    objective: float
    meta: dict


# ------------------------------------------------------- min-variance portfolio
def minimum_variance(
    Sigma: np.ndarray,
    mu: Optional[np.ndarray] = None,
    *,
    max_abs: Optional[np.ndarray] = None,
    gross: float = 1.0,
    dollar_neutral: bool = True,
    target_return: Optional[float] = None,
    factor_loadings: Optional[np.ndarray] = None,
    neutral_factor_idx: Optional[list[int]] = None,
    sector_indicator: Optional[np.ndarray] = None,
    neutral_sectors: bool = False,
    factor_tol: float = 1e-6,
    sector_tol: float = 1e-6,
) -> AdvResult:
    """Min-variance dollar-neutral portfolio.

    Pure min-variance on a dollar-neutral, bounded-gross problem is
    degenerate: w=0 always wins. We therefore also impose a target
    return `μᵀw = target_return` (if both μ and target_return are given)
    — this yields the canonical "mean-variance efficient" left edge.
    Callers that want the degenerate version can pass target_return=None
    and mu=None; they will get w≈0 back as a sanity check.
    """
    n = Sigma.shape[0]
    w = cp.Variable(n)
    cons = [cp.norm1(w) <= gross]
    if dollar_neutral:
        cons.append(cp.sum(w) == 0)
    if max_abs is not None:
        cons += [w <= max_abs, w >= -max_abs]
    if mu is not None and target_return is not None:
        cons.append(mu @ w == target_return)
    if factor_loadings is not None and neutral_factor_idx:
        for k in neutral_factor_idx:
            cons += [factor_loadings[:, k] @ w <= factor_tol,
                     factor_loadings[:, k] @ w >= -factor_tol]
    if sector_indicator is not None and neutral_sectors:
        for s in range(sector_indicator.shape[1]):
            cons += [sector_indicator[:, s] @ w <= sector_tol,
                     sector_indicator[:, s] @ w >= -sector_tol]
    prob = cp.Problem(cp.Minimize(cp.quad_form(w, cp.psd_wrap(Sigma))), cons)
    prob.solve(solver="CLARABEL")
    val = float(prob.value) if prob.value is not None else float("nan")
    return AdvResult(
        weights=np.zeros(n) if w.value is None else np.asarray(w.value),
        status=prob.status,
        objective=val,
        meta={"method": "minimum_variance", "target_return": target_return},
    )


# ---------------------------------------------------------- max-Sharpe (MV-SR)
def max_sharpe(
    mu: np.ndarray,
    Sigma: np.ndarray,
    *,
    max_abs: Optional[np.ndarray] = None,
    gross: float = 1.0,
    dollar_neutral: bool = True,
    **kw,
) -> AdvResult:
    """Because MaxSharpe with a dollar-neutral budget is scale-invariant, we
    instead implement the canonical trick: solve max μᵀw / √(wᵀΣw), which
    with a gross-budget becomes a grid over σ_cap. Here we sweep σ_cap
    across [0.5 %, 30 %] ann and pick the highest μᵀw / σ ratio."""
    n = Sigma.shape[0]
    best = None
    for sig_a in np.linspace(0.005, 0.30, 30):
        sigma_cap = sig_a / np.sqrt(12)
        w = cp.Variable(n)
        cons = [cp.norm1(w) <= gross,
                cp.quad_form(w, cp.psd_wrap(Sigma)) <= sigma_cap ** 2]
        if dollar_neutral:
            cons.append(cp.sum(w) == 0)
        if max_abs is not None:
            cons += [w <= max_abs, w >= -max_abs]
        prob = cp.Problem(cp.Maximize(mu @ w), cons)
        prob.solve(solver="CLARABEL")
        if w.value is None:
            continue
        wv = np.asarray(w.value)
        sig = float(np.sqrt(max(wv @ Sigma @ wv, 0.0)))
        sr = float(mu @ wv) / sig if sig > 0 else 0.0
        if best is None or sr > best["sr"]:
            best = {"w": wv, "sig": sig, "sr": sr, "sig_cap": sig_a}
    if best is None:
        return AdvResult(weights=np.zeros(n), status="infeasible",
                         objective=np.nan, meta={"method": "max_sharpe"})
    return AdvResult(weights=best["w"], status="optimal",
                     objective=best["sr"],
                     meta={"method": "max_sharpe",
                           "best_sigma_cap_a": best["sig_cap"],
                           "monthly_sigma": best["sig"]})


# ---------------------------------------------------- risk parity on factors
def factor_risk_parity(
    mu: np.ndarray,
    B: np.ndarray,
    Omega_F: np.ndarray,
    Omega_eps_diag: np.ndarray,
    *,
    max_abs: Optional[np.ndarray] = None,
    gross: float = 1.0,
    target_annual_vol: float = 0.10,
    parity_cap_bps: float = 50.0,
) -> AdvResult:
    """Long-short "risk-parity"-flavoured portfolio on the factor exposures.

    We constrain each factor's σ-scaled dollar exposure to a common cap
       |(Bᵀw)_k| σ_k ≤ parity_cap_bps · 10⁻⁴
    then maximise μᵀw. This is a simple way to equalise risk contributions
    across factors while still using μ.
    """
    n = B.shape[0]
    K = B.shape[1]
    sigma_cap = target_annual_vol / np.sqrt(12)
    f_sig = np.sqrt(np.diag(Omega_F))
    cap = parity_cap_bps * 1e-4
    w = cp.Variable(n)
    Btw = B.T @ w
    cons = [
        cp.norm1(w) <= gross, cp.sum(w) == 0,
        cp.quad_form(w, cp.psd_wrap(B @ Omega_F @ B.T + Omega_eps_diag))
        <= sigma_cap ** 2,
    ]
    for k in range(K):
        cons += [Btw[k] * f_sig[k] <= cap, Btw[k] * f_sig[k] >= -cap]
    if max_abs is not None:
        cons += [w <= max_abs, w >= -max_abs]
    prob = cp.Problem(cp.Maximize(mu @ w), cons)
    prob.solve(solver="CLARABEL")
    wv = np.zeros(n) if w.value is None else np.asarray(w.value)
    return AdvResult(weights=wv, status=prob.status,
                     objective=float(prob.value) if prob.value is not None else np.nan,
                     meta={"method": "factor_risk_parity",
                           "parity_cap_bps": parity_cap_bps})


# ---------------------------------------------------- Black–Litterman
def black_litterman(
    Sigma: np.ndarray,
    mkt_weights: np.ndarray,
    views_P: np.ndarray,   # K x N pick matrix
    views_Q: np.ndarray,   # K vector of view returns
    delta: float = 2.5,
    tau: float = 0.05,
    omega_views: Optional[np.ndarray] = None,  # K x K view uncertainty
) -> np.ndarray:
    """Standard BL posterior mean.

    Π = δ Σ w_mkt                        (implied equilibrium return)
    μ_BL = [(τΣ)⁻¹ + Pᵀ Ω⁻¹ P]⁻¹ [(τΣ)⁻¹ Π + Pᵀ Ω⁻¹ Q]
    """
    pi = delta * Sigma @ mkt_weights
    if omega_views is None:
        omega_views = np.diag(np.diag(views_P @ (tau * Sigma) @ views_P.T))
    tauSigma_inv = np.linalg.pinv(tau * Sigma)
    OmegaInv = np.linalg.pinv(omega_views)
    A = tauSigma_inv + views_P.T @ OmegaInv @ views_P
    b = tauSigma_inv @ pi + views_P.T @ OmegaInv @ views_Q
    mu_bl = np.linalg.solve(A, b)
    return mu_bl


# ---------------------------------------------------- CVaR optimisation
def cvar_portfolio(
    scenarios: np.ndarray,      # S x N matrix of scenario returns
    alpha: float = 0.05,
    *,
    max_abs: Optional[np.ndarray] = None,
    gross: float = 1.0,
    mu: Optional[np.ndarray] = None,
    lam: float = 1.0,
    dollar_neutral: bool = True,
) -> AdvResult:
    """Minimise CVaR(α) − λ μᵀw (Rockafellar-Uryasev LP form)."""
    S, N = scenarios.shape
    w = cp.Variable(N)
    z = cp.Variable(S, nonneg=True)
    eta = cp.Variable()
    losses = -scenarios @ w
    cons = [z >= losses - eta, cp.norm1(w) <= gross]
    if dollar_neutral:
        cons.append(cp.sum(w) == 0)
    if max_abs is not None:
        cons += [w <= max_abs, w >= -max_abs]
    cvar_expr = eta + (1 / (alpha * S)) * cp.sum(z)
    obj = cvar_expr if mu is None else cvar_expr - lam * (mu @ w)
    prob = cp.Problem(cp.Minimize(obj), cons)
    prob.solve(solver="CLARABEL")
    wv = np.zeros(N) if w.value is None else np.asarray(w.value)
    return AdvResult(weights=wv, status=prob.status,
                     objective=float(prob.value) if prob.value is not None else np.nan,
                     meta={"method": "cvar", "alpha": alpha,
                           "eta": float(eta.value) if eta.value is not None else np.nan})


# ---------------------------------------------------- James–Stein shrinkage on B
def james_stein_betas(B: np.ndarray) -> np.ndarray:
    """Classical JS estimator: B̂ = (1-c) B + c B̄, with c from the
    cross-sectional mean beta and the common variance.
    Here we shrink each column of B toward its cross-sectional mean with
    per-factor shrinkage that grows with the cross-sectional variance."""
    B = np.asarray(B, dtype=float)
    n, k = B.shape
    B_bar = B.mean(axis=0)
    c = np.zeros(k)
    for j in range(k):
        col = B[:, j]
        ss_to_mean = float(((col - B_bar[j]) ** 2).sum())
        if ss_to_mean <= 0:
            c[j] = 0.0
            continue
        sigma2_hat = float(col.var(ddof=1))
        c[j] = max(0.0, min(1.0, (n - 2) * sigma2_hat / ss_to_mean))
    return (1 - c) * B + c * B_bar


# ---------------------------------------------------- Michaud resampling
def michaud_resample(
    mu: np.ndarray, Sigma: np.ndarray,
    solve_fn,           # callable(mu, Sigma) -> w
    n_draws: int = 50,
    n_months: int = 60,
    rng: np.random.Generator | None = None,
) -> np.ndarray:
    """Average the optimal weights across bootstrap draws of (μ, Σ)."""
    rng = rng or np.random.default_rng(0)
    L = np.linalg.cholesky(Sigma + 1e-10 * np.eye(Sigma.shape[0]))
    w_acc = np.zeros_like(mu)
    n_ok = 0
    for _ in range(n_draws):
        # resample a (T_months x N) return panel from N(μ, Σ) and estimate.
        Z = rng.standard_normal((n_months, mu.shape[0]))
        R = mu[None, :] + Z @ L.T
        mu_hat = R.mean(axis=0)
        Sigma_hat = np.cov(R, rowvar=False)
        w = solve_fn(mu_hat, Sigma_hat)
        if w is None or np.any(~np.isfinite(w)):
            continue
        w_acc += w
        n_ok += 1
    return w_acc / max(n_ok, 1)


# ---------------------------------------------------- Hierarchical risk parity
def hierarchical_risk_parity(
    Sigma: np.ndarray,
    mu: Optional[np.ndarray] = None,
    *,
    box: Optional[float] = None,
) -> np.ndarray:
    """Lopez de Prado 2016 --- HRP adapted to long/short.

    Standard HRP produces long-only capital weights w⁺. For a long/short
    portfolio we overlay a sign taken from the ranked µ (top half long,
    bottom half short) and re-scale to gross = 1 and dollar-neutral.
    """
    std = np.sqrt(np.clip(np.diag(Sigma), 1e-12, None))
    corr = Sigma / np.outer(std, std)
    dist = np.sqrt(np.clip(0.5 * (1 - corr), 0.0, None))
    from scipy.cluster.hierarchy import linkage, leaves_list
    from scipy.spatial.distance import squareform
    dist_cond = squareform(dist, checks=False)
    Z = linkage(dist_cond, method="single")
    order = leaves_list(Z)

    w = np.ones(Sigma.shape[0])
    stack = [order]
    while stack:
        idx = stack.pop()
        if len(idx) <= 1:
            continue
        mid = len(idx) // 2
        left, right = idx[:mid], idx[mid:]
        var_l = float(_cluster_variance(Sigma, left))
        var_r = float(_cluster_variance(Sigma, right))
        alpha = 1 - var_l / (var_l + var_r + 1e-12)
        w[left] *= alpha
        w[right] *= 1 - alpha
    # long-only HRP weights
    w = w / max(w.sum(), 1e-12)
    # overlay long-short sign from µ-rank
    if mu is not None:
        ranks = np.argsort(np.argsort(mu))
        half = len(mu) // 2
        sign = np.where(ranks >= half, +1.0, -1.0)
    else:
        sign = np.where(np.arange(len(w)) % 2 == 0, +1.0, -1.0)
    w = w * sign
    # enforce dollar-neutral, gross=1
    w = w - w.mean()
    denom = np.abs(w).sum()
    w = w / denom if denom > 0 else w
    if box is not None:
        w = np.clip(w, -box, box)
        w = w - w.mean()
        denom = np.abs(w).sum()
        w = w / denom if denom > 0 else w
    return w


def _cluster_variance(Sigma: np.ndarray, idx: np.ndarray) -> float:
    Sub = Sigma[np.ix_(idx, idx)]
    d = np.clip(np.diag(Sub), 1e-12, None)
    iv = 1.0 / d
    s = iv.sum()
    if not np.isfinite(s) or s <= 0:
        return float(Sub.mean())
    iv = iv / s
    return float(iv @ Sub @ iv)


# ---------------------------------------------------- Rolling-window B (time-varying)
def rolling_loadings(
    R_df, F: np.ndarray, *, window: int = 36, step: int = 1
) -> dict:
    """For each stock and each trailing `window` months, fit OLS and return
    the time series of betas."""
    n, T = R_df.shape
    out = {}
    dates = list(R_df.columns)
    for mid, row in R_df.iterrows():
        r = row.to_numpy(dtype=float)
        betas = []
        for t_end in range(window, T + 1, step):
            mask = ~np.isnan(r[t_end - window:t_end])
            if mask.sum() < max(window - 5, 10):
                betas.append(np.full(F.shape[0], np.nan))
                continue
            X = F.T[t_end - window:t_end][mask]
            y = r[t_end - window:t_end][mask]
            beta, *_ = np.linalg.lstsq(X, y, rcond=None)
            betas.append(beta)
        out[mid] = np.asarray(betas)
    return {"betas": out, "dates": dates[window - 1::step]}
