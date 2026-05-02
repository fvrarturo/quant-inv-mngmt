#!/usr/bin/env python3
"""
Problem 7: run every long-short optimisation variant requested in parts (a)
through (e) and save weights + exposures for each.

Each optimisation maximises μᵀw subject to
  * dollar neutrality (Σw_i = 0)
  * gross exposure = 1 (Σ|w_i| ≤ 1)
  * monthly σ cap = 10 %/√12 ≈ 2.887 %
  * whichever additional constraints are appropriate.

Parts (b)–(f) assume a $100M book and a 2 %-of-ADV per-name trading cap.

Outputs:
  results/07_<variant>/weights.csv
  results/07_<variant>/summary.json
  results/07_<variant>/figures/...
  results/07_summary.csv  (every variant in one wide table)
  md_files/07_portfolio_construction.md
"""
from __future__ import annotations

import json
import sys
from dataclasses import asdict
from pathlib import Path

import numpy as np
import pandas as pd

HW5 = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HW5))

from src.optimize import (
    TARGET_ANNUAL_VOL,
    solve_portfolio,
    volume_based_max_weights,
)
from src.plotting import weight_plots
from src.portfolio_inputs import Inputs, build_inputs, save_weights

RESULTS = HW5 / "results"
MD = HW5 / "md_files"

BOOK_100M = 100_000_000
VOL_FRAC = 0.02


def run_variant(
    *,
    inputs: Inputs,
    name: str,
    description: str,
    box: float | None = None,
    neutral_factor_idx: list[int] | None = None,
    neutral_sectors: bool = False,
    capacity_max: np.ndarray | None = None,
    shock_caps: list | None = None,
    factor_tol: float = 1e-6,
    sector_tol: float = 1e-6,
    book: float = BOOK_100M,
) -> dict:
    out_dir = RESULTS / f"07_{name}"
    out_dir.mkdir(parents=True, exist_ok=True)
    fig_dir = out_dir / "figures"
    fig_dir.mkdir(exist_ok=True)

    # Combine hard boxes (box) and per-name capacity bounds into max_weights.
    max_w = None
    if capacity_max is not None and box is not None:
        max_w = np.minimum(capacity_max, box)
    elif capacity_max is not None:
        max_w = capacity_max
    elif box is not None:
        max_w = np.full(inputs.n, box)

    min_w = -max_w if max_w is not None else None

    res = solve_portfolio(
        mu=inputs.mu,
        Sigma=inputs.Omega_R,
        realized=inputs.realized,
        factor_loadings=inputs.B,
        sector_indicator=inputs.sector_indicator,
        sector_ids=inputs.sector_ids,
        target_annual_vol=TARGET_ANNUAL_VOL,
        max_weights=max_w,
        min_weights=min_w,
        neutral_factor_idx=neutral_factor_idx,
        neutral_sectors=neutral_sectors,
        factor_tol=factor_tol,
        sector_tol=sector_tol,
        shock_caps=shock_caps,
        meta={"variant": name, "description": description},
    )

    summary = res.to_summary()
    summary["variant"] = name
    summary["description"] = description
    summary["book_dollars"] = book

    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2))

    w_df = save_weights(inputs, res.weights, out_dir / "weights.csv", book=book)
    if np.any(np.abs(res.weights) > 0):
        weight_plots(res.weights, fig_dir / "weights_sorted.png",
                     fig_dir / "weights_hist.png",
                     title_prefix=f"{name} (status={res.status})")

    # Headline stats to stdout.
    print(f"\n[{name}] status={res.status}")
    print(f"  μᵀw  : {res.expected_return:+.4f} ({res.expected_return*12:+.2%} ann.)")
    print(f"  r̂ᵀw : {res.realized_return:+.4f} (Jan-2041 realised)")
    print(f"  σ_m  : {res.monthly_vol:.4f}  σ_a : {res.annual_vol:.4f}")
    print(f"  gross: {res.gross:.3f}   net: {res.net:+.3e}")
    factors_str = ", ".join(f"{k}:{v:+.3e}" for k, v in res.factor_exposure.items())
    print(f"  factor exp: {factors_str}")
    sectors_str = ", ".join(f"{k}:{v:+.3e}" for k, v in res.sector_exposure.items())
    print(f"  sector exp: {sectors_str}")
    print(f"  n long: {(res.weights > 1e-9).sum()}, n short: {(res.weights < -1e-9).sum()}")
    return summary


