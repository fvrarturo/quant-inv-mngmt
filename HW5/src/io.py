"""
Data loaders for HW5.

Column definitions (see readme.md):
  data.xlsx:      date, mrap_id, naics, price, vol, ret, shrout
  factors.xlsx:   date, factor_1..factor_5, rf
  estimates.xlsx: mrap_id, naics, price, ret, shrout, pred
"""
from __future__ import annotations

from pathlib import Path
from typing import Tuple

import numpy as np
import pandas as pd

HW5_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = HW5_DIR / "data.xlsx"
FACTORS_PATH = HW5_DIR / "factors.xlsx"
ESTIMATES_PATH = HW5_DIR / "estimates.xlsx"

FACTOR_COLS = ["factor_1", "factor_2", "factor_3", "factor_4", "factor_5"]
TARGET_SECTORS = [52, 33, 32, 51, 54, 53, 22, 21, 56, 31]


def load_panel(path: Path = DATA_PATH) -> pd.DataFrame:
    df = pd.read_excel(path, engine="openpyxl")
    df["date"] = pd.to_datetime(df["date"])
    df["mrap_id"] = df["mrap_id"].astype(int)
    return df.sort_values(["mrap_id", "date"]).reset_index(drop=True)


def load_factors(path: Path = FACTORS_PATH) -> pd.DataFrame:
    df = pd.read_excel(path, engine="openpyxl")
    df["date"] = pd.to_datetime(df["date"])
    return df.sort_values("date").reset_index(drop=True)


def load_estimates(path: Path = ESTIMATES_PATH) -> pd.DataFrame:
    df = pd.read_excel(path, engine="openpyxl")
    df["mrap_id"] = df["mrap_id"].astype(int)
    df["sector"] = df["naics"].astype(int).astype(str).str[:2].astype(int)
    return df.sort_values("mrap_id").reset_index(drop=True)


def build_returns_matrix(
    panel: pd.DataFrame, factors: pd.DataFrame
) -> Tuple[pd.DataFrame, np.ndarray, np.ndarray]:
    """Pivot panel returns to R (n x T) aligned with F (5 x T).

    Missing cells in R are left NaN. The caller decides how to treat them.
    Returns
    -------
    R_df : DataFrame indexed by mrap_id, columns are dates (sorted), values are returns.
    F    : ndarray (5 x T), factor returns matrix.
    dates: ndarray of dates corresponding to columns of R_df / F.
    """
    dates = factors["date"].values
    R_df = (
        panel.pivot(index="mrap_id", columns="date", values="ret")
        .reindex(columns=dates)
        .sort_index()
    )
    F = factors[FACTOR_COLS].to_numpy().T  # 5 x T
    return R_df, F, dates


def assign_sector(naics_series: pd.Series) -> pd.Series:
    """First-two-digits sector from NAICS."""
    return naics_series.astype(int).astype(str).str[:2].astype(int)


def average_monthly_volume(panel: pd.DataFrame) -> pd.Series:
    """Average historical monthly share volume per stock (vol column is in hundreds)."""
    return panel.groupby("mrap_id")["vol"].mean().mul(100.0)  # convert to shares
