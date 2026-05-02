# Supplementary diagnostics

Every number below is an explicit check that the baseline outputs
are economically reasonable and statistically well-behaved. None of
these diagnostics changes an answer; they provide independent
verification of the baselines.

## 1. Per-stock regression diagnostics

- Sample covers N=946 stocks (≥24 obs each).
- Median $R^2$ = 0.331,
  IQR [0.209, 0.464].
- Durbin–Watson: median 2.02; fraction <1.5 (positive AC) = 1.3%.
- Jarque–Bera residual normality rejected (p<0.05) in 39.5% of stocks — fat tails in residuals, as expected.
- Breusch–Pagan heteroscedasticity rejected (p<0.05) in 98.0% — justifies HC0 / White s.e.
- Median |t-stat| per factor (HC0):

  | factor | median \|t\| | frac \|t\|>1.96 |
  |---|---|---|
  | factor_1 | 5.71 | 93.1% |
  | factor_2 | 1.20 | 26.1% |
  | factor_3 | 1.25 | 30.1% |
  | factor_4 | 0.92 | 17.1% |
  | factor_5 | 0.98 | 17.5% |

Figures: `10_r2_histogram.png`, `10_tstat_histograms.png`.

## 2. Factor-matrix collinearity

VIFs for the 5 factors (treating each as the response vs the
other four):

  factor   VIF  tolerance_1_over_VIF
factor_1 1.121                 0.892
factor_2 1.418                 0.705
factor_3 1.729                 0.578
factor_4 1.322                 0.756
factor_5 1.753                 0.570

Condition number of $F^\top F$: 15.22.

The strongest collinearity is between factors 3 and 5 (ρ=0.60);
their VIFs remain well below the usual serious thresholds (>10),
but the correlation is large enough to widen individual β
standard errors.

## 3. PCA on ε — are we missing a factor?

If the 5-factor model captured all systematic risk, PCA on ε
would show eigenvalues ≈ 1/N each. Instead we observe:

 eigenvalue  variance_share  cumulative
     0.2577          0.0462      0.0462
     0.2283          0.0410      0.0872
     0.1939          0.0348      0.1220
     0.1731          0.0311      0.1530
     0.1588          0.0285      0.1815
     0.1437          0.0258      0.2073
     0.1386          0.0249      0.2321
     0.1259          0.0226      0.2547
     0.1176          0.0211      0.2758
     0.1125          0.0202      0.2960

First PC explains 4.6%. Anything
above ~5% flags a missing systematic dimension we could add
(statistical factor, e.g. mean-reversion / quality tilt).

## 4. Residual correlation within sectors

If ε truly were cross-sectionally uncorrelated, mean within-sector
residual-correlation should equal mean cross-sector. In fact some
sectors retain systematic co-movement:

 sector   n  mean_within_corr  mean_cross_corr  within_minus_cross
     22  48             0.371           -0.001               0.372
     21  36             0.195           -0.014               0.210
     49   4             0.192            0.012               0.179
     55   5             0.163            0.007               0.156
     23  24             0.164            0.015               0.149
     44  28             0.086           -0.001               0.087
     62  17             0.082            0.000               0.081
     52 142             0.069           -0.000               0.069
     31  48             0.069            0.002               0.067
     53  19             0.079            0.013               0.066

The top-gap sectors should motivate a block-diagonal
$\Omega_\varepsilon$ by industry in a next pass.

## 5. $\Omega_R$ eigen-spectrum

- Min eigenvalue: -1.057e-17 (≥0 ⇒ PSD).
- Max eigenvalue: 2.225.
- Number of PCs to explain 95 % of $\Omega_R$ variance: **705** out of 1000.

See `results/figures/10_omega_R_spectrum.png`.

## 6. Per-variant portfolio diagnostics

Effective number of bets $= 1/\sum w_i^{\prime 2}$ (with
$w^\prime = w / \|w\|_1$); Herfindahl $= \sum w_i^{\prime 2}$
(lower = more diversified). Factor share = $w^\top B \Omega_F
B^\top w \,/\, w^\top \Omega_R w$.

         variant  effective_N_bets  herfindahl  factor_var_share  idio_var_share  pct_long  pct_short  f1_contrib  f2_contrib  f3_contrib  f4_contrib  f5_contrib
 a_unconstrained            5.5140      0.1814            0.0735          0.9265     0.086      0.914         0.0         0.0         0.0         0.0         0.0
         b1_1pct          100.4915      0.0100            0.1599          0.8401     0.240      0.760         0.0        -0.0         0.0         0.0         0.0
        b2_50bps          200.2525      0.0050            0.0937          0.9063     0.378      0.622         0.0         0.0        -0.0        -0.0         0.0
        b3_10pct           10.5785      0.0945            0.0780          0.9220     0.104      0.896         0.0        -0.0         0.0        -0.0         0.0
    c_f1_neutral          100.9952      0.0099            0.1343          0.8657     0.245      0.755         0.0        -0.0         0.0         0.0         0.0
d_sector_neutral          100.9890      0.0099            0.1233          0.8767     0.353      0.647         0.0        -0.0        -0.0         0.0         0.0
  e1_all_neutral          102.5919      0.0097            0.0000          1.0000     0.355      0.645         0.0         0.0         0.0         0.0         0.0
  e2_shock_10bps          102.0725      0.0098            0.0173          0.9827     0.360      0.640         0.0         0.0         0.0         0.0         0.0

Figure `10_factor_risk_bars.png` shows the stacked factor-vs-idio
share per variant: the neutralised portfolios run almost entirely
on idiosyncratic risk, consistent with $B^\top w \approx 0$.

## 7. α diagnostics

Cross-sectional statistics of `pred` vs `ret` by sector, by market-
cap decile, by historical $β_1$ decile — see files
`10_alpha_by_sector.csv`, `10_alpha_by_mcap.csv`,
`10_alpha_by_beta.csv`. Winsorisation of α at |z|≤{1.5,2,3,5} is
compared in `10_alpha_winsor_cdf.png`: above |z|=3 the cdf is
essentially unchanged, below |z|=2 the optimisation concentration
falls noticeably.
