"""
Build analysis-ready DataFrame by applying Q1 corrections.
Does not modify the raw data file.
"""
from pathlib import Path
from typing import Union

import numpy as np
import pandas as pd

from .io import load_data, normalize_columns


def build_analysis_ready_df(raw_df_or_path: Union[str, Path, pd.DataFrame]) -> pd.DataFrame:
    """
    Load (if path), normalize, sort, deduplicate, fix monotonicity,
    drop bad prices, replace signal sentinels with NaN. Returns cleaned DataFrame.
    """
    if isinstance(raw_df_or_path, pd.DataFrame):
        df = raw_df_or_path.copy()
    else:
        df = normalize_columns(load_data(raw_df_or_path))

    date_col = "date"
    if date_col not in df.columns:
        date_col = df.columns[0]
    df = df.sort_values(date_col).reset_index(drop=True)

    # Deduplicate: keep first occurrence for each duplicate date
    df = df.drop_duplicates(subset=[date_col], keep="first").reset_index(drop=True)

    # Fix monotonicity: drop the row that is earlier than the previous (backward step)
    ser = pd.to_datetime(df[date_col], errors="coerce")
    backward = ser.diff() < pd.Timedelta(0)
    backward.iloc[0] = False
    if backward.any():
        drop_idx = df.index[backward].tolist()
        df = df.drop(index=drop_idx).reset_index(drop=True)

    # Drop rows with bad prices (adj_close <= 0)
    adj_col = "adj_close" if "adj_close" in df.columns else "price"
    if adj_col in df.columns:
        df = df[df[adj_col] > 0].reset_index(drop=True)

    # Signal sentinels: replace -999 and 0 with NaN
    signal_col = "signal" if "signal" in df.columns else None
    if signal_col is not None:
        df = df.copy()
        df.loc[df[signal_col].isin([-999, 0]), signal_col] = np.nan

    return df


def add_forward_return(df: pd.DataFrame) -> pd.DataFrame:
    """Add forward_return = (adj_close[t+1]/adj_close[t]) - 1. No lookahead."""
    out = df.copy()
    adj_col = "adj_close" if "adj_close" in out.columns else "price"
    out["forward_return"] = out[adj_col].pct_change().shift(-1)
    return out


def add_multi_horizon_targets_and_predictors(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add multi-horizon forward returns (5, 20), forward-looking volatility (5, 20, 60),
    and signal transforms (rolling mean 5/20, pct_change, sign). Expects df with
    forward_return (horizon 1) and adj_close already present.
    """
    out = df.copy()
    adj_col = "adj_close" if "adj_close" in out.columns else "price"
    ret = out[adj_col].pct_change()

    # Forward returns at horizons 5 and 20: (adj_close[t+H]/adj_close[t]) - 1
    for h in (5, 20):
        out[f"forward_return_{h}"] = (out[adj_col].shift(-h) / out[adj_col]) - 1

    # Alias horizon 1 for consistency
    if "forward_return" in out.columns and "forward_return_1" not in out.columns:
        out["forward_return_1"] = out["forward_return"]

    # Forward-looking volatility: std of next H daily returns
    n = len(out)
    for H in (5, 20, 60):
        vol = np.full(n, np.nan, dtype=float)
        for t in range(n - H):
            vol[t] = ret.iloc[t + 1 : t + H + 1].std()
        out[f"forward_vol_{H}"] = vol

    # Signal transforms
    sig = out["signal"] if "signal" in out.columns else None
    if sig is not None:
        out["signal_ma_5"] = sig.rolling(5, min_periods=1).mean()
        out["signal_ma_20"] = sig.rolling(20, min_periods=1).mean()
        out["signal_pct"] = sig.pct_change(fill_method=None)
        out.loc[out["signal_pct"].isin([np.inf, -np.inf]) | out["signal_pct"].isna(), "signal_pct"] = np.nan
        out["sign_signal"] = np.sign(sig)
        out.loc[sig.isna() | (sig == 0), "sign_signal"] = np.nan

    return out


def build_and_save(
    raw_df_or_path: Union[str, Path, pd.DataFrame],
    out_path: Union[str, Path, None] = None,
) -> pd.DataFrame:
    """Build analysis-ready df, add forward return, optionally save to CSV."""
    df = build_analysis_ready_df(raw_df_or_path)
    df = add_forward_return(df)
    if out_path is not None:
        Path(out_path).parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(out_path, index=False)
    return df
