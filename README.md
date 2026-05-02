# 15.439 — Quantitative Investment Management

This repository collects my coursework for **MIT 15.439 — Quantitative
Investment Management**, taught by Prof. Matthew Rothman in Spring 2026. The
course covers behavioural finance, factor investing, signal
construction, portfolio construction & risk management, short selling,
trading and execution, and the future of the asset-management industry.

> **Author.** Arturo Favara
> [LinkedIn](https://www.linkedin.com/in/arturo-favara)
>
> **Course.** 15.439 Quantitative Investment Management
> MIT, Spring 2026.
> Instructor: Prof. Matthew Rothman (Head of Statistical Arbitrage Strategies
> & Deputy Head of Quantitative Strategies, Millennium Management).
>
> **Reference texts.** *Inside the Black Box* (Narang); *Asset Management*
> (Ang); *Efficiently Inefficient* (Pedersen); *Inefficient Markets*
> (Shleifer); *Trading & Exchanges* (Harris).

---

## Repository layout

```
Quant_Inv_HWs/
├── HW1/   Data quality + signal evaluation (WKKWNT "4sight")
├── HW2/   S&P 500 momentum & Fama–MacBeth cross-sectional regressions
├── HW3/   China SOE Factor — methodology critique & redesign
├── HW4/   Loss-probability, drawdowns and Monte-Carlo for hedge-fund DD
├── HW5/   Risk model + portfolio-construction cascade (full code)
├── HW6/   "Guaranteed to lose money" — closed-book essay
├── requirements.txt
└── README.md
```

Each homework folder contains the **assignment PDF** as released by the
instructor (`HW{n}.pdf`) and **my submitted report** (`Quant_Inv_HW{n}.pdf`).
The data-intensive assignments (HW1, HW2, HW5) additionally ship with the
Python code that produced the report:

```
HW{n}/
├── HW{n}.pdf              # the original prompt
├── Quant_Inv_HW{n}.pdf    # my submitted report
├── src/                   # reusable modules (loaders, math, optimisers, …)
├── scripts/               # one numbered script per question / problem
└── md_files/              # per-question markdown summaries
```

---

## Assignment summary

### HW1 — Data Quality & Signal Effectiveness
*Released Feb 10, due Feb 25.*

A fictional vendor ("WKKWNT, LLC") has shipped a forecast signal called
*4sight* together with the prices of a broad-market ETF, and our portfolio
manager wants a quality audit + a fast read on whether the signal predicts
returns. The work covers the entire data-due-diligence playbook — schema
checks, null/duplicate/gap detection, OHLC bracket sanity, return-outlier
flagging, signal z-score and sentinel checks, weekend/holiday alignment —
followed by an information-coefficient and IR-based assessment of the
signal's predictive power.

*Code.* `src/check_*.py` (one module per quality check), `src/io.py`,
`src/clean_for_analysis.py`, `src/metrics_signal.py`;
`scripts/01_initial_analysis.py`, `scripts/02_signal_effectiveness.py`.

### HW2 — Momentum signals & Fama–MacBeth on the S&P 500
*Released Mar 3, due Mar 11.*

Build a panel of every S&P 500 constituent for 2010–2024 (monthly), construct
a battery of trailing-return "momentum" features
(`PRC_Ret(T12)`, `Prices_Ret(T12)`, `PRC_Ret(T12M1)`, `Prices_Ret(T12M1)`,
`PRC_Ret(T12_1M)`, `SR_Prices_Ret(T12M1)`, …) and regress one-/three-/six-
month forward returns on each (and combinations) using Fama–MacBeth
cross-sectional regressions. Reports per-month coefficients, t-statistics,
percentile time-series of market cap and signal values, and a discussion
of why a signal that looks predictive in one cross-section can fail in the
time-series average.

*Code.* `src/fama_macbeth.py`, `src/percentiles.py`, `src/returns.py`,
`src/io.py`; one numbered script per question (`00_explore_data.py`
through `07_q10.py`).

### HW3 — China SOE Factor (methodology critique)
*Released Mar 24, due Apr 1.*

A pure thought piece. We are handed a memo proposing a "China State-Owned-
Enterprise" risk factor and asked (i) why SOE membership might be a unique
risk premium (governance / tail-policy-risk decomposition); (ii) what is
weak about the proposed construction; (iii) an alternative grounded in
Fama–MacBeth regressions and Bayesian (Vasicek-style) shrinkage; and
(iv) how to measure stock-level SOE exposure in a multi-PM platform setting.
The submission is a 12-page report — no code.

### HW4 — Loss probability, win rate, and drawdowns
*Released Apr 7, due Apr 15.*

Hedge-fund "Braggadocio Capital Management" is pitched at 8 % annualised
return and 4 % vol (Sharpe ≈ 2). The assignment derives, both analytically
and via Monte-Carlo, the probability of losing money over a year /
quarter / month / day; the relationship between Sharpe ratio, win rate
and up-down dollar ratio under varying μ and σ; and the probability of
observing a 90- or 120-day drawdown over 5- and 10-year commit horizons.
Closes with a Bayesian discussion of how long it takes an LP to learn the
true Sharpe of a manager.

### HW5 — Portfolio construction (the heavy one)
*Released Apr 14, due May 6.*

Given a 1 000-stock × 108-month return panel, five factor returns and a
Jan-2041 alpha forecast, build a five-factor risk model
($\Omega_R = B\Omega_F B^\top + \Omega_\varepsilon$) and use it to construct
a cascade of dollar-neutral long-short portfolios — unconstrained,
1 % / 50 bps / 10 % box-constrained, F1-neutral, sector-neutral, jointly
factor + sector neutral, and 2σ-shock-capped — all subject to a 10 %
annualised vol cap and (from part b on) a 2 %-of-ADV trading-capacity
constraint on a $100 M book. Report covers $\Omega_R$ construction, MVO
diagnostics (effective N bets, factor-vs-idio variance decomposition,
within-sector residual correlation, residual PCA, eigen-spectrum), the
financing of long-short books, capacity ranking at $1 B / 10× leverage
and a stack of advanced-method extensions: Hierarchical Risk Parity,
Michaud resampling, Black–Litterman, CVaR, James–Stein loading
shrinkage and a rolling-window time-varying $B$.

*Code.* `src/io.py`, `src/regression.py`, `src/covariance.py`,
`src/optimize.py`, `src/portfolio_inputs.py`, `src/diagnostics.py`,
`src/advanced_opt.py`, `src/plotting.py`; numbered scripts
`00_explore.py` → `12_corr_heatmap_fix.py`, one per problem (and per
extension).

### HW6 — "Guaranteed to lose money"
*Released Apr 28, due May 9. Closed-book.*

Design an investment process that is **guaranteed** (not merely likely)
to lose money over the next nine months without resorting to obvious
bid/ask wastage. Then explain whether flipping the sign of that strategy
would produce a guaranteed money-maker. A short essay on the limits of
arbitrage, transaction costs, capacity, signal decay and self-fulfilling
crowding.

---

## Reproducing the data-intensive homeworks

The Python environment for HW1, HW2 and HW5 is captured by the top-level
`requirements.txt`:

```bash
python3.10 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Each numbered script in `HW{n}/scripts/` is independently runnable from
its homework root, e.g.

```bash
cd HW5
python scripts/01_p1_factor_loadings.py
python scripts/07_p7_run_all.py
```

`HW5` additionally needs `cvxpy` (installed transitively) for the
quadratic-programming optimiser.

---

## Notes & disclaimers

- **Academic integrity.** This repository is published as a personal
  portfolio. If you are currently enrolled in 15.439, MIT's
  collaboration policy (Type 3) prohibits looking at any other group's
  solution. Don't use this code or these write-ups as a shortcut.
- The writing reflects my interpretation and conclusions; the instructor
  may grade other valid approaches differently.

---

*Last updated: May 2026.*
