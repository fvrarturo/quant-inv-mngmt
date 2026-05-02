"""
Signal effectiveness metrics with hypothesis tests (IC, hit rate, regression, rank IC).
"""
from typing import Tuple

import numpy as np
import pandas as pd
from scipy import stats


def _dropna_pair(signal: pd.Series, forward_return: pd.Series) -> Tuple[np.ndarray, np.ndarray]:
    """Return (signal, return) as numpy arrays with pairwise dropna."""
    df = pd.concat([signal, forward_return], axis=1).dropna()
    return df.iloc[:, 0].values, df.iloc[:, 1].values


def _fisher_z(r: float, n: int) -> Tuple[float, float]:
    """Fisher z-transform and SE; return (z, se)."""
    if n < 4 or abs(r) >= 1:
        return np.nan, np.nan
    z = 0.5 * np.log((1 + r) / (1 - r))
    se = 1.0 / np.sqrt(n - 3)
    return z, se


def _z_to_r(z: float) -> float:
    """Inverse Fisher z to correlation."""
    if np.isnan(z):
        return np.nan
    e = np.exp(2 * z)
    return (e - 1) / (e + 1)


def compute_ic(
    signal: pd.Series, forward_return: pd.Series
) -> Tuple[float, int, float, float, float]:
    """Pearson IC with Fisher z-test. Returns (ic, n, p_value, ci_low, ci_high)."""
    s, r = _dropna_pair(signal, forward_return)
    n = len(s)
    if n < 4:
        return np.nan, n, np.nan, np.nan, np.nan
    ic = np.corrcoef(s, r)[0, 1]
    if np.isnan(ic):
        return np.nan, n, np.nan, np.nan, np.nan
    z, se = _fisher_z(ic, n)
    if np.isnan(z):
        return ic, n, np.nan, np.nan, np.nan
    z_stat = z / se
    p_value = 2 * (1 - stats.norm.cdf(abs(z_stat)))
    z_lo = z - 1.96 * se
    z_hi = z + 1.96 * se
    ci_low = _z_to_r(z_lo)
    ci_high = _z_to_r(z_hi)
    return float(ic), n, float(p_value), float(ci_low), float(ci_high)


def compute_hit_rate(
    signal: pd.Series, forward_return: pd.Series
) -> Tuple[float, int, float, float, float]:
    """Hit rate = P(sign(signal)==sign(return)). Binomial test H0: p=0.5. Returns (hit_rate, n, p_value, ci_low, ci_high)."""
    s, r = _dropna_pair(signal, forward_return)
    n = len(s)
    if n == 0:
        return np.nan, 0, np.nan, np.nan, np.nan
    # Exclude signal exactly 0 (already NaN in cleaned data)
    signs_s = np.sign(s)
    signs_r = np.sign(r)
    valid = (signs_s != 0) & (signs_r != 0)
    s_ok = signs_s[valid]
    r_ok = signs_r[valid]
    n_ok = len(s_ok)
    if n_ok == 0:
        return np.nan, 0, np.nan, np.nan, np.nan
    hits = np.sum(s_ok == r_ok)
    hit_rate = hits / n_ok
    res = stats.binomtest(int(hits), n_ok, p=0.5, alternative="two-sided")
    p_value = res.pvalue
    # Wilson score interval for proportion
    z = 1.96
    denom = 1 + z**2 / n_ok
    center = (hit_rate + z**2 / (2 * n_ok)) / denom
    margin = z * np.sqrt(hit_rate * (1 - hit_rate) / n_ok + z**2 / (4 * n_ok**2)) / denom
    ci_low = center - margin
    ci_high = center + margin
    ci_low = max(0.0, ci_low)
    ci_high = min(1.0, ci_high)
    return float(hit_rate), n_ok, float(p_value), float(ci_low), float(ci_high)


def compute_regression(
    signal: pd.Series, forward_return: pd.Series
) -> Tuple[float, float, float, float, float, float, float]:
    """OLS forward_return = alpha + beta * signal. Returns (beta, se, t_stat, p_value, r_squared, ci_low, ci_high)."""
    s, r = _dropna_pair(signal, forward_return)
    n = len(s)
    if n < 3:
        return np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan
    X = np.column_stack([np.ones(n), s])
    try:
        beta_vec, residuals, rank, s2 = np.linalg.lstsq(X, r, rcond=None)[:4]
    except Exception:
        return np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan
    beta = float(beta_vec[1])
    y_hat = X @ beta_vec
    ss_res = np.sum((r - y_hat) ** 2)
    ss_tot = np.sum((r - np.mean(r)) ** 2)
    r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0.0
    mse = ss_res / (n - 2) if n > 2 else np.nan
    var_beta = mse * np.linalg.inv(X.T @ X)[1, 1]
    se = np.sqrt(var_beta)
    t_stat = beta / se if se > 0 else np.nan
    p_value = 2 * (1 - stats.t.cdf(abs(t_stat), n - 2))
    t_crit = stats.t.ppf(0.975, n - 2)
    ci_low = beta - t_crit * se
    ci_high = beta + t_crit * se
    return (
        float(beta),
        float(se),
        float(t_stat),
        float(p_value),
        float(r_squared),
        float(ci_low),
        float(ci_high),
    )


def compute_rank_ic(
    signal: pd.Series, forward_return: pd.Series
) -> Tuple[float, int, float, float, float]:
    """Spearman rank IC with Fisher z-test. Returns (rank_ic, n, p_value, ci_low, ci_high)."""
    s, r = _dropna_pair(signal, forward_return)
    n = len(s)
    if n < 4:
        return np.nan, n, np.nan, np.nan, np.nan
    rank_ic, _ = stats.spearmanr(s, r)
    if np.isnan(rank_ic):
        return np.nan, n, np.nan, np.nan, np.nan
    z, se = _fisher_z(rank_ic, n)
    if np.isnan(z):
        return float(rank_ic), n, np.nan, np.nan, np.nan
    z_stat = z / se
    p_value = 2 * (1 - stats.norm.cdf(abs(z_stat)))
    z_lo = z - 1.96 * se
    z_hi = z + 1.96 * se
    ci_low = _z_to_r(z_lo)
    ci_high = _z_to_r(z_hi)
    return float(rank_ic), n, float(p_value), float(ci_low), float(ci_high)
