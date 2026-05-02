# Problem 1 — factor loadings

For each of the 1 000 stocks we fit the no-intercept OLS
$r_i(t) = B_i F(t) + \varepsilon_i(t)$ on the 108 monthly observations the
stock is present (some names have < 108 months because of entry/exit).

- Loadings matrix `B` shape: (1000, 5)
- Median per-stock $R^2$: 0.326
- Mean per-stock $R^2$:   0.329

## Loadings summary (mean and std across stocks)

| factor | mean | std |
|---|---|---|
| factor_1 | 1.0502 | 0.4820 |
| factor_2 | 0.3701 | 0.6283 |
| factor_3 | -0.0320 | 0.8530 |
| factor_4 | -0.0101 | 1.1247 |
| factor_5 | -0.0014 | 0.9896 |

## Factor cumulative / annualised stats

See `results/01_factor_summary.csv`. Plot in `results/figures/01_cumulative_factor_returns.png`.

## Actual vs fitted plots

- MRAP 8568:  `results/figures/01_actual_vs_fitted_8568.png`
- MRAP 39541: `results/figures/01_actual_vs_fitted_39541.png`
