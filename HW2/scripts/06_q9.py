#!/usr/bin/env python3
"""
Q9: Repeat 7(b) with dependent = PRC_Ret(F3M) and PRC_Ret(F6M). Compare to 7(b).
    Discuss econometric issues (overlapping returns) and corrections (e.g. Newey-West).
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
from src.fama_macbeth import run_fama_macbeth, fama_macbeth_inference, newey_west_t_stat

X_COL = "PRC_Ret_T12M1"
X_COLS = [X_COL]


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

    results = {}
    for y_col, label in [("PRC_Ret_F3M", "F3M"), ("PRC_Ret_F6M", "F6M")]:
        valid = panel.dropna(subset=[y_col, X_COL])
        coef_df = run_fama_macbeth(valid, y_col, X_COLS)
        coef_df.to_csv(RESULTS_DIR / f"q9_{label.lower()}_coef.csv")
        inf = fama_macbeth_inference(coef_df[X_COL])
        nw = newey_west_t_stat(coef_df[X_COL], max_lags=6)
        results[label] = {"coef_df": coef_df, "inf": inf, "nw": nw}
        print(f"Q9 {label}: mean={inf['mean']:.4f}, t={inf['t_stat']:.4f}, p={inf['p_value']:.4f}; NW t={nw['t_stat']:.4f}, p={nw['p_value']:.4f}")

        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(coef_df.index, coef_df[X_COL], color="steelblue", alpha=0.8)
        ax.axhline(inf["mean"], color="red", linestyle="--", label=f"Mean = {inf['mean']:.4f}")
        ax.set_xlabel("Date")
        ax.set_ylabel("Coefficient")
        ax.set_title(f"Fama-MacBeth: PRC_Ret({label}) on PRC_Ret(T12M1)")
        ax.legend()
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        fig.savefig(FIGURES_DIR / f"q9_{label.lower()}_coef.png", dpi=150, bbox_inches="tight")
        plt.close()

    # Q9_analysis.md
    f3 = results["F3M"]
    f6 = results["F6M"]
    md = f"""# Q9 Analysis: Fama-MacBeth with F3M and F6M

## Comparison with 7(b)

- **7(b)** used forward 1-month return; coefficients are not overlapping across months.
- **F3M / F6M** use overlapping forward returns: adjacent months share 2/3 or 5/6 of the return window, so the time-series of coefficients has positive autocorrelation.

## Results

### F3M (forward 3-month)

- Mean coefficient: {f3['inf']['mean']:.6f}
- Standard t: {f3['inf']['t_stat']:.4f} (p={f3['inf']['p_value']:.4f})
- Newey-West t: {f3['nw']['t_stat']:.4f} (p={f3['nw']['p_value']:.4f})

### F6M (forward 6-month)

- Mean coefficient: {f6['inf']['mean']:.6f}
- Standard t: {f6['inf']['t_stat']:.4f} (p={f6['inf']['p_value']:.4f})
- Newey-West t: {f6['nw']['t_stat']:.4f} (p={f6['nw']['p_value']:.4f})

## Econometric issues and corrections

- **Overlapping returns:** When the dependent variable is 3- or 6-month forward return, consecutive cross-sections use overlapping periods. Residuals (and thus coefficient estimates) are correlated across months, so the usual standard error of the mean coefficient is too small and t-stats are inflated.
- **Corrections:** (1) Newey-West HAC standard errors for the time-series mean (implemented above); (2) use non-overlapping forward returns (e.g. F3M every 3 months, F6M every 6 months) so that each observation is independent; (3) block bootstrap. The Newey-West adjusted t-stat is typically smaller than the standard t-stat.
"""
    (MD_DIR / "Q9_analysis.md").write_text(md, encoding="utf-8")
    print("Wrote md_files/Q9_analysis.md")


if __name__ == "__main__":
    main()
