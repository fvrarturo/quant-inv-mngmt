# HW2 Plan: Momentum signals and cross-section

## Run

Use the project `.venv` (from repo root): e.g. `../.venv/bin/python scripts/00_explore_data.py` from `HW2/`, or activate the venv and run `python scripts/00_explore_data.py`.

## Data

- **SP500Raw.xlsx**: S&P 500 constituents by month (EOM), 2010-01 to 2024-12.
- Columns: permno, date, price, shrout, prc, mcap.
- Exploratory run: `scripts/00_explore_data.py` → `results/explore_summary.csv`, `results/companies_per_date.csv`, `md_files/explore_data.md`.

## Scripts → questions

| Script | Questions | Description |
|--------|-----------|-------------|
| `00_explore_data.py` | — | Load data, shape, nulls, companies per date, unique permnos, full-sample count. |
| `01_q1_q2.py` | Q1, Q2 | PERMNO vs TICKERS; Price_Ret(T1) vs PRC (save variable); 2a/2b explanation. |
| `02_q3_q5.py` | Q3, Q4, Q5 | Company counts; unique / full-sample; percentile sets (mcap): time series, prior to exit, on entry. |
| `03_q6.py` | Q6 | Trailing returns (i–vi), forward returns; one graph per variable with Percentile Sets; median of each percentile. |
| `04_q7.py` | Q7 | Fama-MacBeth: Nov 2019 single month; full sample coefficients; interpretation; performance measures. |
| `05_q8.py` | Q8 | Fama-MacBeth univariate (all predictors) and multivariate (specified pairs). |
| `06_q9.py` | Q9 | Fama-MacBeth with F3M/F6M; compare to 7(b); econometric issues and corrections. |
| `07_q10.py` | Q10 | Fama-MacBeth 7(b) with log(mcap) weighting; compare and discuss. |
| (write-up) | Q11 | First principles, what the homework teaches, different independent/dependent variables. |

## Shared code (src)

- **src/io.py**: `load_sp500(path)` — load Excel, parse dates, coerce numerics.
- **src/returns.py**: `build_full_panel(df)` — Price_Ret(T1), trailing returns (T12, T12M1, T12_1M), volatility, SR, forward returns (F1M, F3M, F6M); all geometric; optional `load_panel(path)` in io.
- **src/percentiles.py**: Percentile sets by date, plotting, entry/exit subsets for Q5a/5b.
- **src/fama_macbeth.py**: Cross-sectional OLS/WLS, `run_fama_macbeth`, inference, Newey-West, strategy_metrics.

## Outputs

- **results/**: CSVs, summary stats, coefficient series.
- **results/figures/**: Time series plots, percentile plots.
- **md_files/**: Per-question or combined analysis markdown.
