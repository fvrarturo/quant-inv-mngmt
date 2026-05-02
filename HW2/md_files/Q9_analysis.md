# Q9 Analysis: Fama-MacBeth with F3M and F6M

## Comparison with 7(b)

- **7(b)** used forward 1-month return; coefficients are not overlapping across months.
- **F3M / F6M** use overlapping forward returns: adjacent months share 2/3 or 5/6 of the return window, so the time-series of coefficients has positive autocorrelation.

## Results

### F3M (forward 3-month)

- Mean coefficient: 0.005609
- Standard t: 0.7010 (p=0.4843)
- Newey-West t: 0.4654 (p=0.6423)

### F6M (forward 6-month)

- Mean coefficient: 0.010720
- Standard t: 0.8962 (p=0.3715)
- Newey-West t: 0.4515 (p=0.6522)

## Econometric issues and corrections

- **Overlapping returns:** When the dependent variable is 3- or 6-month forward return, consecutive cross-sections use overlapping periods. Residuals (and thus coefficient estimates) are correlated across months, so the usual standard error of the mean coefficient is too small and t-stats are inflated.
- **Corrections:** (1) Newey-West HAC standard errors for the time-series mean (implemented above); (2) use non-overlapping forward returns (e.g. F3M every 3 months, F6M every 6 months) so that each observation is independent; (3) block bootstrap. The Newey-West adjusted t-stat is typically smaller than the standard t-stat.
