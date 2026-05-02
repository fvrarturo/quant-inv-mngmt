# Q1 Data Quality Analysis: WKKWNT 4sight Sample Dataset

**15.439 Quantitative Investment Management — Assignment 1**  
This document summarizes all issues identified by the initial analysis pipeline (`scripts/01_initial_analysis.py`) on the WKKWNT sample dataset (1,045 rows, 7 columns: Date, Signal, Open, High, Low, Close, Adj Close). Findings are reported check-by-check with interpretation and recommended corrections. Raw data is left unchanged; corrections belong in a separate ledger/spreadsheet per assignment instructions.

---

## 1. Null counts

**Check:** Count of missing values per column.

**Findings:**
- **low:** 1 null (0.1% of rows). All other columns have zero nulls.

**Interpretation:** A single missing Low price prevents consistent OHLC bracket checks for that row and may indicate a vendor feed gap or typo.

**Recommended correction:** Log the row index and date in the corrections ledger; either impute (e.g. interpolate from Open/High/Close or copy from previous day) or drop that row for time-series analysis. Verify with source data before imputing.

---

## 2. Duplicate dates

**Check:** Calendar dates that appear more than once.

**Findings:**
- **2016-08-19:** 2 copies (row indices 189, 190).
- **2016-10-31:** 2 copies (row indices 240, 241).
- **2016-11-03:** 2 copies (row indices 244, 245).

**Interpretation:** Duplicate dates break the assumption of one observation per trading day and can distort returns, rolling statistics, and point-in-time backtests. They may be copy-paste errors or double submissions from the vendor.

**Recommended correction:** Resolve per duplicate-content audit (Check 3): keep first and drop rest when content is identical; escalate to vendor when content conflicts.

---

## 3. Duplicate content audit

**Check:** For each duplicate date, compare OHLC and Signal across copies.

**Findings:**

| Date       | Copies | Identical? | Recommendation           |
|-----------|--------|------------|---------------------------|
| 2016-08-19 | 2      | Y          | keep_first_drop_rest      |
| 2016-10-31 | 2      | N          | vendor_conflict_escalate  |
| 2016-11-03 | 2      | Y          | keep_first_drop_rest      |

**Interpretation:** Two duplicate dates are exact duplicates (safe to de-duplicate by keeping the first row). **2016-10-31** has conflicting OHLC and/or Signal between the two rows—this is a data integrity issue and must be escalated to WKKWNT; do not silently keep one row without vendor confirmation.

**Recommended correction:** For 2016-08-19 and 2016-11-03: document “drop duplicate row (second copy)” in the corrections ledger. For 2016-10-31: log “vendor conflict; request correct values from WKKWNT” and exclude or flag that date until resolved.

---

## 4. Monotonic dates

**Check:** Dates must be non-decreasing (no time travel).

**Findings:**
- **Row 404:** date **2017-06-21** immediately follows **2020-06-20** (previous row). This is a 1,097-day backward jump.

**Interpretation:** A block of 2020 data appears to be mis-sorted or pasted into the 2017 section. Rolling calculations, train/test splits, and any time-based logic are invalid across this break. This is a critical structural error.

**Recommended correction:** Log in the corrections ledger: “Row 404 date 2017-06-21 is out of order; previous row is 2020-06-20. Relocate row to correct chronological position or exclude until vendor confirms.” Re-sort the dataset by date before any analysis, or drop the misplaced row if it duplicates a true 2020 row.

---

## 5. Date coverage

**Check:** US business-day calendar between min and max dates vs. observed dates; missing sessions by year.

**Findings:**

| Year | Missing sessions |
|------|-------------------|
| 2015 | 2                 |
| 2016 | 9                 |
| 2017 | 9                 |
| 2018 | 15                |
| 2019 | 9                 |
| 2020 | 120               |

Sample missing dates (first 10): 2015-11-26, 2015-12-25, 2016-01-01, 2016-01-18, 2016-02-15, 2016-03-25, 2016-05-30, 2016-07-04, 2016-09-05, 2016-11-24.

