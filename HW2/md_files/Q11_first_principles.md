# Q11: First principles — why this homework and what it teaches

## Why this homework?

The assignment connects three things: (1) **data construction** (identifiers, total vs price return, panel structure), (2) **momentum signals** (trailing returns, skip-month momentum, volatility-adjusted measures), and (3) **cross-sectional prediction** (Fama-MacBeth, weighting, overlapping returns). The goal is to see whether past returns help predict future returns in the cross-section of S&P 500 stocks—and to do it in a way that is reproducible, clearly defined, and aware of econometric pitfalls.

## What it teaches about investment strategies

- **Signal design:** Different definitions of “momentum” (T12, T12M1, T12_1M, price vs total return, Sharpe-style) can have different predictive power and robustness. Skip-month momentum (T12M1) is often used to avoid short-term reversal.
- **Implementation:** Equal-weight vs cap-weighted (or log-cap-weighted) regression changes whose behavior we are averaging; it matters for index-like or institutional applications.
- **Inference:** Overlapping forward returns (F3M, F6M) inflate t-stats; corrections like Newey-West or non-overlapping samples are necessary for honest inference. Single-month forward returns (F1M) avoid that issue.

## What we learned from different independent and dependent variables

- **Independent variables:** Trailing total return (PRC-based) vs price-only return capture dividend effects differently. The same “strategy” can look different depending on which return we use. Volatility-adjusted (SR) and skip-month (T12M1) variants isolate different aspects of momentum.
- **Dependent variables:** F1M gives one clear interpretation per month; F3M and F6M increase power but introduce overlap and require different standard errors. The choice of horizon ties directly to holding period and to how we test the strategy.

Taking a step back: the homework trains us to build a factor (momentum), test it in the cross-section with a standard method (Fama-MacBeth), and interpret results with appropriate caveats—skills that generalize to other factors and datasets.
