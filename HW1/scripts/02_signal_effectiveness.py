#!/usr/bin/env python3
"""
Q2 Signal effectiveness: apply Q1 corrections, compute multi-horizon targets
(returns 1/5/20, forward vol 5/20/60) and signal transforms, run four metrics
(IC, hit rate, regression, rank IC) for each target × predictor, save
q2_metrics.csv and Q2_analysis.md.
"""
import sys
from pathlib import Path

import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parent
HW1_DIR = SCRIPT_DIR.parent
DATA_PATH = HW1_DIR / "WKKWNT Data Sample (HomeWork #1 15-439).csv"
RESULTS_DIR = HW1_DIR / "results"
MD_DIR = HW1_DIR / "md_files"

sys.path.insert(0, str(HW1_DIR))

from src.clean_for_analysis import build_and_save, add_multi_horizon_targets_and_predictors
from src.metrics_signal import (
    compute_ic,
    compute_hit_rate,
    compute_regression,
    compute_rank_ic,
)


# (target_type, horizon) -> column name
TARGET_COLS = [
    ("return", 1, "forward_return_1"),
    ("return", 5, "forward_return_5"),
    ("return", 20, "forward_return_20"),
    ("vol", 5, "forward_vol_5"),
    ("vol", 20, "forward_vol_20"),
    ("vol", 60, "forward_vol_60"),
]

# (predictor_type, param) -> column name
PREDICTOR_COLS = [
    ("signal", None, "signal"),
    ("signal_ma", 5, "signal_ma_5"),
    ("signal_ma", 20, "signal_ma_20"),
    ("signal_pct", None, "signal_pct"),
    ("sign_signal", None, "sign_signal"),
]

METHODS = [
    ("IC", compute_ic, "estimate", None),
    ("hit_rate", compute_hit_rate, "estimate", None),
    ("regression", compute_regression, "beta", "r_squared"),
    ("rank_ic", compute_rank_ic, "estimate", None),
]


def fmt(x, decimals=4):
    if x is None or (isinstance(x, float) and (x != x or abs(x) > 1e10)):
        return "—"
    return f"{x:.{decimals}f}"


def fmt_ci(lo, hi):
    return f"[{fmt(lo)}, {fmt(hi)}]"