**Interpretation:** Many missing dates are holidays (e.g. Christmas, New Year’s Day, July 4th) or weekends—expected for equity data. The **120 missing sessions in 2020** are likely driven by the mis-placed 2020 row (see Check 4) and the resulting truncation or gap in the 2020 range. Confirm with a proper chronological sort and re-run coverage.

**Recommended correction:** Document “missing business days vs. calendar” in the ledger. After fixing the monotonicity issue, re-check 2020 coverage. No need to “fix” holiday/weekend gaps; use them only for awareness.

---

## 6. Weekend / holiday check

**Check:** Flag weekend (Saturday/Sunday) dates in the series.

**Findings:** 9 weekend dates, e.g. 2016-01-03, 2017-02-11, 2017-02-12, 2020-06-20, 2018-05-19, 2018-05-20, 2018-06-23, 2018-06-24, 2019-04-21.

**Interpretation:** Equity data should typically be business-day only. Weekend dates suggest vendor feed quirks or different exchange calendars. 2020-06-20 ties to the monotonicity issue (row 404).

**Recommended correction:** Log these dates in the corrections ledger. Consider excluding weekend rows for return/volatility analysis or flag them in the treated dataset. Do not “fix” without confirming vendor intent.

---

## 7. Negative / zero prices

**Check:** Rows where Adj Close ≤ 0.

**Findings:**
- **Row 648 (2018-06-06):** adj_close = 0.000000.
- **Row 738 (2018-10-10):** adj_close = -152.277847.

**Interpretation:** Prices should be strictly positive. Zero produces infinite returns; negative is impossible for a long-only ETF. These are almost certainly bad ticks or data errors and will severely distort returns and any downstream metrics.

**Recommended correction:** Log in the corrections ledger: “Replace with NaN or remove row; do not use for return calculation.” Optionally impute from Close or neighboring days only after vendor confirmation. Null out forward and backward returns that use these prices.

---

## 8. OHLC bracket check

**Check:** High ≥ Low; Low ≤ Open ≤ High; Low ≤ Close ≤ High (when bracket is valid). Boolean columns appended to `Treated_datasample.csv`.

**Findings:**
- **high < low:** 3 violations.
- **open not in [low, high]:** 3 violations.
- **close not in [low, high]:** 17 violations.

**Interpretation:** Violations indicate inconsistent OHLC (e.g. Close outside the day’s range) or bad ticks. The 17 close violations are material for return and bracket consistency. The three “high < low” rows have an invalid bracket; open/close bracket flags are set to NaN for those rows by design.

**Recommended correction:** Document each violating row (date and check type) in the corrections ledger. Request corrected OHLC from vendor for those dates or exclude them from analyses that assume valid OHLC. Use the boolean columns in `Treated_datasample.csv` to filter or weight observations.

---

## 9. Adj Close vs Close

**Check:** Count and list rows where |Adj Close − Close| > 1e-6.

**Findings:** 1,045 mismatches (100% of rows). Differences are on the order of several dollars (e.g. 7.78, 7.83, 7.87, …).

**Interpretation:** Adj Close and Close are expected to differ: Adj Close is adjusted for splits and dividends. A systematic difference across the sample is **not** an error—it reflects the adjustment factor. This check is diagnostic only.

**Recommended correction:** None. Use Adj Close for return-based analysis; use Close only when comparing to unadjusted vendor or exchange data. Do not list as an “error” in the corrections ledger.

---

## 10. Return outliers

**Check:** Single-period (day-over-day) returns with |r| > 20%.

**Findings:** 15 rows with extreme returns, including:
- 2017-06-14: −99.0%; 2017-06-15: +9,849%.
- 2018-06-06: −100%; 2018-06-07: **inf** (division by zero from prior 0 price).
- 2018-08-07: −100%; 2018-08-08: +2.64e6%.
- 2018-10-10 / 2018-10-11: ≈ −197% and −198%.
- 2019-08-05 / 2019-08-06: +94% and −49.5%.

