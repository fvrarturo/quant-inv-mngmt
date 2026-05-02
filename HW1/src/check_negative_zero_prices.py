"""7. Price (Adj Close or Close) <= 0. Table + time series with anomalies highlighted."""
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def run(df: pd.DataFrame, results_dir: Path, figures_dir: Path) -> None:
    print("=== 7. Negative / zero prices ===")
    price_col = "adj_close" if "adj_close" in df.columns else "price"
    date_col = "date" if "date" in df.columns else df.columns[0]
    bad = df[df[price_col] <= 0]
    if bad.empty:
        print("No negative or zero prices.")
        print()
        return
    out = bad[[date_col, price_col]].reset_index().rename(columns={"index": "row_index"})
    print(out.to_string(index=False))
    df_sorted = df.sort_values(date_col).copy()
    df_sorted[date_col] = pd.to_datetime(df_sorted[date_col])
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(df_sorted[date_col], df_sorted[price_col], label="Price", color="steelblue")
    bad_sorted = df_sorted[df_sorted[price_col] <= 0]
    if not bad_sorted.empty:
        ax.scatter(bad_sorted[date_col], bad_sorted[price_col], color="red", s=80, zorder=5, label="Anomaly (<=0)")
    ax.set_xlabel("Date")
    ax.set_ylabel(price_col)
    ax.set_title("Price series with negative/zero anomalies highlighted")
    ax.legend()
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(figures_dir / "negative_zero_prices.png", dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Plot saved: {figures_dir / 'negative_zero_prices.png'}")
    print()

