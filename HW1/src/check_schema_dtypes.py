"""15. Dtypes per column. Print dtypes; save schema_snapshot.csv under results_dir."""
from pathlib import Path
import pandas as pd


def run(df: pd.DataFrame, results_dir: Path, figures_dir: Path) -> None:
    print("=== 15. Schema / dtypes ===")
    dtypes = df.dtypes.astype(str)
    snap = pd.DataFrame({"column": dtypes.index, "dtype": dtypes.values})
    print(snap.to_string(index=False))
    results_dir.mkdir(parents=True, exist_ok=True)
    path = results_dir / "schema_snapshot.csv"
    snap.to_csv(path, index=False)
    print(f"Saved: {path}")
    print()

