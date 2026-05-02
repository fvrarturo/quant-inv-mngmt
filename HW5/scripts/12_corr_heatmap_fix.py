#!/usr/bin/env python3
"""
Re-generate the 1000x1000 correlation heat-map for Omega_R with sensible row
ordering so the sector block structure is visible. The original heat-map
showed rows / columns in arbitrary mrap_id order, which is the reason we
could not see the sector blocks that are clearly present in within-vs-cross
sector statistics.

We produce three versions:
  (a) mrap_id order (the original -- kept for comparison)
  (b) sector-then-mrap_id order, with sector boundaries drawn
  (c) single-linkage hierarchical-clustering order (reveals the true
      clusters inferred from the correlation distance)
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HW5 = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HW5))

from src.covariance import correlation_from_covariance
from src.plotting import savefig
from src.portfolio_inputs import build_inputs

FIGURES = HW5 / "results" / "figures"


def main() -> None:
    inputs = build_inputs()
    corr = correlation_from_covariance(inputs.Omega_R)
    n = corr.shape[0]
    sectors = inputs.sectors.astype(int)

    # Handle the single zero-variance stock by replacing its row/col diag
    # with 1 so the heat-map shows it as a clean blank line.
    bad = np.where(np.diag(corr) <= 1e-12)[0]
    for k in bad:
        corr[k, :] = np.nan
        corr[:, k] = np.nan

    # ---- (a) sector-then-mrap_id order
    order_sec = np.lexsort((inputs.mrap_ids, sectors))
    corr_sec = corr[np.ix_(order_sec, order_sec)]
    sectors_sorted = sectors[order_sec]

    # Compute the row index at which each sector ends (for drawing lines).
    boundaries = []
    for s in np.unique(sectors_sorted):
        mask = (sectors_sorted == s)
        idx = np.where(mask)[0]
        boundaries.append((int(s), int(idx.min()), int(idx.max()) + 1))

    fig, ax = plt.subplots(figsize=(8, 7))
    im = ax.imshow(corr_sec, cmap="coolwarm", vmin=-0.6, vmax=0.8,
                   interpolation="nearest")
    # Draw sector boundary lines.
    for _, _, end in boundaries[:-1]:
        ax.axhline(end - 0.5, color="black", lw=0.4, alpha=0.5)
        ax.axvline(end - 0.5, color="black", lw=0.4, alpha=0.5)
    # Label sectors at the mid-point of each block if the block is large
    # enough (>= 25 stocks) so the labels are readable.
    for s, start, end in boundaries:
        if end - start >= 25:
            mid = (start + end) / 2
            ax.text(-12, mid, f"{s}", va="center", ha="right",
                    fontsize=8, color="black")
            ax.text(mid, -12, f"{s}", va="bottom", ha="center",
                    fontsize=8, color="black", rotation=0)
    ax.set_xticks([]); ax.set_yticks([])
    ax.set_title("corr($\\Omega_R$) ordered by NAICS-2 sector\n"
                 "(black lines at sector boundaries)\n")
    plt.colorbar(im, ax=ax, fraction=0.03, pad=0.02)
    savefig(fig, FIGURES / "04_corr_R_sector_ordered.png")

    # ---- (b) hierarchical-clustering order
    from scipy.cluster.hierarchy import linkage, leaves_list
    from scipy.spatial.distance import squareform
    # distance from correlation (clipped & NaN-safe)
    c_safe = np.nan_to_num(corr, nan=0.0)
    dist = np.sqrt(np.clip(0.5 * (1 - c_safe), 0.0, None))
    np.fill_diagonal(dist, 0.0)
    dist_c = squareform(dist, checks=False)
    Z = linkage(dist_c, method="average")
    order_hc = leaves_list(Z)
    corr_hc = corr[np.ix_(order_hc, order_hc)]

    fig, ax = plt.subplots(figsize=(8, 7))
    im = ax.imshow(corr_hc, cmap="coolwarm", vmin=-0.6, vmax=0.8,
                   interpolation="nearest")
    ax.set_xticks([]); ax.set_yticks([])
    ax.set_title("corr($\\Omega_R$), hierarchical-clustering order\n"
                 "(average linkage on $\\sqrt{(1-\\rho)/2}$)")
    plt.colorbar(im, ax=ax, fraction=0.03, pad=0.02)
    savefig(fig, FIGURES / "04_corr_R_hc_ordered.png")

    # ---- (c) within/cross sector table (Omega_R itself, not epsilon)
    rows = []
    for sid in np.unique(sectors):
        idx = np.where(sectors == sid)[0]
        if len(idx) < 2:
            continue
        sub = corr[np.ix_(idx, idx)]
        iu = np.triu_indices_from(sub, k=1)
        within = float(np.nanmean(sub[iu]))
        other = np.where(sectors != sid)[0]
        cross = float(np.nanmean(corr[np.ix_(idx, other)]))
        rows.append({"sector": int(sid), "n": int(len(idx)),
                     "within": within, "cross": cross,
                     "gap": within - cross})
    df = pd.DataFrame(rows).sort_values("gap", ascending=False)
    df.to_csv(HW5 / "results" / "12_omega_R_sector_corr.csv", index=False)

    print("\\nTop 10 sectors by Omega_R within-vs-cross gap:")
    print(df.head(10).to_string(index=False))
    print(f"\\noverall within-sector mean: {df['within'].mean():.3f}, "
          f"cross-sector: {df['cross'].mean():.3f}")


if __name__ == "__main__":
    main()
