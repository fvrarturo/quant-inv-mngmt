"""
Risk-model and portfolio diagnostics used by scripts/10_diagnostics.py.

Nothing here changes the homework answers; everything is a check that the
numbers produced upstream are well-behaved or, when they are not, an
explicit statement of how they are not.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats


# ---------------------------------------------------------------------- regression
def ols_with_stats(X: np.ndarray, y: np.ndarray) -> dict:
    """OLS with no intercept: β̂ = (XᵀX)⁻¹Xᵀy, HAC / white s.e., DW, JB, BP."""
    n, k = X.shape
    XtX_inv = np.linalg.inv(X.T @ X)
    beta = XtX_inv @ X.T @ y
    resid = y - X @ beta
    dof = max(n - k, 1)
    sigma2 = float(resid @ resid) / dof
    var_beta = sigma2 * np.diag(XtX_inv)
    se = np.sqrt(np.clip(var_beta, 0.0, None))
    tstat = beta / np.where(se > 0, se, np.nan)

    # Durbin-Watson.
    dw = float(np.sum(np.diff(resid) ** 2) / max(np.sum(resid ** 2), 1e-12))

    # White/HC0 standard errors (heteroscedasticity-robust).
    omega_hc0 = (resid[:, None] * resid[None, :])  # rank-1-like; cheap form:
    meat = X.T * resid[None, :] @ (X * resid[:, None])
    var_hc0 = XtX_inv @ meat @ XtX_inv
    se_hc0 = np.sqrt(np.clip(np.diag(var_hc0), 0.0, None))

    # Jarque–Bera for normality of residuals.
    if n >= 8 and resid.std() > 0:
        jb = float(stats.jarque_bera(resid).statistic)
        jb_p = float(stats.jarque_bera(resid).pvalue)
    else:
        jb, jb_p = np.nan, np.nan

    # Breusch–Pagan: regress resid² on X, LM statistic.
    if n > k:
        g = resid ** 2
        g_mean = g.mean()
        XtX_inv2 = XtX_inv  # same design matrix
        alpha = XtX_inv2 @ X.T @ g
        g_hat = X @ alpha
        ess = float(np.sum((g_hat - g_mean) ** 2))
        tss = float(np.sum((g - g_mean) ** 2))
        r2_bp = ess / tss if tss > 0 else 0.0
        lm = n * r2_bp
        bp_p = float(1 - stats.chi2.cdf(lm, df=k))
    else:
        lm, bp_p = np.nan, np.nan

    return dict(
        beta=beta, se=se, se_hc0=se_hc0, tstat=tstat, dw=dw,
        resid=resid, sigma2=sigma2, jb=jb, jb_p=jb_p, bp=lm, bp_p=bp_p,
        r2=1.0 - float(resid @ resid) / max(float((y - y.mean()) @ (y - y.mean())), 1e-12),
        n_obs=int(n),
    )


def variance_inflation_factors(X: np.ndarray) -> np.ndarray:
    """VIF_i = 1 / (1 - R²_i), with R²_i from regressing col i on the other cols."""
    k = X.shape[1]
    out = np.zeros(k)
    for j in range(k):
        mask = np.ones(k, dtype=bool)
        mask[j] = False
        Xj = X[:, j]
        Xr = X[:, mask]
        beta, *_ = np.linalg.lstsq(Xr, Xj, rcond=None)
        resid = Xj - Xr @ beta
        ss_res = float(resid @ resid)
        ss_tot = float((Xj - Xj.mean()) @ (Xj - Xj.mean()))
        r2 = 1 - ss_res / max(ss_tot, 1e-12)
        out[j] = 1 / max(1 - r2, 1e-12)
    return out


def condition_number(M: np.ndarray) -> float:
    w = np.linalg.eigvalsh((M + M.T) / 2)
    w = w[w > 0]
    if len(w) == 0:
        return np.inf
    return float(w.max() / w.min())


# ---------------------------------------------------------------------- covariance
def pca_of_covariance(M: np.ndarray, n_components: int = 10) -> pd.DataFrame:
    w, _ = np.linalg.eigh((M + M.T) / 2)
    w = np.sort(w)[::-1]
    total = w.sum()
    out = pd.DataFrame({
        "eigenvalue": w[:n_components],
        "variance_share": w[:n_components] / total,
        "cumulative": np.cumsum(w[:n_components]) / total,
    })
    return out


def pca_on_residuals(eps_df: pd.DataFrame, n_components: int = 5) -> pd.DataFrame:
    """If residuals truly had no structure, PCA on ε should explain <5 % / PC.
    Significant shares suggest missing systematic factors."""
    eps = eps_df.to_numpy(dtype=float)
    eps = np.where(np.isnan(eps), 0.0, eps)
    eps_c = eps - eps.mean(axis=1, keepdims=True)
    cov = (eps_c @ eps_c.T) / max(eps_c.shape[1] - 1, 1)
    return pca_of_covariance(cov, n_components=n_components)


# ---------------------------------------------------------------------- portfolio
def effective_number_of_bets(w: np.ndarray) -> float:
    """1 / sum(w_i²) normalised by gross²; ~N means perfectly diversified."""
    w = np.asarray(w, dtype=float)
    if np.sum(np.abs(w)) == 0:
        return 0.0
    w_norm = w / np.sum(np.abs(w))
    return float(1.0 / np.sum(w_norm ** 2))


def herfindahl(weights: np.ndarray) -> float:
    w = np.abs(weights)
    total = w.sum()
    if total == 0:
        return 1.0
    w_norm = w / total
    return float((w_norm ** 2).sum())


def factor_variance_decomposition(
    B: np.ndarray, Omega_F: np.ndarray, Omega_eps_diag: np.ndarray, w: np.ndarray
) -> dict:
    """Decompose wᵀ Ω_R w into factor contribution + idio contribution."""
    factor_var = float(w @ (B @ Omega_F @ B.T) @ w)
    idio_var = float(w @ Omega_eps_diag @ w)
    # contributions from each factor k: 2 * (Bᵀw)_k² * Ω_F[k, k] is an approx;
    # exact decomp comes from Bᵀw spectrum.
    Btw = B.T @ w
    per_factor = Btw * (Omega_F @ Btw)  # same sum as above when summed
    total = factor_var + idio_var
    return {
        "factor_var": factor_var,
        "idio_var": idio_var,
        "total_var": total,
        "factor_share": factor_var / total if total > 0 else np.nan,
        "idio_share": idio_var / total if total > 0 else np.nan,
        "per_factor_contribution": per_factor,
    }
