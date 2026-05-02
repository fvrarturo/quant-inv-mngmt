"""10. Single-period return |r| > threshold (e.g. 20%). Table + histogram with outliers marked."""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def run(df: pd.DataFrame, results_dir: Path, figures_dir: Path) -> None:
    print("=== 10. Return outliers ===")
    price_col = "adj_close" if "adj_close" in df.columns else "price"
    date_col = "date" if "date" in df.columns else df.columns[0]
    if price_col not in df.columns:
        print("Missing price column.")
        print()
        return
    threshold_pct = 20.0
    df_sorted = df.sort_values(date_col).copy()
    ret = df_sorted[price_col].pct_change() * 100
    outlier = ret.abs() > threshold_pct
    outlier.iloc[0] = False
    if not outlier.any():
        print(f"No single-period returns with |r| > {threshold_pct}%.")
        print()
        return
    out = df_sorted.loc[outlier, [date_col]].copy()
    out["return_pct"] = ret[outlier].values
    out = out.reset_index().rename(columns={"index": "row_index"})
    print(out.to_string(index=False))
    fig, ax = plt.subplots(figsize=(10, 5))
    ret_clean = ret.replace([np.inf, -np.inf], np.nan).dropna()
    ret_clean = ret_clean[np.isfinite(ret_clean)]
    if len(ret_clean) > 0:
        ax.hist(ret_clean, bins=50, color="steelblue", edgecolor="navy", alpha=0.7, label="All returns (finite)")
    ax.axvline(threshold_pct, color="red", linestyle="--", label=f"±{threshold_pct}%")
    ax.axvline(-threshold_pct, color="red", linestyle="--")
    ax.set_xlabel("Return (%)")
    ax.set_ylabel("Count")
    ax.set_title("Distribution of single-period returns (outlier threshold ±20%)")
    ax.legend()
    plt.tight_layout()
    plt.savefig(figures_dir / "return_outliers_hist.png", dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Plot saved: {figures_dir / 'return_outliers_hist.png'}")
    print()

