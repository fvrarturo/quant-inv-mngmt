#!/usr/bin/env python3
"""
Q7: Fama-MacBeth cross-sectional regression.
    (a) Nov 2019: dependent = forward 1M return, independent = PRC_Ret(T12M1).
    (b) Full sample; plot time series of coefficients; statistical significance.
    (c)(d) Interpretation and performance measures → md_files/Q7_analysis.md
"""
import os
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
HW2_DIR = SCRIPT_DIR.parent
os.environ.setdefault("MPLCONFIGDIR", str(HW2_DIR / ".mpl_cache"))
(HW2_DIR / ".mpl_cache").mkdir(exist_ok=True)

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

DATA_PATH = HW2_DIR / "SP500Raw.xlsx"
RESULTS_DIR = HW2_DIR / "results"
FIGURES_DIR = RESULTS_DIR / "figures"
MD_DIR = HW2_DIR / "md_files"
PANEL_PATH = RESULTS_DIR / "full_panel.csv"

sys.path.insert(0, str(HW2_DIR))

from src.io import load_sp500, load_panel
from src.returns import build_full_panel
from src.fama_macbeth import (
    cross_sectional_ols,
    run_fama_macbeth,
    fama_macbeth_inference,
    strategy_metrics,
)


def _load_panel(data_path: Path) -> pd.DataFrame:
    if PANEL_PATH.exists():
        return load_panel(PANEL_PATH)
    df = load_sp500(data_path)
    return build_full_panel(df)


def main() -> None:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else DATA_PATH
    if not path.exists():
        print(f"Data file not found: {path}")
        sys.exit(1)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    MD_DIR.mkdir(parents=True, exist_ok=True)

    panel = _load_panel(path)
    panel["date"] = pd.to_datetime(panel["date"], errors="coerce")
    y_col = "PRC_Ret_F1M"
    x_col = "PRC_Ret_T12M1"
    x_cols = [x_col]

    # 7(a): November 2019 only
    nov2019 = panel[panel["date"].dt.to_period("M") == "2019-11"].copy()
    nov2019 = nov2019.dropna(subset=[y_col, x_col])
    coef_a = float("nan")
    r2_a = float("nan")
    if len(nov2019) >= 30:
        res_a = cross_sectional_ols(nov2019[y_col], nov2019[x_cols])
        coef_a = res_a["coef"].iloc[0]
        r2_a = res_a["r_squared"]
        pd.DataFrame({"coef": [coef_a], "r_squared": [r2_a]}).to_csv(
            RESULTS_DIR / "q7a_nov2019_coef.csv", index=False
        )
        print(f"Q7(a) Nov 2019: coef(PRC_Ret_T12M1) = {coef_a:.6f}, R² = {r2_a:.4f}")
    else:
        print("Q7(a) Nov 2019: insufficient data")

    # 7(b): Full sample Fama-MacBeth
    valid = panel.dropna(subset=[y_col] + x_cols)
    coef_df = run_fama_macbeth(valid, y_col, x_cols)
    coef_df.to_csv(RESULTS_DIR / "q7b_fm_coef.csv")
    inf = fama_macbeth_inference(coef_df[x_col])
    metrics = strategy_metrics(coef_df[x_col])
    print(f"Q7(b) Full sample: mean coef = {inf['mean']:.6f}, t = {inf['t_stat']:.4f}, p = {inf['p_value']:.4f}")

    # Plot coefficient series
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(coef_df.index, coef_df[x_col], color="steelblue", alpha=0.8)
    ax.axhline(inf["mean"], color="red", linestyle="--", label=f"Mean = {inf['mean']:.4f}")
    ax.set_xlabel("Date")
    ax.set_ylabel("Coefficient")
    ax.set_title("Fama-MacBeth: PRC_Ret(F1M) on PRC_Ret(T12M1)")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "q7_fm_coef_t12m1.png", dpi=150, bbox_inches="tight")
    plt.close()

    # Q7_analysis.md
    md = f"""# Q7 Analysis: Fama-MacBeth (forward 1M on PRC_Ret(T12M1))

## 7(a) November 2019

- Coefficient (PRC_Ret_T12M1): {coef_a:.6f}
- R²: {f"{r2_a:.4f}" if pd.notna(r2_a) else "—"}

Interpretation: one cross-sectional regression; the coefficient measures the predicted change in next-month return per unit increase in momentum [-12,-1].

## 7(b) Full sample

- **Mean coefficient:** {inf['mean']:.6f}
- **t-statistic:** {inf['t_stat']:.4f}
- **p-value:** {inf['p_value']:.4f}
- **N dates:** {inf['n_dates']}

Time series of coefficients saved to `results/q7b_fm_coef.csv` and plotted in `results/figures/q7_fm_coef_t12m1.png`.

## 7(c) Interpretation

- **Economic/statistical:** The time-series mean of the cross-sectional slope indicates whether momentum (past 11-month return excluding last month) predicts next-month return on average. A positive mean would support momentum; the t-stat and p-value assess significance.
- **Momentum [-12,-1] as strategy:** If the coefficient is positive on average, going long high-momentum and short low-momentum would earn a positive spread, subject to implementation and risk.
- **Layperson:** "Stocks that did well (excluding the last month) tend to do a bit better next month on average, but the effect may be weak or inconsistent over time."
- **Consistency:** Inspect the plot for periods where the coefficient flips sign or is unusually large (e.g. post-2008, 2020).

## 7(d) Performance measures (Peterson Ch.2)

Treating the time-series of regression coefficients as a "strategy return" (each month we get one coefficient):

- **Hit rate:** {metrics['hit_rate']:.4f} (fraction of months with positive coefficient)
- **Cumulative return (product of 1+coef):** {metrics['cum_return']:.4f}
- **Max drawdown:** {metrics['max_drawdown']:.4f}
- **Sortino ratio:** {metrics['sortino']:.4f}

The single regression coefficient each month can be interpreted as the expected excess return to a portfolio that goes long high momentum and short low momentum (per unit of exposure). The time-series of coefficients shows whether that premium is stable; drawdowns and hit rate help assess consistency.
"""
    (MD_DIR / "Q7_analysis.md").write_text(md, encoding="utf-8")
    print("Wrote md_files/Q7_analysis.md")


if __name__ == "__main__":
    main()