**Interpretation:** These coincide with the zero/negative prices and OHLC issues already flagged. They are symptoms of bad prices, not genuine market moves. The **inf** return is a direct consequence of the 2018-06-06 zero price.

**Recommended correction:** Fix or drop the underlying bad prices (Check 7); then recompute returns. Do not winsorize without addressing the root cause. Document in the ledger: “Extreme returns driven by bad ticks; corrected by price correction.”

---

## 11. Signal sentinels

**Check:** Sentinel values in the 4sight signal: −999 and runs of zeros.

**Findings:**
- **−999:** 1 occurrence (2018-05-20).
- **0:** 6 occurrences (2019-12-27, 2019-12-30, 2019-12-31, 2020-01-02, 2020-01-03, 2020-01-06).

**Interpretation:** −999 is commonly used for “missing” or “no signal.” The six zeros at year-end 2019/early 2020 may indicate “no forecast” or feed outage rather than a true zero signal. Using these as numeric signals would bias IC and hit-rate metrics.

**Recommended correction:** Log in the corrections ledger: “Treat −999 and the six zeros as missing (NaN) for signal-based analysis.” Confirm with WKKWNT that −999 and 0 mean “unavailable.” Exclude or null these rows when computing IC, hit rate, and strategy returns.

---

## 12. Signal z-score

**Check:** Flag rows where |signal z-score| > 5.

**Findings:** 1 row (2018-05-20, signal = −999.0, z-score ≈ −32.09).

**Interpretation:** This is the same sentinel row as in Check 11. The extreme z-score is entirely due to the −999 placeholder.

**Recommended correction:** Same as Check 11: treat −999 as missing. No separate correction needed once sentinels are handled.

---

## 13. Signal day-over-day jumps

**Check:** Day-over-day change in signal exceeding 5 sigma.

**Findings:** 2 rows:
- 2018-05-20: signal −999, change ≈ 1019.4 (≈32.2 sigma).
- 2018-05-21: signal 19.03, change ≈ 1018.0 (≈32.2 sigma).

**Interpretation:** The jump is from −999 (missing) to a normal level. This is consistent with sentinel coding, not a genuine signal move.

**Recommended correction:** Treat 2018-05-20 as missing; no additional fix for 2018-05-21 beyond sentinel handling.

---

## 14. Corporate action ratio

**Check:** Abrupt changes in the ratio Adj Close / Close (e.g. >5% day-over-day), indicating possible splits/dividends or errors.

**Findings:** 12 rows with abrupt ratio changes, including:
- 2016-12-05 / 2016-12-06, 2017-03-27 / 2017-03-28: large ratio moves.
- 2018-03-19 / 2018-03-20: ratio 0.77 → 0.96.
- 2018-06-06: ratio 0 (Adj Close = 0); 2018-06-07: inf (prior 0).
- 2018-08-07 / 2018-08-08: small move from very low price (0.006).
- 2018-10-10 / 2018-10-11: negative Adj Close (−152.28) and ratio ≈ −0.97 / 0.97.

**Interpretation:** Some dates align with known bad prices (zero, negative). Others may reflect real corporate actions; the ratio time series helps distinguish data errors from legitimate adjustments.

**Recommended correction:** For rows already flagged as bad prices (zero/negative), correct prices first. For the rest, document “abrupt ratio change on [date]; verify split/dividend or vendor error” in the ledger. Do not automatically “fix” without confirmation.

---

## 15. Schema / dtypes

**Check:** Column dtypes and snapshot for future diff (e.g. after vendor refresh).

**Findings:** date (datetime64[us]), signal, open, high, low, price, adj_close (float64). Schema snapshot saved to `results/schema_snapshot.csv`.

**Interpretation:** All numeric columns are numeric; no inadvertent string columns in the normalized pipeline. Use the snapshot to detect schema drift (e.g. dates read as strings) on future data drops.

**Recommended correction:** None. Re-run schema check after each vendor refresh and diff against this snapshot.

---

## 16. Date gaps

**Check:** Gaps between consecutive calendar dates exceeding 5 days.

**Findings:**
- **2018-11-09 → 2018-11-19:** 10-day gap.
- **2020-01-06 → 2020-06-20:** 166-day gap.

