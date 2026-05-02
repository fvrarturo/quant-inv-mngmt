#!/usr/bin/env python3
"""
Problem 5: set up the Jan 2041 optimisation inputs and discuss how we would
forecast expected returns absent a provided alpha file.

Produces an "investable universe" table aligned to estimates.xlsx:
  mrap_id, pred (μ), ret (realised), naics, sector (first two digits), price,
  shrout, mcap_dollars, avg_monthly_volume_shares, dollar_adv.

These columns are consumed by the downstream optimisation scripts.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

HW5 = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HW5))

from src.io import (
    TARGET_SECTORS,
    assign_sector,
    average_monthly_volume,
    load_estimates,
    load_panel,
)

RESULTS = HW5 / "results"
MD = HW5 / "md_files"


def main() -> None:
    RESULTS.mkdir(exist_ok=True)
    MD.mkdir(exist_ok=True)

    panel = load_panel()
    est = load_estimates()

    # Average monthly share volume across all observed months (panel vol is in hundreds).
    adv_shares = average_monthly_volume(panel)
    avg_price = panel.groupby("mrap_id")["price"].mean()

    universe = est.copy().rename(columns={"ret": "ret_realized_2041_01",
                                          "pred": "alpha_2041_01",
                                          "price": "price_2041_01",
                                          "shrout": "shrout_2041_01"})
    universe["sector"] = assign_sector(universe["naics"])
    universe["mcap_dollars"] = universe["price_2041_01"] * universe["shrout_2041_01"] * 1000  # shrout is 000s
    universe["adv_shares"] = universe["mrap_id"].map(adv_shares)
    universe["avg_price_hist"] = universe["mrap_id"].map(avg_price)
    universe["dollar_adv"] = universe["adv_shares"] * universe["price_2041_01"]

    universe.to_csv(RESULTS / "05_universe.csv", index=False)

    print(f"universe rows: {len(universe)}")
    print("alpha summary:")
    print(universe["alpha_2041_01"].describe())
    print("\nrealized return summary:")
    print(universe["ret_realized_2041_01"].describe())
    print("\nsector distribution (first 2 NAICS digits):")
    print(universe["sector"].value_counts().sort_index())

    # IC between predicted and realised returns (a crude check).
    ic_pearson = universe[["alpha_2041_01", "ret_realized_2041_01"]].corr().iloc[0, 1]
    ic_spearman = universe[["alpha_2041_01", "ret_realized_2041_01"]].corr(method="spearman").iloc[0, 1]

    md = [
        "# Problem 5 — Jan 2041 setup",
        "",
        "### Investable universe",
        "",
        f"- `estimates.xlsx` gives 1 000 names. All map 1-1 to `data.xlsx`.",
        f"- Predictions μ range: [{universe['alpha_2041_01'].min():.3f}, {universe['alpha_2041_01'].max():.3f}]",
        f"  mean {universe['alpha_2041_01'].mean():.4f}.",
        f"- Pearson IC(μ, realised): **{ic_pearson:+.3f}**",
        f"- Spearman IC:              **{ic_spearman:+.3f}**",
        f"- Target sectors flagged for neutrality (first-two NAICS digits) : {TARGET_SECTORS}",
        "",
        "### How would we forecast μ if not provided?",
        "",
        "At a high level, an expected-return forecast for January 2041 would fuse",
        "several signals with (i) forecast horizon = one month and (ii) cross-",
        "sectional breadth across the 1 000-name universe:",
        "",
        "1. **Value / quality / momentum style premia.** Long-short portfolios on",
        "   book-to-price, gross-profit-to-assets, 12-1 month momentum, short-",
        "   term reversal etc. are combined linearly; weights set by walk-",
        "   forward IC or by a lasso on the monthly panel.",
        "2. **Time-series factor forecast.** The five factors in `factors.xlsx`",
        "   are forecast (EWMA momentum / mean-reversion / macro regression),",
        "   then mapped to stock-level α via α_i = B_i · E[F].",
        "3. **Cross-sectional regression (Fama–MacBeth style).** For each month",
        "   fit r_{i,t+1} ~ characteristics_{i,t}; use the rolling-average γ",
        "   coefficient as the forecast for Jan 2041.",
        "4. **Analyst/consensus signals.** EPS revisions, target-price implied",
        "   return, sell-side recommendations, and Bayesian pooling.",
        "5. **Machine-learning ensemble.** Gradient-boosted trees / neural nets",
        "   on the same characteristic panel, trained on rolling windows with",
        "   purged-K-fold validation and shrunk to zero out-of-sample.",
        "",
        "All individual signals would be cross-sectionally demeaned, ranked and",
        "standardised, then combined with inverse-variance weights. A final",
        "winsorisation (|z| ≤ 3) and **σ-rescaling** ensures the combined α has",
        "similar information ratio across time.",
        "",
        "### Outputs",
        "",
        "- `results/05_universe.csv` — input table consumed by the optimisers.",
        "",
    ]
    (MD / "05_setup_jan2041.md").write_text("\n".join(md), encoding="utf-8")
    print("wrote md_files/05_setup_jan2041.md")


if __name__ == "__main__":
    main()