def main() -> None:
    data_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DATA_PATH
    if not data_path.exists():
        print(f"Data file not found: {data_path}")
        sys.exit(1)

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    MD_DIR.mkdir(parents=True, exist_ok=True)

    analysis_csv = RESULTS_DIR / "analysis_ready.csv"
    df = build_and_save(data_path, out_path=analysis_csv)
    df = add_multi_horizon_targets_and_predictors(df)
    print(f"Analysis-ready data: {len(df)} rows, saved to {analysis_csv}\n")

    # Ensure forward_return_1 exists (alias for forward_return)
    if "forward_return_1" not in df.columns and "forward_return" in df.columns:
        df["forward_return_1"] = df["forward_return"]

    rows = []
    for (ttype, thoriz, tcol) in TARGET_COLS:
        if tcol not in df.columns:
            continue
        target = df[tcol]
        for (ptype, pparam, pcol) in PREDICTOR_COLS:
            if pcol not in df.columns:
                continue
            pred = df[pcol]
            n_valid = int((pred.notna() & target.notna()).sum())
            for method_name, method_fn, est_key, extra_key in METHODS:
                if method_name == "IC":
                    est, n, pv, clo, chi = method_fn(pred, target)
                    r_sq = None
                elif method_name == "hit_rate":
                    est, n, pv, clo, chi = method_fn(pred, target)
                    r_sq = None
                elif method_name == "regression":
                    est, se, tstat, pv, r_sq, clo, chi = method_fn(pred, target)
                    n = n_valid
                else:
                    est, n, pv, clo, chi = method_fn(pred, target)
                    r_sq = None
                rows.append({
                    "target_type": ttype,
                    "target_horizon": thoriz,
                    "target_col": tcol,
                    "predictor_type": ptype,
                    "predictor_param": pparam,
                    "predictor_col": pcol,
                    "method": method_name,
                    "estimate": est,
                    "n": n,
                    "p_value": pv,
                    "ci_low": clo,
                    "ci_high": chi,
                    "r_squared": r_sq,
                })

    table_df = pd.DataFrame(rows)
    q2_csv = RESULTS_DIR / "q2_metrics.csv"
    table_df.to_csv(q2_csv, index=False)
    print(f"Metrics saved to {q2_csv} ({len(rows)} rows)\n")

    # Console: summary by target (one table per target, key metrics only)
    for (ttype, thoriz, tcol) in TARGET_COLS:
        sub = table_df[(table_df["target_type"] == ttype) & (table_df["target_horizon"] == thoriz)]
        if sub.empty:
            continue
        # One row per predictor, method=IC
        ic_sub = sub[sub["method"] == "IC"]
        if ic_sub.empty:
            continue
        print(f"Target: {ttype} horizon {thoriz} ({tcol})")
        print("  Predictor   | IC       | p-value | Rank IC  | p-value")
        print("  " + "-" * 55)
        for _, pr in enumerate(PREDICTOR_COLS):
            pcol = pr[2]
            r_ic = ic_sub[ic_sub["predictor_col"] == pcol]
            r_ri = sub[(sub["predictor_col"] == pcol) & (sub["method"] == "rank_ic")]
            ic_est = r_ic["estimate"].iloc[0] if not r_ic.empty else None
            ic_p = r_ic["p_value"].iloc[0] if not r_ic.empty else None
            ri_est = r_ri["estimate"].iloc[0] if not r_ri.empty else None
            ri_p = r_ri["p_value"].iloc[0] if not r_ri.empty else None
            print(f"  {pcol:12} | {fmt(ic_est):8} | {fmt(ic_p):7} | {fmt(ri_est):8} | {fmt(ri_p):7}")
        print()

    # Best combination by |IC| and by p-value
    ic_rows = table_df[table_df["method"] == "IC"].copy()
    ic_rows["abs_ic"] = ic_rows["estimate"].abs()
    ic_rows = ic_rows.dropna(subset=["abs_ic"])
    best_ic_str = "—"
    best_p_str = "—"
    if not ic_rows.empty:
        best_ic = ic_rows.loc[ic_rows["abs_ic"].idxmax()]
        best_ic_str = f"{best_ic['target_col']} × {best_ic['predictor_col']} (|IC|={fmt(best_ic['estimate'])})"
    p_valid = table_df.dropna(subset=["p_value"])
    if not p_valid.empty:
        best_p = p_valid.loc[p_valid["p_value"].idxmin()]
        best_p_str = f"{best_p['target_col']} × {best_p['predictor_col']} (p={fmt(best_p['p_value'])})"
        print("Best (target × predictor) by |IC|:", best_ic_str)
        print("Best by p-value:", best_p_str)
        print()

    # Q2_analysis.md
    q2_md = MD_DIR / "Q2_analysis.md"
    any_sig = (table_df["p_value"] < 0.05).any()
    if any_sig:
        conclusion = "After Q1 corrections, at least one (target × predictor × method) combination shows statistically significant predictability (p < 0.05). The signal may have predictive power for some horizons or volatility windows."
    else:
        conclusion = "After Q1 corrections, the signal does not show statistically significant predictability for returns (horizons 1, 5, 20) or for forward-looking volatility (5, 20, 60), whether using raw signal, rolling average, percentage change, or sign. We conclude no significant usefulness on this cleaned sample."

    # Build markdown tables: compact results (IC and Rank IC by target × predictor)
    md_tables = []
    for (ttype, thoriz, tcol) in TARGET_COLS:
        sub = table_df[(table_df["target_type"] == ttype) & (table_df["target_horizon"] == thoriz)]
        if sub.empty:
            continue
        md_tables.append(f"\n### {ttype} horizon {thoriz}\n")
        md_tables.append("| Predictor | IC | p (IC) | Rank IC | p (Rank IC) | Hit rate | p (HR) | β | p (reg) |\n")
        md_tables.append("|-----------|-----|--------|---------|--------------|----------|--------|-----|--------|\n")
        for (_, __, pcol) in PREDICTOR_COLS:
            r = sub[sub["predictor_col"] == pcol]
            if r.empty:
                continue
            def get(m, key="estimate"):
                x = r[r["method"] == m]
                return x[key].iloc[0] if not x.empty else None
            def get_p(m):
                x = r[r["method"] == m]
                return x["p_value"].iloc[0] if not x.empty else None
            ic_est, ic_p = get("IC"), get_p("IC")
            ri_est, ri_p = get("rank_ic"), get_p("rank_ic")
            hr_est, hr_p = get("hit_rate"), get_p("hit_rate")
            beta_est, reg_p = get("regression"), get_p("regression")
            md_tables.append(f"| {pcol} | {fmt(ic_est)} | {fmt(ic_p)} | {fmt(ri_est)} | {fmt(ri_p)} | {fmt(hr_est)} | {fmt(hr_p)} | {fmt(beta_est)} | {fmt(reg_p)} |\n")

    content = f"""# Q2 Signal effectiveness

## Data cleaning applied

We applied Q1 corrections without modifying the raw file: sort by date; deduplicate dates (keep first); fix monotonicity; drop rows with `adj_close` ≤ 0; replace signal in {{−999, 0}} with NaN.

## Multi-horizon returns

- `forward_return_1[t] = (adj_close[t+1]/adj_close[t]) - 1`
- `forward_return_5[t] = (adj_close[t+5]/adj_close[t]) - 1`
- `forward_return_20[t] = (adj_close[t+20]/adj_close[t]) - 1`

Last 1, 5, 20 rows respectively have NaN. No lookahead.

## Forward-looking volatility

Daily returns `r[t] = (adj_close[t]/adj_close[t-1]) - 1`. For window H ∈ {{5, 20, 60}}:

`forward_vol_H[t] = std(r[t+1], …, r[t+H])`

Last 5, 20, 60 rows have NaN for forward_vol_5, forward_vol_20, forward_vol_60.

## Predictor transforms

- **signal**: raw (sentinels already NaN).
- **signal_ma_5 / signal_ma_20**: backward-looking rolling mean (min_periods=1).
- **signal_pct**: signal.pct_change(); inf/NaN set to NaN.
- **sign_signal**: sign(signal); 0/NaN set to NaN.

## Why these metrics

- **IC (Pearson):** Linear predictive relationship; industry standard.
- **Hit rate:** Directional accuracy; binomial test vs 50%.
- **Regression:** Slope (effect size) and t-test on β.
- **Rank IC (Spearman):** Robust to outliers and monotone non-linearity.

## Results (compact)

{''.join(md_tables)}

## Best combinations

- **Best by |IC|:** {best_ic_str}
- **Best by p-value:** {best_p_str}

## Conclusion

{conclusion}
"""
    q2_md.write_text(content, encoding="utf-8")
    print(f"Report written to {q2_md}")


if __name__ == "__main__":
    main()
