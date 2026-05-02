"""4. Dates must be non-decreasing. Table: row_index, date, previous_date."""
from pathlib import Path
import pandas as pd


def run(df: pd.DataFrame, results_dir: Path, figures_dir: Path) -> None:
    print("=== 4. Monotonic dates ===")
    date_col = "date" if "date" in df.columns else df.columns[0]
    ser = pd.to_datetime(df[date_col], errors="coerce")
    diff = ser.diff()
    backward = diff < pd.Timedelta(0)
    backward.iloc[0] = False
    if not backward.any():
        print("Dates are monotonic (non-decreasing).")
        print()
        return
    viol = df.loc[backward].copy()
    viol["previous_date"] = ser.shift(1).loc[backward].values
    viol = viol[[date_col, "previous_date"]].reset_index().rename(columns={"index": "row_index", date_col: "date"})
    print(viol.to_string(index=False))
    print()

