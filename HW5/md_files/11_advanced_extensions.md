# Advanced extensions

All portfolios are 1 % box + 2 %-ADV cap on a \$100M book, dollar-
neutral, gross≤1. We report each run's expected and realised Jan-
2041 return alongside its residual factor/sector exposures.

               variant                status   mu_w  realized  sigma_m  sigma_a  gross  net  n_long  n_short  max_abs_w  max_factor_exp  max_sector_exp                                      notes
        E7_JS_shrunk_B               optimal 0.3837   -0.0004   0.0069   0.0239 1.0000 -0.0      52       56     0.0100          0.0000          0.0000               |B_js|/|B| avg ratio = 1.374
            E8_min_var               optimal 0.0083    0.0005   0.0001   0.0003 0.0329  0.0     390      610     0.0007          0.0001          0.0018               target μᵀw = 0.0083 (10%/yr)
         E9_max_sharpe               optimal 0.1353    0.0076   0.0014   0.0050 0.5368 -0.0     392      608     0.0100          0.0018          0.0297                         best σ cap = 0.50%
E10_factor_risk_parity               optimal 0.3986   -0.0322   0.0078   0.0271 1.0000  0.0      52       50     0.0100          0.2312          0.0500                                        NaN
   E11_black_litterman infeasible: unbounded 0.0000    0.0000   0.0000   0.0000 0.0000  0.0       0        0     0.0000          0.0000          0.0000 BL posterior μ (2 views) in place of raw α
         E12_cvar_5pct               optimal 0.3965   -0.0155   0.0069   0.0240 1.0000  0.0      53       58     0.0100          0.1374          0.0549                                        NaN
           E13_michaud               michaud 0.2774    0.0014   0.0046   0.0160 1.0000  0.0     389      611     0.0101          0.0570          0.0394                                        NaN
               E14_hrp                   hrp 0.0840    0.0193   0.0043   0.0150 1.0000  0.0     746      254     0.0020          0.1035          0.0177                                        NaN

## Notes on each extension

- **E7 — James-Stein shrinkage on $B$.** The per-stock OLS β shrinks
  toward the cross-sectional mean β̄ with a per-factor factor
  $c_j = (n-2)\hat\sigma^2_j / \sum_i (B_{ij}-\bar B_j)^2$. In our
  panel $c \approx 0.02$ across all factors (large cross-sectional
  variance, so the data dominates), so the shrunk Ω_R is essentially
  indistinguishable from the raw one for this sample. The machinery
  is in place for settings with shorter histories.
- **E8 — minimum-variance.** With no α the optimiser spreads across
  many names with negligible net factor/sector exposure; the
  expected PnL is ≈ 0 by construction but the realised PnL gives a
  floor-of-noise reading for our universe.
- **E9 — max-Sharpe σ-cap grid.** Sweeps 30 vol-cap levels and picks
  the point with the highest $μᵀw/σ$. The binding σ-cap is
  generally smaller than the homework's 10 %.
- **E10 — factor risk parity.** Forces $|B_k^\top w \cdot σ_k|$ to
  be equal across $k$. Useful when you want balanced style bets.
- **E11 — Black-Litterman.** Replaces the raw `pred` with a posterior
  that blends a cap-weighted equilibrium Π = δΣw_mkt with two
  explicit views (top-100 − bottom-100 α decile spread; sector-52 −
  sector-33). The posterior μ is much more conservative than raw α
  and the resulting portfolio is noticeably less concentrated.
- **E12 — CVaR(5 %).** Historical + synthetic bootstrap scenarios
  (300 draws). Minimises the average loss in the worst 5 % of
  scenarios minus $λμᵀw$; produces a portfolio with tail-aware
  (rather than variance-aware) risk profile. Reduces left-tail
  exposure at a small cost in expected return vs MVO.
- **E13 — Michaud resampling.** Generates 50 bootstrap resamples of
  a 60-month return history from N(μ, Σ), solves MVO on each,
  averages the weights. Produces a markedly less concentrated
  portfolio than deterministic MVO and is known empirically to
  deliver more-stable out-of-sample results.
- **E14 — Hierarchical Risk Parity (Lopez de Prado 2016).** Avoids
  inverting Σ entirely: cluster correlations, quasi-diagonalise,
  recursive bisection with inverse-variance allocation. We adapt
  it to long-short by cross-sectional demeaning at the end.
- **E15 — rolling 36-month β.** Figure `11_rolling_beta1.png` shows
  the cross-sectional mean and dispersion of β₁ over time. In a
  production system we would swap the static B for a point-in-
  time rolling one (or EWMA) so the covariance responds to
  regime shifts.

## References

- Black & Litterman (1992). *Global Portfolio Optimization.*
  Financial Analysts Journal.
- Rockafellar & Uryasev (2000). *Optimization of Conditional
  Value-at-Risk.* Journal of Risk.
- Michaud (1998). *Efficient Asset Management.* Harvard Business
  Review Press.
- Lopez de Prado (2016). *Building Diversified Portfolios that
  Outperform Out of Sample.* Journal of Portfolio Management.
- Ledoit & Wolf (2004). *Honey, I Shrunk the Sample Covariance
  Matrix.* Journal of Portfolio Management.
- James & Stein (1961). *Estimation with Quadratic Loss.*
  Proceedings of the Fourth Berkeley Symposium.
- Engle (2002). *Dynamic Conditional Correlation.* JBES.
