# Problem 2 — idiosyncratic covariance

## ε = R − BF

With per-stock OLS loadings `B` from problem 1 we computed
ε = R − BF and Ω_ε = (1/T) ε ε^T.

- ε shape: (1000, 108).
- Median idiosyncratic monthly σ: 0.0573 (0.198 annualised).
- Mean idiosyncratic monthly σ:   0.0656.
- Max idiosyncratic monthly σ:    0.4014.

## What is `BF` doing?

`BF` is the **systematic-return** reconstruction of the n × T return panel:
each stock's n × 5 loading row `B_i` multiplies the 5 × T factor path `F`
to give the part of that stock's time series that is explained by the
five common factors. Equivalently, `BF` is the orthogonal projection of
`R` onto the factor subspace in time-series sense (for a per-stock OLS
without intercept). It collapses cross-sectional co-movement into five
shared drivers; whatever remains in ε = R − BF is the stock-specific
residual that the factor model does not capture and that we take to be
(approximately) uncorrelated across names.

## File outputs

- `results/02_idio_variance.csv` — per-stock idiosyncratic variance.
- `results/02_omega_eps_diag.csv` — Ω_ε with zeroed off-diagonals (the
  convention used in the Ω_R decomposition of problem 4).
- `results/02_omega_eps_full.csv` / `.npz` — the un-shrunk sample Ω_ε.
