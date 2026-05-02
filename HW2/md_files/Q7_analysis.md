# Q7 Analysis: Fama-MacBeth (forward 1M on PRC_Ret(T12M1))

## 7(a) November 2019

- Coefficient (PRC_Ret_T12M1): -0.053444
- R²: 0.0520

Interpretation: one cross-sectional regression; the coefficient measures the predicted change in next-month return per unit increase in momentum [-12,-1].

## 7(b) Full sample

- **Mean coefficient:** 0.002252
- **t-statistic:** 0.4395
- **p-value:** 0.6609
- **N dates:** 168

Time series of coefficients saved to `results/q7b_fm_coef.csv` and plotted in `results/figures/q7_fm_coef_t12m1.png`.

## 7(c) Interpretation

- **Economic/statistical:** The time-series mean of the cross-sectional slope indicates whether momentum (past 11-month return excluding last month) predicts next-month return on average. A positive mean would support momentum; the t-stat and p-value assess significance.
- **Momentum [-12,-1] as strategy:** If the coefficient is positive on average, going long high-momentum and short low-momentum would earn a positive spread, subject to implementation and risk.
- **Layperson:** "Stocks that did well (excluding the last month) tend to do a bit better next month on average, but the effect may be weak or inconsistent over time."
- **Consistency:** Inspect the plot for periods where the coefficient flips sign or is unusually large (e.g. post-2008, 2020).

## 7(d) Performance measures (Peterson Ch.2)

Treating the time-series of regression coefficients as a "strategy return" (each month we get one coefficient):

- **Hit rate:** 0.5119 (fraction of months with positive coefficient)
- **Cumulative return (product of 1+coef):** 0.0058
- **Max drawdown:** -0.5708
- **Sortino ratio:** 0.0340

The single regression coefficient each month can be interpreted as the expected excess return to a portfolio that goes long high momentum and short low momentum (per unit of exposure). The time-series of coefficients shows whether that premium is stable; drawdowns and hit rate help assess consistency.
