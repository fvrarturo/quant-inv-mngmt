"""
Load S&P 500 raw data (SP500Raw.xlsx). Column definitions from readme/columns.txt:
  permno - identifier
  date - time and date at month close
  price - average of bid ask price at close
  shrout - shares outstanding in 000's
  prc - total return if money invested in security at period 't-1'
  mcap - market cap of the company in 000's
"""
from pathlib import Path
from typing import Union

import pandas as pd


def load_sp500(path: Union[str, Path]) -> pd.DataFrame:
    """Load SP500Raw.xlsx. Ensures date is datetime and numeric cols are numeric."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Data file not found: {path}")
    if path.suffix.lower() not in (".xlsx", ".xls"):
        raise ValueError("Expected .xlsx or .xls file")
    engine = "openpyxl" if path.suffix.lower() == ".xlsx" else None
    df = pd.read_excel(path, engine=engine)
    # Normalize column names to lowercase
    df = df.rename(columns={c: str(c).strip().lower() for c in df.columns})
    # Parse date
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
    # Coerce numeric
    for col in ["permno", "price", "shrout", "prc", "mcap"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def load_panel(path: Union[str, Path]) -> pd.DataFrame:
    """Load cached full panel CSV (e.g. results/full_panel.csv). Parses date column."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Panel file not found: {path}")
    df = pd.read_csv(path)
    for col in df.columns:
        if col == "date" or "date" in col.lower():
            df[col] = pd.to_datetime(df[col], errors="coerce")
            break
    return df
