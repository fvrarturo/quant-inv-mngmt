"""2. Duplicate calendar dates. List dates with count and row indices; bar chart."""
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def run(df: pd.DataFrame, results_dir: Path, figures_dir: Path) -> None:
    print("=== 2. Duplicate dates ===")
    date_col = "date" if "date" in df.columns else df.columns[0]
    dup = df.groupby(date_col).size()
    dup = dup[dup > 1]
    if dup.empty:
        print("No duplicate dates.")
        print()
        return
    for d, count in dup.items():
        rows = df.index[df[date_col] == d].tolist()
        print(f"  {d}: {count} copies, row indices: {rows}")
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(range(len(dup)), dup.values, color="coral", edgecolor="darkred")
    ax.set_xticks(range(len(dup)))
    ax.set_xticklabels([str(d)[:10] for d in dup.index], rotation=45, ha="right")
    ax.set_ylabel("Duplicate count")
    ax.set_title("Duplicate dates")
    plt.tight_layout()
    plt.savefig(figures_dir / "duplicate_dates.png", dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Plot saved: {figures_dir / 'duplicate_dates.png'}")
    print()

