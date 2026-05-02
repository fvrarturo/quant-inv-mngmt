#!/usr/bin/env python3
"""
Q10: Repeat 7(b) with observation weight = log(market cap). Compare to unweighted.
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
from src.fama_macbeth import run_fama_macbeth, fama_macbeth_inference

Y_COL = "PRC_Ret_F1M"
X_COL = "PRC_Ret_T12M1"
X_COLS = [X_COL]
WEIGHT_COL = "log_mcap"


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
    if WEIGHT_COL not in panel.columns:
        panel[WEIGHT_COL] = __import__("numpy").log(panel["mcap"].clip(lower=1e-6))

    valid = panel.dropna(subset=[Y_COL, X_COL, WEIGHT_COL])
    coef_unw = run_fama_macbeth(valid, Y_COL, X_COLS, weight_col=None)
    coef_w = run_fama_macbeth(valid, Y_COL, X_COLS, weight_col=WEIGHT_COL)
    inf_unw = fama_macbeth_inference(coef_unw[X_COL])
    inf_w = fama_macbeth_inference(coef_w[X_COL])

    pd.DataFrame([
        {"weighting": "equal", "mean_coef": inf_unw["mean"], "t_stat": inf_unw["t_stat"], "p_value": inf_unw["p_value"]},
        {"weighting": "log_mcap", "mean_coef": inf_w["mean"], "t_stat": inf_w["t_stat"], "p_value": inf_w["p_value"]},
    ]).to_csv(RESULTS_DIR / "q10_weighted_coef.csv", index=False)
    print(f"Unweighted: mean={inf_unw['mean']:.6f}, t={inf_unw['t_stat']:.4f}")
    print(f"Weighted (log mcap): mean={inf_w['mean']:.6f}, t={inf_w['t_stat']:.4f}")

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(coef_unw.index, coef_unw[X_COL], label="Equal weight", alpha=0.8)
    ax.plot(coef_w.index, coef_w[X_COL], label="log(mcap) weight", alpha=0.8)
    ax.set_xlabel("Date")
    ax.set_ylabel("Coefficient")
    ax.set_title("Q10: Fama-MacBeth PRC_Ret(F1M) on PRC_Ret(T12M1)")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "q10_weighted_vs_unweighted.png", dpi=150, bbox_inches="tight")
    plt.close()

    md = f"""# Q10 Analysis: Weighted Fama-MacBeth (log mcap)

## Comparison

| Weighting   | Mean coef | t-stat | p-value |
|------------|-----------|--------|---------|
| Equal      | {inf_unw['mean']:.6f} | {inf_unw['t_stat']:.4f} | {inf_unw['p_value']:.4f} |
| log(mcap)  | {inf_w['mean']:.6f} | {inf_w['t_stat']:.4f} | {inf_w['p_value']:.4f} |

Plot: `results/figures/q10_weighted_vs_unweighted.png`.

## Why this weighting?

- **Cap-weighted index:** The S&P 500 is market-cap weighted. Equal-weight OLS gives the same weight to small and large caps; the estimated "average" slope is dominated by the many small-cap names if they have higher cross-sectional variance. Weighting by log(mcap) (or mcap) makes the regression more representative of the effect for larger names and reduces the influence of tiny, noisy firms.
- **Issues to be aware of:** (1) Endogeneity: size and momentum may be related. (2) Interpretation: the weighted coefficient is the effect for a "typical" observation when weighted; it is not the same as the equal-weight average. (3) Log vs level: log(mcap) dampens the extreme weights that raw mcap would give.
"""
    (MD_DIR / "Q10_analysis.md").write_text(md, encoding="utf-8")
    print("Wrote md_files/Q10_analysis.md")


if __name__ == "__main__":
    main()
