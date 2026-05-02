# Problem 4 — total covariance Ω_R

Ω_R = B Ω_F Bᵀ + Ω_ε.
- Shape: (1000, 1000).
- min eigenvalue: -1.057e-17

## Reported pair

- ρ(MRAP 24541, MRAP 91309) = **0.4628**
- σ(MRAP 24541) = 0.0496/mo, σ(MRAP 91309) = 0.0640/mo, cov = 0.001470

Heatmap of Ω_R correlations: `results/figures/04_corr_R.png`.

## What errors could have crept in, and what could be improved?

1. **OLS loadings are noisy.** Per-stock OLS with only 108 observations (and
   fewer for names that enter/exit mid-sample) produces betas with large
   standard errors, especially when factors are correlated. Shrinking each
   stock's β toward the cross-sectional mean (James–Stein) or using a
   Bayesian/ridge fit would stabilise B.
2. **No alpha term.** The no-intercept convention `R = BF + ε` forces any
   level return into the residual. If a factor is not return-dollar-neutral
   this can bias loadings. Centring F (and including an intercept) is a
   standard fix.
3. **Ω_F uses 108 months** — point-in-time estimate that is slow to respond
   to regime shifts; an EWMA or DCC estimator, or separate specific/
   systemic time horizons (Barra-style) would be preferable.
4. **Diagonal Ω_ε assumption.** Residuals are not perfectly cross-
   sectionally uncorrelated, especially within industries. Keeping a
   block-diagonal Ω_ε by sector, or shrinking to the diagonal with a
   Ledoit–Wolf-style target, is an improvement.
5. **Stale factor definitions** — Ω_R does not adjust for turnover in the
   factor construction; if the factors' own weighting schemes drift, Ω_F
   moves too.
6. **Non-synchronous data / outliers.** Price spikes (splits, corporate
   actions) blow up individual residuals. Robust regression (Huber) or
   winsorisation would reduce leverage of a few big residual months.
7. **Small-T / large-N.** 1 000 names × 108 months ≈ rank-deficient sample
   covariance; Ω_R gets structure only from B Ω_F Bᵀ (rank ≤ 5). Augmenting
   with a statistical factor pull (PCA on ε) could catch missing factors.
