#!/usr/bin/env python3
"""
Q8: Fama-MacBeth as in 7(b).
    (a) Univariate: dep = forward 1M; each predictor separately.
    (b) Multivariate: four specified pairs.
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

UNIVARIATE_PREDICTORS = [
    "Price_Ret_T1",
    "prc",  # PRC column
    "PRC_Ret_T12",
    "Prices_Ret_T12",
    "PRC_Ret_T12M1",
    "Prices_Ret_T12M1",
    "PRC_Ret_T12_1M",
    "Prices_Ret_T12_1M",
    "SR_Prices_Ret_T12M1",
]

MULTIVARIATE_SPECS = [
    ("Price_Ret_T1", "Prices_Ret_T12M1"),
    ("prc", "PRC_Ret_T12M1"),
    ("prc", "Prices_Ret_T12"),
    ("prc", "SR_Prices_Ret_T12M1"),
]


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

    # 8(a) Univariate
    univariate_rows = []
    coef_series_univariate = {}
    for pred in UNIVARIATE_PREDICTORS:
        if pred not in panel.columns:
            continue
        valid = panel.dropna(subset=[Y_COL, pred])
        coef_df = run_fama_macbeth(valid, Y_COL, [pred])
        if coef_df.empty:
            continue
        col = coef_df.columns[0]
        inf = fama_macbeth_inference(coef_df[col])
        univariate_rows.append({
            "predictor": pred,
            "mean_coef": inf["mean"],
            "t_stat": inf["t_stat"],
            "p_value": inf["p_value"],
            "n_dates": inf["n_dates"],
        })
        coef_series_univariate[pred] = coef_df[col]
        print(f"  8(a) {pred}: mean_coef={inf['mean']:.4f}, t={inf['t_stat']:.4f}, p={inf['p_value']:.4f}")

    pd.DataFrame(univariate_rows).to_csv(RESULTS_DIR / "q8a_univariate.csv", index=False)

    # Plot univariate coefficient series (one subplot per predictor or multi-line)
    fig, ax = plt.subplots(figsize=(12, 5))
    for pred, ser in coef_series_univariate.items():
        ax.plot(ser.index, ser.values, label=pred, alpha=0.8)
    ax.set_xlabel("Date")
    ax.set_ylabel("Coefficient")
    ax.set_title("Q8(a) Univariate Fama-MacBeth coefficient series")
    ax.legend(bbox_to_anchor=(1.02, 1), loc="upper left", fontsize=7)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "q8a_coef_series.png", dpi=150, bbox_inches="tight")
    plt.close()

    # 8(b) Multivariate
    multi_rows = []
    for i, (x1, x2) in enumerate(MULTIVARIATE_SPECS):
        if x1 not in panel.columns or x2 not in panel.columns:
            continue
        valid = panel.dropna(subset=[Y_COL, x1, x2])
        coef_df = run_fama_macbeth(valid, Y_COL, [x1, x2])
        if coef_df.empty:
            continue
        for col in [x1, x2]:
            inf = fama_macbeth_inference(coef_df[col])
            multi_rows.append({
                "spec": f"{x1}+{x2}",
                "predictor": col,
                "mean_coef": inf["mean"],
                "t_stat": inf["t_stat"],
                "p_value": inf["p_value"],
            })
        coef_df.to_csv(RESULTS_DIR / f"q8b_multivariate_{i+1}_{x1}_{x2}.csv".replace(" ", "_"))
    pd.DataFrame(multi_rows).to_csv(RESULTS_DIR / "q8b_multivariate.csv", index=False)
    print("8(b) Multivariate results saved.")

    # Q8_analysis.md
    md = """# Q8 Analysis: Univariate and multivariate Fama-MacBeth

## 8(a) Univariate

Results in `results/q8a_univariate.csv` and `results/figures/q8a_coef_series.png`.

- **Sign expectations:** Momentum (trailing returns) might be expected to have a positive sign (past winners continue). Price-only vs total return (PRC) can differ; PRC is total return so may capture dividend effects. We would not necessarily expect all signs to be the same (e.g. short-term reversal vs momentum).
- **Particularities:** Univariate regressions ignore correlation between predictors; one variable may proxy for another. Interpretation is "marginal" effect holding nothing else constant.

## 8(b) Multivariate

Results in `results/q8b_multivariate.csv` and per-spec CSVs.

- **Issues:** With two regressors, multicollinearity (e.g. PRC_Ret_T12M1 vs Prices_Ret_T12M1) can inflate standard errors. Signs may flip relative to univariate when both are included. Economic interpretation: each coefficient is the effect of that variable holding the other constant.
"""
    (MD_DIR / "Q8_analysis.md").write_text(md, encoding="utf-8")
    print("Wrote md_files/Q8_analysis.md")


if __name__ == "__main__":
    main()
