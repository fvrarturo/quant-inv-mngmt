"""9. Adj Close vs Close mismatch. Count, table, scatter with identity line."""
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def run(df: pd.DataFrame, results_dir: Path, figures_dir: Path) -> None:
    print("=== 9. Adj Close vs Close ===")
    price_col = "price" if "price" in df.columns else "Close"
    adj_col = "adj_close" if "adj_close" in df.columns else "Adj Close"
    if price_col not in df.columns or adj_col not in df.columns:
        print("Missing price or adj_close column.")
        print()
        return
    tol = 1e-6
    diff = (df[adj_col] - df[price_col]).abs()
    mismatch = diff > tol
    n = mismatch.sum()
    print(f"Mismatch count (|Adj Close - Close| > {tol}): {n}")
    if n > 0:
        out = df.loc[mismatch, [price_col, adj_col]].copy()
        out["diff"] = diff[mismatch]
        print(out.head(20).to_string())
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.scatter(df[price_col], df[adj_col], alpha=0.5, s=10, label="Observed")
    mn = min(df[price_col].min(), df[adj_col].min())
    mx = max(df[price_col].max(), df[adj_col].max())
    ax.plot([mn, mx], [mn, mx], "k--", label="Identity", linewidth=1)
    ax.set_xlabel("Close (price)")
    ax.set_ylabel("Adj Close")
    ax.set_title("Adj Close vs Close")
    ax.legend()
    plt.tight_layout()
    plt.savefig(figures_dir / "adj_vs_close.png", dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Plot saved: {figures_dir / 'adj_vs_close.png'}")
    print()

