# Q8 Analysis: Univariate and multivariate Fama-MacBeth

## 8(a) Univariate

Results in `results/q8a_univariate.csv` and `results/figures/q8a_coef_series.png`.

- **Sign expectations:** Momentum (trailing returns) might be expected to have a positive sign (past winners continue). Price-only vs total return (PRC) can differ; PRC is total return so may capture dividend effects. We would not necessarily expect all signs to be the same (e.g. short-term reversal vs momentum).
- **Particularities:** Univariate regressions ignore correlation between predictors; one variable may proxy for another. Interpretation is "marginal" effect holding nothing else constant.

## 8(b) Multivariate

Results in `results/q8b_multivariate.csv` and per-spec CSVs.

- **Issues:** With two regressors, multicollinearity (e.g. PRC_Ret_T12M1 vs Prices_Ret_T12M1) can inflate standard errors. Signs may flip relative to univariate when both are included. Economic interpretation: each coefficient is the effect of that variable holding the other constant.
