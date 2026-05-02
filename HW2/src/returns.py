"""
Build full panel with all trailing and forward returns (geometric).
Column names: Price_Ret_T1, PRC_Ret_T12, Prices_Ret_T12, PRC_Ret_T12M1, Prices_Ret_T12M1,
PRC_Ret_T12_1M, Prices_Ret_T12_1M, Vol_Prices_Ret_T12M1, SR_Prices_Ret_T12M1,
PRC_Ret_F1M, PRC_Ret_F3M, PRC_Ret_F6M.
"""
import numpy as np
import pandas as pd


def _rolling_prod_minus_one(series: pd.Series, window: int) -> pd.Series:
    """(1+r1)*...*(1+r_window) - 1 for each window. Requires min_periods=window."""
    one_plus = 1 + series
    return one_plus.rolling(window, min_periods=window).apply(
        lambda x: x.prod() - 1, raw=True
    )


def build_full_panel(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add all return columns. Input must have permno, date, price, prc, mcap.
    Sorted by permno, date. All multi-period returns are geometric.
    """
    out = df.sort_values(["permno", "date"]).copy()
    g = out.groupby("permno", group_keys=False)

    # --- Price_Ret_T1: one-month price return ---
    out["Price_Ret_T1"] = (out["price"] / out.groupby("permno")["price"].shift(1)) - 1

    # --- Trailing 12m from prc (months t-11..t) ---
    out["PRC_Ret_T12"] = g["prc"].transform(
        lambda x: _rolling_prod_minus_one(x, 12)
    )

    # --- Trailing 12m from prices (same window) ---
    out["Prices_Ret_T12"] = g["Price_Ret_T1"].transform(
        lambda x: _rolling_prod_minus_one(x, 12)
    )

    # --- 11 months t-12 to t-2 (exclude most recent month): product of (1+r) at t-11..t-1 ---
    out["PRC_Ret_T12M1"] = g["prc"].transform(
        lambda x: (1 + x).shift(1).rolling(11, min_periods=11).apply(
            lambda y: np.prod(y) - 1, raw=True
        )
    )
    out["Prices_Ret_T12M1"] = g["Price_Ret_T1"].transform(
        lambda x: (1 + x).shift(1).rolling(11, min_periods=11).apply(
            lambda y: np.prod(y) - 1, raw=True
        )
    )

    # --- One month at t-12 ---
    out["PRC_Ret_T12_1M"] = g["prc"].shift(12)
    out["Prices_Ret_T12_1M"] = g["Price_Ret_T1"].shift(12)

    # --- Vol and SR for price-based T12M1 ---
    # Std of the 11 monthly returns (t-11..t-1) = shift(1).rolling(11).std()
    out["Vol_Prices_Ret_T12M1"] = g["Price_Ret_T1"].transform(
        lambda x: x.shift(1).rolling(11, min_periods=11).std()
    )
    out["SR_Prices_Ret_T12M1"] = out["Prices_Ret_T12M1"] / out["Vol_Prices_Ret_T12M1"]
    out.loc[out["Vol_Prices_Ret_T12M1"] <= 0, "SR_Prices_Ret_T12M1"] = np.nan

    # --- Forward returns (point-in-time): F1M = prc at t+1 ---
    out["PRC_Ret_F1M"] = g["prc"].shift(-1)
    # F3M: (1+r_{t+1})*(1+r_{t+2})*(1+r_{t+3}) - 1
    out["PRC_Ret_F3M"] = g["prc"].transform(
        lambda x: (1 + x.shift(-1)) * (1 + x.shift(-2)) * (1 + x.shift(-3)) - 1
    )
    # F6M: 6 months forward
    out["PRC_Ret_F6M"] = g["prc"].transform(
        lambda x: (
            (1 + x.shift(-1)) * (1 + x.shift(-2)) * (1 + x.shift(-3))
            * (1 + x.shift(-4)) * (1 + x.shift(-5)) * (1 + x.shift(-6))
        ) - 1
    )

    # --- log_mcap for Q10 weighted regression ---
    out["log_mcap"] = np.log(out["mcap"].clip(lower=1e-6))

    return out