**Interpretation:** The 10-day gap may be a market closure, holiday cluster, or feed outage. The 166-day gap is largely an artifact of the monotonicity error: the 2020-06-20 row appears earlier in the file (before 2017-06-21), so the “next” date after 2020-01-06 in sorted order is 2020-06-20 after re-sorting. After fixing the order, 2020 coverage should be re-assessed.

**Recommended correction:** Log both gaps. After correcting the misplaced 2020 row (Check 4), re-run the gap check. Investigate the 10-day gap with the vendor if it does not match known closures.

---

## 17. Issue summary

**Check:** Aggregate counts across the main checks (nulls, duplicate dates, monotonic violations, negative/zero prices, return outliers, signal sentinels, OHLC bracket violations, gaps).

**Findings:**

| Check name               | Count |
|--------------------------|-------|
| null_values              | 1     |
| duplicate_dates          | 6     |
| monotonic_violations     | 1     |
| negative_zero_prices     | 2     |
| return_outliers_20pct    | 15    |
| signal_sentinels         | 7     |
| ohlc_bracket_violations  | 23    |
| gaps_gt_5_days           | 2     |

**Interpretation:** There are exactly 23 OHLC bracket violations (17 “close not in [low, high]” + 3 “high < low” + 3 “open not in [low, high]”). Previous references or summaries which suggested over a thousand OHLC violations were incorrect and likely caused by double-counting or improper handling of NaNs. The specific breakdown in Check 8 reflects the true error count and the most important consistency issues are captured by this detailed tally. Other counts match those described in earlier sections.

**Recommended correction:** Use this summary for high-level reporting. For the corrections ledger, use the per-check details (sections 1–16) so each error is listed and corrected once.

---

## Summary table for corrections ledger

| # | Issue type           | Severity   | Count / key dates                    | Proposed action |
|---|----------------------|------------|--------------------------------------|------------------|
| 1 | Null (low)           | Low        | 1 row                                | Impute or drop; log row/date |
| 2 | Duplicate dates       | Medium     | 3 dates, 6 rows                      | Keep first for 2 dates; escalate 2016-10-31 |
| 3 | Monotonic date       | Critical   | Row 404 (2017-06-21 after 2020-06-20)| Re-sort or relocate row; re-check coverage/gaps |
| 4 | Negative/zero price  | Critical   | 2 rows (2018-06-06, 2018-10-10)      | Replace with NaN or drop; null returns |
| 5 | OHLC bracket         | Medium     | 3 high<low; 3 open; 17 close         | Log rows; exclude or request correction |
| 6 | Return outliers      | Symptom    | 15 rows                              | Resolved by fixing bad prices |
| 7 | Signal sentinels     | Medium     | 1× −999, 6× 0                        | Treat as missing; confirm with WKKWNT |
| 8 | Weekend dates        | Low        | 9                                    | Log; optionally exclude |
| 9 | Gaps                 | Informational | 10d, 166d                          | Re-check after monotonicity fix |
|10 | Adj Close ≠ Close    | Not error  | All rows                            | No correction; use Adj Close for returns |

---

## Conclusions

1. **Do not modify the raw data file.** Record every error and proposed correction in a separate spreadsheet (issues_found + corrections_proposed) as required by the assignment.
2. **Critical fixes:** Resolve the monotonic date (row 404), the two negative/zero prices, and duplicate dates (especially the conflicting 2016-10-31). Treat signal −999 and the six zeros as missing in any signal evaluation.
3. **OHLC:** Use the boolean columns in `Treated_datasample.csv` to filter or flag rows for analysis; document OHLC violations (23 total) in the ledger and request corrections where needed.
4. **Adj Close vs Close:** The full-sample “mismatch” is expected; use Adj Close for returns and do not log as an error.
5. **Next steps:** Build the issues_found and corrections_proposed spreadsheets from this analysis, then re-run the pipeline on a corrected (or filtered) copy to obtain clean metrics for signal effectiveness (Assignment 1, part 2).
