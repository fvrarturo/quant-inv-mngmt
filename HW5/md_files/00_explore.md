# HW5 data exploration

## Panel (`data.xlsx`)

- rows: 95,631
- unique `mrap_id`: 1000
- unique dates: 108 (2031-01-31 → 2039-12-31)
- stocks with full 108-month history: 778
- stocks with partial history: 222

## Factors (`factors.xlsx`)

- 5 factor columns + risk-free rate, 108 monthly observations.

## Estimates (`estimates.xlsx`)

- rows: 1000; Jan 2041 snapshot with realized `ret` and predicted `pred`.
- sectors (first two NAICS digits): 24 unique sectors.

See `results/00_sector_counts.csv` for the sector distribution.
