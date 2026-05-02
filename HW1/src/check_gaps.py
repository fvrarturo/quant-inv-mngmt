"""16. Consecutive date gaps > N calendar days. Table + bar/histogram of gap lengths."""
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def run(df: pd.DataFrame, results_dir: Path, figures_dir: Path) -> None:
    print("=== 16. Date gaps ===")
    date_col = "date" if "date" in df.columns else df.columns[0]
    min_gap_days = 5
    ser = pd.to_datetime(df[date_col], errors="coerce").dropna()
    if len(ser) < 2:
        print("Insufficient dates.")
        print()
        return
    df_sorted = df.sort_values(date_col).copy()
    ser = pd.to_datetime(df_sorted[date_col], errors="coerce")
    diff = ser.diff().dt.days
    big = diff > min_gap_days
    big.iloc[0] = False
    if not big.any():
        print(f"No gaps > {min_gap_days} calendar days.")
        print()
        return
    rows = []
    for idx in df_sorted.index[big]:
        gap_days = int(diff.loc[idx])
        gap_start = ser.shift(1).loc[idx]
        gap_end = ser.loc[idx]
        rows.append({"gap_start": gap_start, "gap_end": gap_end, "gap_days": gap_days})
    out = pd.DataFrame(rows)
    print(out.to_string(index=False))
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(range(len(out)), out["gap_days"], color="coral", edgecolor="darkred")
    ax.set_xticks(range(len(out)))
    ax.set_xticklabels([str(out.loc[i, "gap_start"])[:10] for i in out.index], rotation=45, ha="right")
    ax.set_ylabel("Gap (calendar days)")
    ax.set_title(f"Gaps > {min_gap_days} days between consecutive dates")
    plt.tight_layout()
    plt.savefig(figures_dir / "gaps.png", dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Plot saved: {figures_dir / 'gaps.png'}")
    print()

