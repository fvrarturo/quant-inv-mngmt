"""12. Signal z-score; flag |z| > 5. Count, table, distribution with fences."""
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def run(df: pd.DataFrame, results_dir: Path, figures_dir: Path) -> None:
    print("=== 12. Signal z-score ===")
    signal_col = "signal" if "signal" in df.columns else None
    date_col = "date" if "date" in df.columns else df.columns[0]
    if signal_col not in df.columns:
        print("Missing signal column.")
        print()
        return
    s = df[signal_col].dropna()
    if len(s) < 2:
        print("Insufficient signal data.")
        print()
        return
    mean, std = s.mean(), s.std()
    if std == 0:
        z = pd.Series(0.0, index=s.index)
    else:
        z = (df.loc[s.index, signal_col] - mean) / std
    threshold = 5.0
    suspect = np.abs(z) > threshold
    n = suspect.sum()
    print(f"Rows with |z| > {threshold}: {n}")
    if n > 0:
        out = df.loc[z.index[suspect], [date_col, signal_col]].copy()
        out["z_score"] = z[suspect].values
        print(out.head(20).to_string())
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.hist(df[signal_col].dropna(), bins=50, color="steelblue", edgecolor="navy", alpha=0.7, density=True, label="Signal")
    if std > 0:
        for mult in [-threshold, threshold]:
            ax.axvline(mean + mult * std, color="red", linestyle="--", label=f"z=±{threshold}" if mult == threshold else None)
    ax.set_xlabel("Signal")
    ax.set_ylabel("Density")
    ax.set_title(f"Signal distribution with z=±{threshold} fences")
    ax.legend()
    plt.tight_layout()
    plt.savefig(figures_dir / "signal_zscore_fences.png", dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Plot saved: {figures_dir / 'signal_zscore_fences.png'}")
    print()

