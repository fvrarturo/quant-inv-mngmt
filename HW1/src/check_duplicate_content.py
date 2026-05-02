"""3. For each duplicate date: compare OHLC + signal. Table: date, n_copies, identical, recommendation."""
from pathlib import Path
import pandas as pd


def run(df: pd.DataFrame, results_dir: Path, figures_dir: Path) -> None:
    print("=== 3. Duplicate content audit ===")
    date_col = "date" if "date" in df.columns else df.columns[0]
    content_cols = [c for c in ["open", "high", "low", "price", "signal", "adj_close"] if c in df.columns]
    dup_dates = df[df.duplicated(subset=[date_col], keep=False)][date_col].unique()
    if len(dup_dates) == 0:
        print("No duplicate dates to audit.")
        print()
        return
    rows = []
    for d in dup_dates:
        block = df[df[date_col] == d][content_cols].dropna(axis=1, how="all")
        if len(block) <= 1:
            continue
        same = block.nunique().eq(1).all()
        rec = "keep_first_drop_rest" if same else "vendor_conflict_escalate"
        rows.append({"date": d, "n_copies": len(block), "identical": "Y" if same else "N", "recommendation": rec})
    out = pd.DataFrame(rows)
    print(out.to_string(index=False))
    print()