def main() -> None:
    RESULTS.mkdir(exist_ok=True)
    MD.mkdir(exist_ok=True)

    print("building inputs ...")
    inputs = build_inputs()
    print(f"universe: {inputs.n} names. Sectors flagged: {inputs.sector_ids}")

    # Capacity cap (for parts b-f only). max |w_i| = 2% ADV * price / book.
    cap_weights = volume_based_max_weights(
        inputs.adv_shares, inputs.price, gross_dollars=BOOK_100M, vol_frac=VOL_FRAC
    )
    cap_weights = np.clip(cap_weights, 0.0, 1.0)
    print(f"capacity cap: median={np.median(cap_weights):.4f}, min={cap_weights.min():.4f}, "
          f"max={cap_weights.max():.4f}. Names with cap < 1e-4: {(cap_weights < 1e-4).sum()}")

    # 2-sigma shock bounds (for part e.ii).  Omega_F is the monthly factor cov.
    factor_sigmas = np.sqrt(np.diag(inputs.Omega_F))
    shock_cap_10bps = 10e-4  # 10 bps of gross (gross is normalised to 1 in w-space)
    shock_caps_eii = [
        (inputs.B[:, k] * (2 * factor_sigmas[k]), shock_cap_10bps)
        for k in range(inputs.B.shape[1])
    ]

    variants = []

    # (a) Unconstrained.
    variants.append(run_variant(
        inputs=inputs, name="a_unconstrained",
        description="Dollar-neutral, gross=1, monthly σ ≤ 10%/√12; no other constraints",
    ))

    # (b) Position constraints at 1%, 50 bps, 10% of gross (with capacity cap).
    for tag, box in [("b1_1pct", 0.01), ("b2_50bps", 0.005), ("b3_10pct", 0.10)]:
        variants.append(run_variant(
            inputs=inputs, name=tag, description=f"max|w_i| = {box*100:.2f}% of gross, 2% ADV cap",
            box=box, capacity_max=cap_weights,
        ))

    # (c) F1 neutrality.
    variants.append(run_variant(
        inputs=inputs, name="c_f1_neutral",
        description="F1-neutral: Bᵀw = 0 on the first factor; 2% ADV cap; 1% box",
        box=0.01, capacity_max=cap_weights,
        neutral_factor_idx=[0],
    ))

    # (d) Sector-neutral (on the target sectors).
    variants.append(run_variant(
        inputs=inputs, name="d_sector_neutral",
        description="Net dollar exposure to each flagged sector = 0; 2% ADV cap; 1% box",
        box=0.01, capacity_max=cap_weights,
        neutral_sectors=True,
    ))

    # (e.i) Full neutrality.
    variants.append(run_variant(
        inputs=inputs, name="e1_all_neutral",
        description="All 5 factors neutral + all flagged sectors neutral",
        box=0.01, capacity_max=cap_weights,
        neutral_factor_idx=list(range(5)),
        neutral_sectors=True,
    ))

    # (e.ii) 2-sigma shock cap ≤ 10 bps per factor.
    variants.append(run_variant(
        inputs=inputs, name="e2_shock_10bps",
        description="|Bᵀw · 2σ_k| ≤ 10 bps for k=1..5; sectors neutral; 2% ADV cap; 1% box",
        box=0.01, capacity_max=cap_weights,
        neutral_sectors=True,
        shock_caps=shock_caps_eii,
    ))

    summary_df = pd.DataFrame(variants)
    summary_df.to_csv(RESULTS / "07_summary.csv", index=False)
    print("\nwrote results/07_summary.csv")

    # Stress test the e1 portfolio under 2σ shocks to each factor.
    e1_path = RESULTS / "07_e1_all_neutral" / "weights.csv"
    if e1_path.exists():
        w_e1 = pd.read_csv(e1_path)["weight"].to_numpy()
        factor_shocks = 2 * factor_sigmas  # monthly 2σ
        shock_impact = inputs.B.T @ w_e1 * factor_shocks  # k-long vector: per-factor PnL of shock
        shock_df = pd.DataFrame({
            "factor": inputs.factor_cols,
            "2sigma_monthly": factor_shocks,
            "exposure_Bw": inputs.B.T @ w_e1,
            "pnl_under_2sigma_shock": shock_impact,
        })
        shock_df.to_csv(RESULTS / "07_e1_factor_shocks.csv", index=False)
        print("\n2σ factor shock PnL on e1 portfolio:")
        print(shock_df.to_string(index=False))


if __name__ == "__main__":
    main()
