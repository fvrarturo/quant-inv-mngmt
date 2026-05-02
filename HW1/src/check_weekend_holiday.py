"""6. Flag weekend (Sat/Sun) in date series. Count and list."""
from pathlib import Path
import pandas as pd


def run(df: pd.DataFrame, results_dir: Path, figures_dir: Path) -> None:
    print("=== 6. Weekend / holiday check ===")
    date_col = "date" if "date" in df.columns else df.columns[0]
    ser = pd.to_datetime(df[date_col], errors="coerce").dropna()
    if ser.empty:
        print("No valid dates.")
        print()
        return
    # 5=Saturday, 6=Sunday
    weekend = ser.dt.dayofweek >= 5
    n_weekend = weekend.sum()
    print(f"Weekend dates count: {n_weekend}")
    if n_weekend > 0:
        weekend_dates = ser[weekend].dt.normalize().unique()
        print("Weekend dates (sample, max 20):")
        for d in list(weekend_dates)[:20]:
            print(f"  {d}")
        if len(weekend_dates) > 20:
            print(f"  ... and {len(weekend_dates) - 20} more")
    print()

