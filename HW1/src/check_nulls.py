"""1. Null count per column. Terminal table + bar chart."""
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def run(df: pd.DataFrame, results_dir: Path, figures_dir: Path) -> None:
    print("=== 1. Null counts ===")
    n = len(df)
    nulls = df.isna().sum()
    pct = (nulls / n * 100).round(2)
    out = pd.DataFrame({"column": nulls.index, "null_count": nulls.values, "pct": pct.values})
    print(out.to_string(index=False))
    if out["null_count"].sum() > 0:
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.bar(out["column"], out["null_count"], color="steelblue", edgecolor="navy")
        ax.set_ylabel("Null count")
        ax.set_title("Null counts per column")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        plt.savefig(figures_dir / "null_counts.png", dpi=150, bbox_inches="tight")
        plt.close()
        print(f"Plot saved: {figures_dir / 'null_counts.png'}")
    print()

