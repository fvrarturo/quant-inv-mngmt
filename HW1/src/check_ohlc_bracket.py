"""8. OHLC bracket: compute boolean columns high_lt_low, open_not_in_low_high, close_not_in_low_high; append to Treated_datasample.csv."""
from pathlib import Path
import numpy as np
import pandas as pd


def run(df: pd.DataFrame, results_dir: Path, figures_dir: Path) -> None:
    print("=== 8. OHLC bracket check ===")
    low_col = "low" if "low" in df.columns else "Low"
    high_col = "high" if "high" in df.columns else "High"
    open_col = "open" if "open" in df.columns else "Open"
    # Normalized data has "price" (Close); raw may have "Close" or "adj_close"
    clos_col = "price" if "price" in df.columns else ("adj_close" if "adj_close" in df.columns else "Close")
    for c in [low_col, high_col, open_col, clos_col]:
        if c not in df.columns:
            print("Missing column for OHLC check:", c)
            print()
            return
    L = pd.to_numeric(df[low_col], errors="coerce")
    H = pd.to_numeric(df[high_col], errors="coerce")
    O = pd.to_numeric(df[open_col], errors="coerce")
    C = pd.to_numeric(df[clos_col], errors="coerce")
    # high < low (invalid bracket); if so, bracket checks are NaN
    high_lt_low = H < L
    valid_bracket = H >= L
    # open not in [low, high]: violation when valid_bracket, else NaN
    open_not_in_low_high = np.where(valid_bracket, np.logical_not((O >= L) & (O <= H)), np.nan)
    # close (adj) not in [low, high]: same
    close_not_in_low_high = np.where(valid_bracket, np.logical_not((C >= L) & (C <= H)), np.nan)
    out = df.copy()
    out["high_lt_low"] = high_lt_low
    out["open_not_in_low_high"] = open_not_in_low_high
    out["close_not_in_low_high"] = close_not_in_low_high
    treated_path = results_dir.parent / "Treated_datasample.csv"
    out.to_csv(treated_path, index=False)
    n_high_lt_low = int(high_lt_low.sum())
    n_open_not_in = int(np.nansum(open_not_in_low_high))
    n_close_not_in = int(np.nansum(close_not_in_low_high))
    print("Number of violations:")
    print(f"  high < low:                    {n_high_lt_low}")
    print(f"  open not in [low, high]:       {n_open_not_in}")
    print(f"  close not in [low, high]:      {n_close_not_in}")
    print(f"Added columns: high_lt_low, open_not_in_low_high, close_not_in_low_high")
    print(f"Updated {treated_path}\n")
