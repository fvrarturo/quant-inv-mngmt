# Data exploration: SP500Raw.xlsx

## Summary

| Metric | Value |
|--------|-------|
| n_rows | 90525 |
| n_columns | 6 |
| date_min | 2010-01-29 00:00:00 |
| date_max | 2024-12-31 00:00:00 |
| n_unique_dates | 180 |
| n_unique_permno | 795 |
| n_permno_full_sample | 285 |
| n_companies_min_per_date | 500 |
| n_companies_max_per_date | 506 |
| n_companies_median_per_date | 503 |

## Columns

- **permno**: identifier (CRSP permanent number)
- **date**: month-end date
- **price**: average of bid/ask at close
- **shrout**: shares outstanding (000's)
- **prc**: total return from prior period (e.g. prior month return)
- **mcap**: market cap (000's)

## Companies per date

Count of constituents per month: min=500, max=506, median=503. Not always 500 due to index reconstitution and data availability.

## Outputs

- `results/companies_per_date.csv`: number of companies per date
- `results/explore_summary.csv`: one-row summary of exploration
