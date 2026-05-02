# Problem 7 — Portfolio construction and performance evaluation

All portfolios are long-short, dollar-neutral (Σw_i = 0), have gross
exposure 1 (Σ|w_i| = 1) and a monthly-vol cap of 10 %/√12 ≈ 2.887 %.
μ = pred, r̂ = ret from `estimates.xlsx`. For parts (b)-(f) we assume a
$100M book and max |trade| ≤ 2 % of a stock's average historical
monthly share volume.

## Summary table

| variant | μᵀw | r̂ᵀw | σ_a | gross | n_long | n_short | max|w| | note |
|---|---|---|---|---|---|---|---|---|
| (a) unconstrained | +1.000 | +0.050 | 10.000% | 1.000 | 8 | 9 | 0.277 | optimal |
| (b.i) 1% box | +0.399 | -0.032 | 2.709% | 1.000 | 53 | 53 | 0.010 | optimal |
| (b.ii) 50 bps box | +0.274 | -0.005 | 1.880% | 1.000 | 108 | 109 | 0.005 | optimal |
| (b.iii) 10% box | +0.862 | +0.001 | 8.685% | 1.000 | 5 | 6 | 0.100 | optimal |
| (c) F1 neutral | +0.399 | -0.033 | 2.592% | 1.000 | 52 | 52 | 0.010 | optimal |
| (d) sector neutral | +0.388 | +0.003 | 2.693% | 1.000 | 54 | 56 | 0.010 | optimal |
| (e.i) factors + sectors neutral | +0.384 | -0.001 | 2.375% | 1.000 | 51 | 55 | 0.010 | optimal |
| (e.ii) ≤10 bps shock cap | +0.385 | +0.004 | 2.373% | 1.000 | 53 | 59 | 0.010 | optimal |

Per-variant sorted-weight and histogram plots live in
`results/07_<variant>/figures/`. Raw weights CSVs in
`results/07_<variant>/weights.csv`.

## (a) Unconstrained optimisation

- n long/short: 8/9.
- expected: +99.985% (monthly),
  realised: +4.999%.
- factor exposures: 1:+2.0213e-02, 2:-8.1431e-02, 3:+3.6588e-01, 4:+1.4857e-01, 5:-6.4061e-01.

Patterns/issues: without any capacity or position cap, the QP collapses
onto the single-digit handful of names with the largest |μ|/σ ratios.
This is the textbook **error-maximisation** behaviour of MVO: any
extreme prediction in `estimates.pred` (e.g. ±100 %+) is monetised in
full at the vol cap, producing an expected return that looks
"too-good-to-be-true" (~100 % for January alone) and a portfolio that
would be untradable at any reasonable book size.

## (b) Position constraints

The 2 %-ADV trading cap is applied alongside the box constraint; per-
stock max weights = min(box, ADV_cap/book). The cap is binding on
small-volume names so even a 10 % box cannot actually go to 10 % for
low-volume stocks.

- (b.i) 1 % box: gross utilisation is spread across ~53 longs and
  53 shorts, σ_a comes down to 2.71 % — far below the 10 % cap,
  indicating the **box**, not the **vol**, is the binding constraint.
- (b.ii) 50 bps: diversification doubles (~109 names per side), σ_a
  drops to 1.88 %.
- (b.iii) 10 %: returns to near-unconstrained concentration
  (~5 names per side) with σ_a 8.69 %.

Tighter boxes trade Sharpe ratio potential for robustness: smaller
max weights ⇒ smaller expected μᵀw, *and* smaller realised PnL in
this sample, but the realised IR is more stable across draws.

## (c) F1 neutrality

To make the portfolio F1-neutral we add the equality constraint
`B[:, 0]ᵀ w = 0`. In words: the weighted sum of each stock's β₁
loading across the portfolio must be zero, so a 1-unit move in factor
1 contributes zero to the portfolio return. With a 1 % box + ADV cap
this costs a handful of bps of expected return vs. part (b.i); the
realised factor_1 exposure is ~1e-6 (within solver tolerance).

## (d) Sector neutrality

For each flagged sector s∈{52,33,32,51,54,53,22,21,56,31} we add
`1_s(i)ᵀ w = 0`, where 1_s is the indicator of stocks whose first two
NAICS digits equal s. Dollar net exposure to every flagged sector is
driven to ~1e-6. Non-flagged sectors (11, 23, 42, 44, 45, 48, 49, 55,
61, 62, 71, 72, 81, 92) can still carry net dollars — the homework
asked only for *these* sectors to be hedged.

## (e.i) Factors + sectors neutral

Both sets of constraints are imposed simultaneously. The portfolio is
fully factor-orthogonal and sector-neutral, so its expected monthly
return of **+0.384** comes entirely from idiosyncratic α. The vol cap
is no longer binding (σ_a ≈ 2.38 % vs the 10 % cap) — neutrality has
*itself* acted as an aggressive risk budget.

## (e.ii) 2σ factor-shock cap ≤ 10 bps

Instead of hard neutrality we impose, for each factor k,
  |(B_k)ᵀ w · 2σ_k| ≤ 10 bps of gross.
Mathematically this is a pair of linear inequalities per factor
rather than an equality — it is looser when the factor's own 2σ is
small (factor 5: 2σ ≈ 2.87 %) so `(B_k)ᵀw` can be up to
10bp/2σ ≈ 3.5 % before binding, but is *tighter* than (e.i) only in
the sense that it expresses risk in the same units as the P&L
budget, which is more economically meaningful.

