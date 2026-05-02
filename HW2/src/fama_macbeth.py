"""
Fama-MacBeth: cross-sectional OLS/WLS by date, time-series inference, Newey-West, strategy metrics.
"""
from typing import Dict, List, Optional

import numpy as np
import pandas as pd

try:
    import statsmodels.api as sm
    HAS_STATS = True
except ImportError:
    HAS_STATS = False

MIN_OBS = 30  # minimum observations per cross-section


def cross_sectional_ols(
    y: pd.Series,
    X: pd.DataFrame,
    weights: Optional[pd.Series] = None,
) -> Dict:
    """
    Single cross-section: regress y on X (with constant).
    Returns dict: coef (Series), r_squared, stderr (Series), t_stat (Series).
    """
    valid = y.notna() & X.notna().all(axis=1)
    y_ = y.loc[valid].values
    X_ = X.loc[valid].values
    if weights is not None:
        w = weights.loc[valid].values.astype(float)
    else:
        w = None
    n, k = X_.shape
    if n < 2 or (X_.std(axis=0) == 0).any():
        return {
            "coef": pd.Series(index=X.columns, dtype=float),
            "r_squared": np.nan,
            "stderr": pd.Series(index=X.columns, dtype=float),
            "t_stat": pd.Series(index=X.columns, dtype=float),
        }
    X_const = np.column_stack([np.ones(n), X_])
    if HAS_STATS:
        if w is not None:
            model = sm.WLS(y_, X_const, weights=w, hasconst=True)
        else:
            model = sm.OLS(y_, X_const, hasconst=True)
        res = model.fit()
        coef = pd.Series(res.params[1:], index=X.columns)
        stderr = pd.Series(res.bse[1:], index=X.columns)
        t_stat = pd.Series(res.tvalues[1:], index=X.columns)
        return {
            "coef": coef,
            "r_squared": res.rsquared,
            "stderr": stderr,
            "t_stat": t_stat,
        }
    # Fallback: numpy OLS (X'X)^{-1} X'y
    if w is not None:
        W = np.diag(np.sqrt(w))
        y_ = W @ y_
        X_const = W @ X_const
    XX = X_const.T @ X_const
    Xy = X_const.T @ y_
    try:
        beta = np.linalg.solve(XX, Xy)
    except np.linalg.LinAlgError:
        beta = np.full(X_const.shape[1], np.nan)
    resid = y_ - X_const @ beta
    r_sq = 1 - (resid @ resid) / ((y_ - y_.mean()) ** 2).sum() if n > 1 else np.nan
    sig_sq = (resid @ resid) / max(n - X_const.shape[1], 1)
    try:
        var_beta = sig_sq * np.linalg.inv(XX)
        se = np.sqrt(np.diag(var_beta))[1:]
    except Exception:
        se = np.full(len(X.columns), np.nan)
    coef = pd.Series(beta[1:], index=X.columns)
    stderr = pd.Series(se, index=X.columns)
    t_stat = coef / stderr.replace(0, np.nan)
    return {
        "coef": coef,
        "r_squared": r_sq,
        "stderr": stderr,
        "t_stat": t_stat,
    }


def run_fama_macbeth(
    panel: pd.DataFrame,
    y_col: str,
    x_cols: List[str],
    weight_col: Optional[str] = None,
    date_col: str = "date",
    min_obs: int = MIN_OBS,
) -> pd.DataFrame:
    """
    Run cross-sectional regression for each date. Returns DataFrame index=date, columns=x_cols (coefficients).
    Drops dates with fewer than min_obs valid observations.
    """
    rows = []
    r2_list = []
    for date, g in panel.groupby(date_col):
        y = g[y_col]
        X = g[x_cols]
        weights = g[weight_col] if weight_col and weight_col in g.columns else None
        valid = y.notna() & X.notna().all(axis=1)
        if valid.sum() < min_obs:
            continue
        res = cross_sectional_ols(y, X, weights)
        rows.append({**res["coef"], "_date": date})
        r2_list.append(res["r_squared"])
    if not rows:
        return pd.DataFrame(columns=x_cols)
    out = pd.DataFrame(rows).set_index("_date")
    out.index.name = date_col
    return out


def fama_macbeth_inference(coef_series: pd.Series) -> Dict:
    """Time-series inference: mean, std, t-stat = mean/(se), p-value (two-tailed)."""
    c = coef_series.dropna()
    T = len(c)
    if T == 0:
        return {"mean": np.nan, "std": np.nan, "t_stat": np.nan, "p_value": np.nan, "n_dates": 0}
    mean = c.mean()
    std = c.std()
    se = std / np.sqrt(T) if T > 1 else np.nan
    t_stat = mean / se if se and se > 0 else np.nan
    from scipy import stats as scipy_stats
    p_value = 2 * (1 - scipy_stats.t.cdf(abs(t_stat), T - 1)) if T > 1 and not np.isnan(t_stat) else np.nan
    return {
        "mean": mean,
        "std": std,
        "t_stat": t_stat,
        "p_value": p_value,
        "n_dates": T,
    }


def newey_west_t_stat(
    coef_series: pd.Series,
    max_lags: Optional[int] = None,
) -> Dict:
    """HAC standard error and t-stat for the mean coefficient. max_lags default 6."""
    c = coef_series.dropna()
    T = len(c)
    if T == 0:
        return {"mean": np.nan, "se_hac": np.nan, "t_stat": np.nan, "p_value": np.nan}
    mean = c.mean()
    if max_lags is None:
        max_lags = min(6, T // 2)
    # Newey-West: variance of mean = (1/T) * sum_l (1 - l/(max_lags+1)) * gamma(l)
    demeaned = c - mean
    gamma0 = (demeaned ** 2).mean()
    var = gamma0 / T
    for lag in range(1, max_lags + 1):
        if lag < T:
            cov_lag = (demeaned.iloc[:-lag].values * demeaned.iloc[lag:].values).mean()
            weight = 1 - lag / (max_lags + 1)
            var += 2 * weight * cov_lag / T
    se_hac = np.sqrt(max(var, 0))
    t_stat = mean / se_hac if se_hac > 0 else np.nan
    from scipy import stats as scipy_stats
    p_value = 2 * (1 - scipy_stats.t.cdf(abs(t_stat), T - 1)) if not np.isnan(t_stat) else np.nan
    return {
        "mean": mean,
        "se_hac": se_hac,
        "t_stat": t_stat,
        "p_value": p_value,
        "n_dates": T,
    }


def strategy_metrics(coef_series: pd.Series) -> Dict:
    """Treat time-series of coefficient as strategy return: hit rate, cum return, max DD, Sortino."""
    c = coef_series.dropna()
    if len(c) == 0:
        return {"hit_rate": np.nan, "cum_return": np.nan, "max_drawdown": np.nan, "sortino": np.nan}
    hit_rate = (c > 0).mean()
    cum = (1 + c).cumprod()
    cum_return = cum.iloc[-1] - 1 if len(cum) > 0 else np.nan
    run_max = cum.cummax()
    drawdown = (cum - run_max) / run_max.replace(0, np.nan)
    max_drawdown = drawdown.min()
    downside = c[c < 0]
    downside_std = np.sqrt((downside ** 2).mean()) if len(downside) > 0 else 0
    sortino = c.mean() / downside_std if downside_std > 0 else np.nan
    return {
        "hit_rate": hit_rate,
        "cum_return": cum_return,
        "max_drawdown": max_drawdown,
        "sortino": sortino,
    }
