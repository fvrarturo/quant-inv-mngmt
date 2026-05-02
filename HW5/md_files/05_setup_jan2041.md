# Problem 5 — Jan 2041 setup

### Investable universe

- `estimates.xlsx` gives 1 000 names. All map 1-1 to `data.xlsx`.
- Predictions μ range: [-0.772, 1.537]
  mean 0.0418.
- Pearson IC(μ, realised): **+0.018**
- Spearman IC:              **+0.168**
- Target sectors flagged for neutrality (first-two NAICS digits) : [52, 33, 32, 51, 54, 53, 22, 21, 56, 31]

### How would we forecast μ if not provided?

At a high level, an expected-return forecast for January 2041 would fuse
several signals with (i) forecast horizon = one month and (ii) cross-
sectional breadth across the 1 000-name universe:

1. **Value / quality / momentum style premia.** Long-short portfolios on
   book-to-price, gross-profit-to-assets, 12-1 month momentum, short-
   term reversal etc. are combined linearly; weights set by walk-
   forward IC or by a lasso on the monthly panel.
2. **Time-series factor forecast.** The five factors in `factors.xlsx`
   are forecast (EWMA momentum / mean-reversion / macro regression),
   then mapped to stock-level α via α_i = B_i · E[F].
3. **Cross-sectional regression (Fama–MacBeth style).** For each month
   fit r_{i,t+1} ~ characteristics_{i,t}; use the rolling-average γ
   coefficient as the forecast for Jan 2041.
4. **Analyst/consensus signals.** EPS revisions, target-price implied
   return, sell-side recommendations, and Bayesian pooling.
5. **Machine-learning ensemble.** Gradient-boosted trees / neural nets
   on the same characteristic panel, trained on rolling windows with
   purged-K-fold validation and shrunk to zero out-of-sample.

All individual signals would be cross-sectionally demeaned, ranked and
standardised, then combined with inverse-variance weights. A final
winsorisation (|z| ≤ 3) and **σ-rescaling** ensures the combined α has
similar information ratio across time.

### Outputs

- `results/05_universe.csv` — input table consumed by the optimisers.