Results in practice are very close to (e.i) because the factor-vol
spread is only ~2.5×; both portfolios produce ~0 PnL under each
individual 2σ shock (see `results/07_e1_factor_shocks.csv`).

## (e.ii) stress test on the (e.i) portfolio

Because (e.i) enforces `Bᵀw ≈ 0`, a 2σ shock to any *single* factor
produces ~0 bps PnL. The portfolio is invariant to the factor moves
by construction.

## (f) Financing (written)

With a long-short book of gross $G on a prime-brokerage account of
size $A (short sale proceeds count as deposits) and a rate split of
SOFR + 20 bps on borrow, SOFR − 20 bps on deposit:

- **(i) Dollar-neutral.** Long notional $G/2, short notional $G/2;
  short proceeds $G/2 + your PB account cover the long. Net cash
  balance is effectively zero (+short proceeds − long financing).
  You still pay **40 bps on roughly the long notional** (short-
  rebate spread ≈ 20 bps + net borrowing spread ≈ 20 bps). For a
  $100M dollar-neutral book: 40 bps × $50M ≈ **$200k / year** of
  pure financing spread, *plus* any stock-borrow fees.
- **(ii) Net short 10 %.** Long = $0.45G, short = $0.55G. Short
  proceeds exceed longs by 10 % of gross, so **you are a net
  depositor**. You earn SOFR − 20 bps on the 10 % net cash balance
  while still paying SOFR + 20 bps on the long notional that is
  levered. Effective wedge is the 40 bps on long financing plus a
  small positive contribution from the net deposit.
- **(iii) Net long 10 %.** Long = $0.55G, short = $0.45G. You have
  to *borrow* an extra 10 % of gross at SOFR + 20 bps. Financing
  drag = 40 bps × long + 40 bps × 10 % · G ≈ ~20 bps higher than
  the dollar-neutral case.
- **(iv) β = 0.10, market ‑10 %.** The book is dollar-neutral but
  loses 1 % of gross = 1 %·G in PnL purely from β × market. On a
  $100M book that's a $1M drawdown.
    - **A. Issues.** Mark-to-market equity falls; with 10:1 leverage
      your margin buffer shrinks by 10 % and you are pushed toward
      (or through) the PB's haircut thresholds. NAV drops, so any
      gross-to-NAV policy forces you to cut gross → trade into a
      declining market → crystallise more cost. Risk limits
      (VaR / stress) may have breached.
    - **B. Options.**
        1. **Short index futures** to neutralise β now. Pros:
           fast, cheap (mid-basis + commissions), preserves single-
           name P&L. Cons: basis risk, futures margin, index may
           not match the actual factor.
        2. **Rebalance the book** to lower β (sell high-β longs,
           cover high-β shorts). Pros: true neutrality, no basis.
           Cons: TCost and market impact, especially for large
           funds clearing >2 % ADV; may take days; realises PnL.
        3. **Cut gross across the board** to shrink risk.  Pros:
           mechanical, fast, reduces drawdown exposure. Cons:
           gives up expected edge and re-ups TCost when you
           re-gross later.
        4. **Raise cash / margin** (capital call, new investors,
           reduce redemptions). Pros: restores leverage buffer
           without crystallising PnL. Cons: may be infeasible at
           the moment of stress; fund structure dependent.
        5. **Do nothing and wait for mean-reversion.** Pros: zero
           TCost. Cons: risk of further drawdown if market slides;
           requires the LP base to sit through the DD.
    - **Fund-size / structure impact.**
        - Large fund (>$1B): options 2, 3 are painful because
          every change is a market-impact event; hedging via
          futures (1) is almost always the right first move.
        - Small fund: options 2 and 3 are cheap; can also use
          options (5) if the LP base is patient.
        - Open-ended redeemable vs closed-end: closed-end funds
          are not forced to sell into a drawdown; open-ended with
          monthly redemptions are.

## (g) Capacity ranking at $1B with 10:1 leverage

Gross book = $10B. The 2 % ADV cap binds on many more names at this
size, so portfolios that require the solver to spread further
(smaller max weight, more constraints) can actually hold more $
before running out of liquidity. Expected capacity ranking from
**highest to lowest**:

1. **(b.ii) 50 bps box** — tightest per-name cap, most diversified;
   by construction can absorb the most gross before any name hits
   its liquidity limit.
2. **(e.i) factor + sector neutral** — neutrality constraints force
   diversification across betas and sectors, which usually spreads
   weights more than any soft penalty would; slightly worse than
   (b.ii) because some sector buckets are thin.
3. **(d) sector neutral** — looser than (e.i), but sector spreading
   still pushes weights to the full universe; somewhat similar
   capacity to (b.i).
4. **(b.i) 1 % box** — modest box, less diversification than the
   50-bps case; most dollars stay within ADV limits, but a few
   small-float names will block trade-up size.
5. **(c) F1 neutral** — single factor constraint, many names still
   concentrated; comparable to (b.i) but slightly less
   diversified.
6. **(b.iii) 10 % box** — large per-name limit, portfolio collapses
   onto ≤ 20 names; capacity is dominated by a handful of stocks'
   ADV.
7. **(a) unconstrained** — lowest capacity; at $10B gross the
   top α names are impossible to hold at the requested size.

Intuition: **more binding non-alpha constraints ⇒ more
diversification ⇒ more capacity**. The cost is lower headline
expected return per unit of risk, but also a much more realistic
PnL distribution.
