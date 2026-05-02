"""11. Sentinel values: -999, runs of zeros. Count and list dates; optional signal timeline."""
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def run(df: pd.DataFrame, results_dir: Path, figures_dir: Path) -> None:
    print("=== 11. Signal sentinels ===")
    signal_col = "signal" if "signal" in df.columns else None
    date_col = "date" if "date" in df.columns else df.columns[0]
    if signal_col not in df.columns:
        print("Missing signal column.")
        print()
        return
    s = df[signal_col]
    n_999 = (s == -999).sum()
    n_zero = (s == 0).sum()
    print(f"Count of -999: {n_999}")
    print(f"Count of 0: {n_zero}")
    if n_999 > 0:
        dates_999 = df.loc[s == -999, date_col].tolist()
        print("Dates with signal = -999:", dates_999[:15], "..." if len(dates_999) > 15 else "")
    if n_zero > 0:
        dates_zero = df.loc[s == 0, date_col].tolist()
        print("Dates with signal = 0 (sample):", dates_zero[:15], "..." if len(dates_zero) > 15 else "")
    df_sorted = df.sort_values(date_col).copy()
    df_sorted[date_col] = pd.to_datetime(df_sorted[date_col])
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(df_sorted[date_col], df_sorted[signal_col], color="steelblue", alpha=0.8, label="Signal")
    sentinel = (df_sorted[signal_col] == -999) | (df_sorted[signal_col] == 0)
    if sentinel.any():
        ax.scatter(df_sorted.loc[sentinel, date_col], df_sorted.loc[sentinel, signal_col], color="red", s=40, zorder=5, label="Sentinel (-999 or 0)")
    ax.set_xlabel("Date")
    ax.set_ylabel("Signal")
    ax.set_title("Signal timeline with sentinel values marked")
    ax.legend()
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(figures_dir / "signal_sentinels_timeline.png", dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Plot saved: {figures_dir / 'signal_sentinels_timeline.png'}")
    print()

