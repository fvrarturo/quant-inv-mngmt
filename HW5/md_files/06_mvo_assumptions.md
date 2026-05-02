# Problem 6 — Implicit assumptions of MVO

Mean-variance portfolio construction rests on a stack of simplifying
assumptions that the optimiser *does not verify* but whose violation drives
much of the out-of-sample disappointment of MV portfolios. At least five
that matter for this homework:

1. **Investor utility is quadratic (or returns are jointly elliptical —
   usually Gaussian).** Only the first two moments of the return
   distribution enter the objective, so skewness, kurtosis and tail
   dependence are ignored. Empirically equity returns have fat tails and
   non-linear co-movement in down-states, so MVO systematically under-
   weighs crash risk.

2. **Expected returns and the covariance matrix are known without error.**
   The solution treats μ and Ω as fixed inputs and routes the smallest
   advantage in μ into a levered position, which is why MVO is known for
   "estimation-error maximisation." In practice μ is measured with
   very wide standard errors.

3. **Returns are stationary and i.i.d. over the horizon.** The one-period
   problem treats μ and Ω as constant across the period of investment;
   there is no regime-switching, no auto-correlation in variance, no
   feedback from the investor's own trades.

4. **Markets are frictionless.** No transaction costs, no taxes, no
   borrowing/lending spread, unlimited divisibility and unlimited liquidity
   — any w is as cheap to hold as any other. The version in this homework
   layers on a crude financing model and a volume cap, but the vanilla
   formulation assumes all of the above away.

5. **Short-selling is unrestricted and symmetric with longs.** Negative
   weights carry the same financing, margin and locate cost as positive
   weights, and there is no hard-to-borrow penalty.

6. *(bonus)* **The investor has a single one-period horizon**. There is
   no dynamic re-balancing, no path-dependence, and no consideration of
   liquidation value. Multi-period optimal portfolios differ from the
   myopic MV allocation when returns are predictable.

7. *(bonus)* **Constraints are hard**. The volatility cap, factor
   neutrality, sector neutrality, etc. are all imposed as strict
   equalities/inequalities rather than as penalties; in practice we
   normally want a soft penalty so the optimiser can trade off expected
   return against residual risk gracefully.

8. *(bonus)* **Prices are exogenous** — the portfolio is a price-taker.
   Large funds that clear more than a small % of ADV push prices and
   therefore change their own μ and Ω.

These assumptions are the reason the modern portfolio-construction
pipeline layers shrinkage (μ, Ω), robust estimators, turnover/TCost
penalties and simulation-based validation *on top of* vanilla MVO.
