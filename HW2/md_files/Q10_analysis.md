# Q10 Analysis: Weighted Fama-MacBeth (log mcap)

## Comparison

| Weighting   | Mean coef | t-stat | p-value |
|------------|-----------|--------|---------|
| Equal      | 0.002252 | 0.4395 | 0.6609 |
| log(mcap)  | 0.002424 | 0.4805 | 0.6315 |

Plot: `results/figures/q10_weighted_vs_unweighted.png`.

## Why this weighting?

- **Cap-weighted index:** The S&P 500 is market-cap weighted. Equal-weight OLS gives the same weight to small and large caps; the estimated "average" slope is dominated by the many small-cap names if they have higher cross-sectional variance. Weighting by log(mcap) (or mcap) makes the regression more representative of the effect for larger names and reduces the influence of tiny, noisy firms.
- **Issues to be aware of:** (1) Endogeneity: size and momentum may be related. (2) Interpretation: the weighted coefficient is the effect for a "typical" observation when weighted; it is not the same as the equal-weight average. (3) Log vs level: log(mcap) dampens the extreme weights that raw mcap would give.
