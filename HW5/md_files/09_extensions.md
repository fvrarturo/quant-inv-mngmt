# Extensions (beyond the homework)

Everything below is optional work layered on the required output. It
stress-tests the baseline construction pipeline and documents design
choices that can change the answer materially.

## E1 — α shrinkage (cross-sectional z, clipped to ±2σ)

The raw α in `estimates.pred` has a range of [-0.77, +1.54] — the
tails move the unconstrained solver enormously. After a z-score +
clip at ±2σ (keeps the ordering but rescales magnitude), the
unconstrained portfolio still wins on μᵀw but spreads over many more
names. See `results/09_extensions_summary.csv`.

## E2 — covariance shrinkage

Ledoit-style: Σ ← (1-λ) Σ + λ m I, m = mean(diag Σ). For the fully-
neutral variant:

 lambda     mu_w  realized  sigma_a  n_long  n_short  max_abs_w
   0.00 0.383576 -0.000734 0.023755      51       55       0.01
   0.05 0.383576 -0.000734 0.024209      51       55       0.01
   0.10 0.383576 -0.000734 0.024656      51       55       0.01
   0.25 0.383576 -0.000734 0.025948      52       57       0.01
   0.50 0.383576 -0.000734 0.027971      51       55       0.01

Shrinkage dampens concentration (max |w| falls monotonically with
λ) while expected μᵀw decays slowly — a classic Sharpe-robustness
trade.

## E3 — efficient frontier over σ cap

Expected and realised return for the all-neutral portfolio across
σ_a caps from 2 %–30 %. The realised curve is well below expected
(we are one draw away from μ, and α is optimistic in magnitude).

## E4 — TCost penalty (stylised)

Linear penalty on gross turnover + quadratic term on the covariance
acting as a "market-impact" shrink. Turning on either reduces
max |w| and tightens risk.

## E5 — bootstrap of realised P&L

Jan-2041 is one realisation. We draw 500 synthetic Jan months by
picking a training-month factor row and resampling idiosyncratic
residuals from the historical fit, then recompute r̂ᵀw for each
variant. This gives a range and a "probability of positive" that
the single-point realised figure can't.

                          mean       std       q05       q95  p_pos
a_unconstrained   5.074547e-04  0.032120 -0.066159  0.048969  0.484
b1_1pct          -2.738190e-04  0.007383 -0.012442  0.010410  0.464
b2_50bps          8.132431e-04  0.005298 -0.007051  0.010228  0.552
b3_10pct          3.801291e-03  0.027493 -0.042219  0.042944  0.586
c_f1_neutral     -1.379074e-07  0.007321 -0.011568  0.011750  0.464
d_sector_neutral  8.951934e-04  0.007690 -0.012687  0.010821  0.578
e1_all_neutral    6.087452e-04  0.006776 -0.010423  0.010396  0.558
e2_shock_10bps    7.993152e-04  0.006635 -0.012333  0.009968  0.550

## E6 — expected vs realised plot

See `results/figures/09_E6_expected_vs_realised.png`. The α model
*drastically* overstates monthly returns for the looser variants
(a, b.iii); tighter constraints close the gap but also shrink
expected μᵀw. The bootstrap in E5 shows the realised Jan-2041
figure is within the 90 % band for every variant except (a),
which is the classic concentration pathology.
