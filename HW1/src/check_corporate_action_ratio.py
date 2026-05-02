"""14. Adj Close / Close ratio; abrupt % change. Table + time series of ratio."""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def run(df: pd.DataFrame, results_dir: Path, figures_dir: Path) -> None:
    print("=== 14. Corporate action ratio ===")
    price_col = "price" if "price" in df.columns else "Close"
    adj_col = "adj_close" if "adj_close" in df.columns else "Adj Close"
    date_col = "date" if "date" in df.columns else df.columns[0]
    if price_col not in df.columns or adj_col not in df.columns:
        print("Missing price or adj_close.")
        print()
        return
    ratio = df[adj_col] / df[price_col].replace(0, np.nan)
    r = ratio.pct_change().abs()
    threshold = 0.05
    abrupt = r > threshold
    abrupt.iloc[0] = False
    if not abrupt.any():
        print(f"No abrupt ratio changes (threshold {threshold:.0%}).")
    else:
        out = df.loc[abrupt, [date_col, price_col, adj_col]].copy()
        out["ratio"] = ratio[abrupt].values
        out["pct_change_ratio"] = r[abrupt].values
        print(out.to_string(index=False))
    df_sorted = df.sort_values(date_col).copy()
    df_sorted[date_col] = pd.to_datetime(df_sorted[date_col])
    df_sorted["ratio"] = df_sorted[adj_col] / df_sorted[price_col].replace(0, np.nan)
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(df_sorted[date_col], df_sorted["ratio"], color="steelblue")
    ax.set_xlabel("Date")
    ax.set_ylabel("Adj Close / Close")
    ax.set_title("Corporate action ratio over time")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(figures_dir / "corporate_action_ratio.png", dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Plot saved: {figures_dir / 'corporate_action_ratio.png'}")
    print()

