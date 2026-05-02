# Q1 and Q2 Analysis

## Q1: Why does the dataset use PERMNO and not TICKERS?

**PERMNO** (permanent number) is CRSP's unique, permanent identifier for a security. It is stable over time and across corporate actions (splits, name changes, ticker changes). **TICKER** is the exchange symbol (e.g. AAPL); it can be reused (e.g. after a merger or delisting) and can change when a company changes its symbol. For panel data and linking across databases, PERMNO avoids ambiguity and ensures we track the same firm through time.

## Q2: Price_Ret(T1) vs PRC

### (a) Is the difference a data error or correct?

**Correct, not an error.** PRC is the **total return** over the prior month (price appreciation plus reinvested dividends). Price_Ret(T1) is the **price-only** return (percentage change in price). They differ when the stock pays dividends or when there are adjustments (e.g. splits) that affect total return but may be reflected differently in price. So whenever dividends or other distributions occur, PRC will exceed (or differ from) the simple price return.

### (b) Why are they equal for some companies?

They are equal when there is **no dividend** (and no other distribution or adjustment) in that month—so the total return equals the price return. In our sample: **65569** row-level comparisons are equal (within 1e-6), **24153** are different. **0** companies have Price_Ret_T1 == PRC for every date they appear; for the rest, equality holds only in some months (typically no-dividend months).
