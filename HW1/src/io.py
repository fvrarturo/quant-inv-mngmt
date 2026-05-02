"""
Shared data loading for HW1. Supports CSV and Excel; normalizes column names.
"""
from pathlib import Path
from typing import Union

import pandas as pd


def load_data(path: Union[str, Path]) -> pd.DataFrame:
    """Load dataset from CSV or Excel. Parses date column. Returns raw DataFrame."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Data file not found: {path}")
    suffix = path.suffix.lower()
    if suffix == ".csv":
        df = pd.read_csv(path)
    elif suffix in (".xlsx", ".xls"):
        df = pd.read_excel(path, engine="openpyxl" if suffix == ".xlsx" else None)
    else:
        raise ValueError(f"Unsupported format: {suffix}. Use .csv or .xlsx")
    # Parse date column (any case)
    for col in df.columns:
        if str(col).strip().lower() in ("date", "timestamp", "time"):
            df[col] = pd.to_datetime(df[col], errors="coerce")
            break
    return df


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Map column names to consistent lowercase/snake_case. Returns a copy."""
    out = df.copy()
    rename = {}
    for c in out.columns:
        cl = str(c).strip().lower()
        if cl == "date":
            rename[c] = "date"
        elif cl == "signal":
            rename[c] = "signal"
        elif cl in ("close", "price"):
            rename[c] = "price"
        elif cl == "open":
            rename[c] = "open"
        elif cl == "high":
            rename[c] = "high"
        elif cl == "low":
            rename[c] = "low"
        elif cl in ("adj close", "adj_close"):
            rename[c] = "adj_close"
    if rename:
        out = out.rename(columns=rename)
    # Coerce numeric columns so comparisons (e.g. OHLC) never see str vs float
    numeric_cols = [c for c in ["open", "high", "low", "price", "adj_close", "signal"] if c in out.columns]
    for c in numeric_cols:
        out[c] = pd.to_numeric(out[c], errors="coerce")
    return out
