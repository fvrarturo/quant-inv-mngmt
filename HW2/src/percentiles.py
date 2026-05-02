"""
Percentile sets (min, p5, p25, median, p75, p95, max) by date; plotting; entry/exit helpers.
"""
from pathlib import Path
from typing import Optional

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

PERCENTILE_QUANTILES = [0, 0.05, 0.25, 0.5, 0.75, 0.95, 1]
PERCENTILE_LABELS = ["min", "p5", "p25", "median", "p75", "p95", "max"]


def percentile_series_by_date(
    df: pd.DataFrame,
    value_col: str,
    date_col: str = "date",
) -> pd.DataFrame:
    """Group by date, compute quantiles of value_col. Index=date, columns=PERCENTILE_LABELS."""
    out = df.groupby(date_col)[value_col].quantile(PERCENTILE_QUANTILES).unstack()
    out.columns = PERCENTILE_LABELS
    return out


def plot_percentile_timeseries(
    series_by_date: pd.DataFrame,
    title: str,
    path: Path,
) -> None:
    """Plot 7 lines (one per percentile). x=index (date), y=value. Save to path."""
    fig, ax = plt.subplots(figsize=(10, 5))
    for col in PERCENTILE_LABELS:
        if col in series_by_date.columns:
            ax.plot(series_by_date.index, series_by_date[col], label=col, alpha=0.8)
    ax.set_xlabel("Date")
    ax.set_ylabel("Value")
    ax.set_title(title)
    ax.legend(loc="best", fontsize=8)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()


def median_of_percentiles(series_by_date: pd.DataFrame) -> pd.Series:
    """For each percentile column, median over the time index. Return Series."""
    return series_by_date.median()


def panel_entry_exit_dates(df: pd.DataFrame, date_col: str = "date") -> pd.DataFrame:
    """For each permno, first and last date in panel. Columns: permno, first_date, last_date."""
    agg = df.groupby("permno")[date_col].agg(["min", "max"])
    agg = agg.rename(columns={"min": "first_date", "max": "last_date"})
    return agg.reset_index()


def subset_month_before_exit(
    df: pd.DataFrame,
    entry_exit_df: pd.DataFrame,
    date_col: str = "date",
) -> pd.DataFrame:
    """Rows where (permno, date) is the month prior to last_date for that permno."""
    # last_date is EOM; "month prior to leaving" = one month before last_date
    merged = df.merge(
        entry_exit_df[["permno", "last_date"]],
        on="permno",
        how="inner",
    )
    # Approximate "one month before" by pd.DateOffset(months=1)
    merged["prev_of_last"] = merged["last_date"] - pd.DateOffset(months=1)
    return merged[merged[date_col] == merged["prev_of_last"]].drop(
        columns=["last_date", "prev_of_last"], errors="ignore"
    )


def subset_month_of_entry(
    df: pd.DataFrame,
    entry_exit_df: pd.DataFrame,
    date_col: str = "date",
) -> pd.DataFrame:
    """Rows where (permno, date) equals first_date (month they enter)."""
    merged = df.merge(
        entry_exit_df[["permno", "first_date"]],
        on="permno",
        how="inner",
    )
    return merged[merged[date_col] == merged["first_date"]].drop(
        columns=["first_date"], errors="ignore"
    )


def percentile_set_cross_section(df: pd.DataFrame, value_col: str) -> pd.Series:
    """Single set of percentiles over one cross-section (one value per label)."""
    s = df[value_col].quantile(PERCENTILE_QUANTILES)
    s.index = PERCENTILE_LABELS
    return s
