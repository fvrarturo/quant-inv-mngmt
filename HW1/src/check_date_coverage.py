"""5. Business-day calendar vs observed; missing sessions per year. Bar: missing per year."""
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def run(df: pd.DataFrame, results_dir: Path, figures_dir: Path) -> None:
    print("=== 5. Date coverage ===")
    date_col = "date" if "date" in df.columns else df.columns[0]
    ser = pd.to_datetime(df[date_col], errors="coerce").dropna()
    if ser.empty:
        print("No valid dates.")
        print()
        return
    min_d, max_d = ser.min(), ser.max()
    calendar = pd.bdate_range(start=min_d, end=max_d)
    observed = set(ser.dt.normalize().astype("datetime64[ns]"))
    missing = [d for d in calendar if d not in observed]
    if not missing:
        print("No missing business days (full coverage).")
        print()
        return
    missing_ser = pd.Series(missing)
    by_year = missing_ser.dt.year.value_counts().sort_index()
    print("Missing sessions by year:")
    print(by_year.to_string())
    print(f"Sample missing dates (first 10): {missing[:10]}")
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(by_year.index.astype(str), by_year.values, color="steelblue", edgecolor="navy")
    ax.set_xlabel("Year")
    ax.set_ylabel("Missing sessions")
    ax.set_title("Missing trading sessions per year (vs US business-day calendar)")
    plt.tight_layout()
    plt.savefig(figures_dir / "date_coverage_missing_by_year.png", dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Plot saved: {figures_dir / 'date_coverage_missing_by_year.png'}")
    print()

