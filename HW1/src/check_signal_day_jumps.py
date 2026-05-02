"""13. Day-over-day signal change > K sigma. Table: row_index, date, change, sigma."""
from pathlib import Path
import pandas as pd
import numpy as np


def run(df: pd.DataFrame, results_dir: Path, figures_dir: Path) -> None:
    print("=== 13. Signal day-over-day jumps ===")
    signal_col = "signal" if "signal" in df.columns else None
    date_col = "date" if "date" in df.columns else df.columns[0]
    if signal_col not in df.columns:
        print("Missing signal column.")
        print()
        return
    df_sorted = df.sort_values(date_col).copy()
    s = df_sorted[signal_col]
    diff = s.diff().abs()
    std = s.std()
    if std == 0 or pd.isna(std):
        print("Signal has zero variance.")
        print()
        return
    K = 5.0
    shift_sigma = diff / std
    big = shift_sigma > K
    big.iloc[0] = False
    if not big.any():
        print(f"No day-over-day signal changes > {K} sigma.")
        print()
        return
    out = df_sorted.loc[big, [date_col, signal_col]].copy()
    out["change"] = diff[big].values
    out["sigma"] = shift_sigma[big].values
    out = out.reset_index().rename(columns={"index": "row_index"})
    print(out.to_string(index=False))
    print()

