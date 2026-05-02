"""17. Summary counts of all issue types. Re-runs minimal checks; one table + optional bar."""
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def _count_nulls(df: pd.DataFrame) -> int:
    return int(df.isna().sum().sum())


def _count_duplicate_dates(df: pd.DataFrame) -> int:
    date_col = "date" if "date" in df.columns else df.columns[0]
    return int(df.duplicated(subset=[date_col], keep=False).sum())


def _count_monotonic_violations(df: pd.DataFrame) -> int:
    date_col = "date" if "date" in df.columns else df.columns[0]
    ser = pd.to_datetime(df[date_col], errors="coerce")
    diff = ser.diff()
    return int((diff < pd.Timedelta(0)).sum())


def _count_negative_zero_prices(df: pd.DataFrame) -> int:
    price_col = "adj_close" if "adj_close" in df.columns else "price"
    if price_col not in df.columns:
        return 0
    return int((df[price_col] <= 0).sum())


def _count_return_outliers(df: pd.DataFrame, threshold_pct: float = 20.0) -> int:
    price_col = "adj_close" if "adj_close" in df.columns else "price"
    if price_col not in df.columns:
        return 0
    ret = df[price_col].pct_change().abs() * 100
    ret.iloc[0] = 0
    return int((ret > threshold_pct).sum())


def _count_signal_sentinels(df: pd.DataFrame) -> int:
    signal_col = "signal" if "signal" in df.columns else None
    if signal_col is None:
        return 0
    return int(((df[signal_col] == -999) | (df[signal_col] == 0)).sum())


def _count_ohlc_violations(df: pd.DataFrame) -> int:
    low_col = "low" if "low" in df.columns else "Low"
    high_col = "high" if "high" in df.columns else "High"
    adj_col = "adj_close" if "adj_close" in df.columns else "Adj Close"
    if not all(c in df.columns for c in [low_col, high_col, adj_col]):
        return 0
    L = pd.to_numeric(df[low_col], errors="coerce")
    H = pd.to_numeric(df[high_col], errors="coerce")
    C = pd.to_numeric(df[adj_col], errors="coerce")
    return int(((C < L) | (C > H) | (H < L)).sum())


def _count_gaps(df: pd.DataFrame, min_days: int = 5) -> int:
    date_col = "date" if "date" in df.columns else df.columns[0]
    ser = pd.to_datetime(df.sort_values(date_col)[date_col], errors="coerce")
    diff = ser.diff().dt.days
    diff.iloc[0] = 0
    return int((diff > min_days).sum())


def run(df: pd.DataFrame, results_dir: Path, figures_dir: Path) -> None:
    print("=== 17. Issue summary ===")
    counts = [
        ("null_values", _count_nulls(df)),
        ("duplicate_dates", _count_duplicate_dates(df)),
        ("monotonic_violations", _count_monotonic_violations(df)),
        ("negative_zero_prices", _count_negative_zero_prices(df)),
        ("return_outliers_20pct", _count_return_outliers(df)),
        ("signal_sentinels", _count_signal_sentinels(df)),
        ("ohlc_bracket_violations", _count_ohlc_violations(df)),
        ("gaps_gt_5_days", _count_gaps(df)),
    ]
    out = pd.DataFrame(counts, columns=["check_name", "count"])
    print(out.to_string(index=False))
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.barh(out["check_name"], out["count"], color="steelblue", edgecolor="navy")
    ax.set_xlabel("Count")
    ax.set_title("Issue summary (counts by check)")
    plt.tight_layout()
    plt.savefig(figures_dir / "issue_summary.png", dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Plot saved: {figures_dir / 'issue_summary.png'}")
    print()

