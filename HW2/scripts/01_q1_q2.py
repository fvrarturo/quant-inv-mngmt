#!/usr/bin/env python3
"""
Q1: Why PERMNO and not TICKERS?
Q2: Price_Ret(T1) vs PRC — (a) data error or correct? (b) Why equal for some companies?
    Save Price_Ret(T1) for later use.
"""
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
HW2_DIR = SCRIPT_DIR.parent
DATA_PATH = HW2_DIR / "SP500Raw.xlsx"
RESULTS_DIR = HW2_DIR / "results"
MD_DIR = HW2_DIR / "md_files"

sys.path.insert(0, str(HW2_DIR))

from src.io import load_sp500


def main() -> None:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else DATA_PATH
    if not path.exists():
        print(f"Data file not found: {path}")
        sys.exit(1)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    df = load_sp500(path)
    df = df.sort_values(["permno", "date"])
    # Price_Ret(T1): one-month price return
    df["price_lag"] = df.groupby("permno")["price"].shift(1)
    df["Price_Ret_T1"] = (df["price"] / df["price_lag"]) - 1

    # Compare to prc
    diff = (df["Price_Ret_T1"] - df["prc"]).abs()
    equal = (diff < 1e-6) & df["Price_Ret_T1"].notna() & df["prc"].notna()
    different = (diff >= 1e-6) & df["Price_Ret_T1"].notna() & df["prc"].notna()

    print("Q2 preview: Price_Ret(T1) vs PRC")
    print("  Rows where equal (within 1e-6):", equal.sum())
    print("  Rows where different:", different.sum())
    # Which permnos always equal?
    by_permno = df.groupby("permno", group_keys=False).apply(
        lambda g: ((g["Price_Ret_T1"] - g["prc"]).abs() < 1e-6).all()
        if g["Price_Ret_T1"].notna().any() and g["prc"].notna().any() else False,
        include_groups=False,
    )
    always_equal = by_permno[by_permno].index.tolist()
    print("  Permnos where Price_Ret_T1 == PRC for all dates:", len(always_equal))

    # Save dataset with Price_Ret_T1 for downstream scripts
    out = RESULTS_DIR / "data_with_Price_Ret_T1.csv"
    df.drop(columns=["price_lag"], errors="ignore").to_csv(out, index=False)
    print(f"\nSaved data with Price_Ret_T1 to {out}")

    # Q1_Q2_analysis.md
    MD_DIR.mkdir(parents=True, exist_ok=True)
    n_equal = int(equal.sum())
    n_diff = int(different.sum())
    n_always = len(always_equal)
    md = f"""# Q1 and Q2 Analysis

## Q1: Why does the dataset use PERMNO and not TICKERS?

**PERMNO** (permanent number) is CRSP's unique, permanent identifier for a security. It is stable over time and across corporate actions (splits, name changes, ticker changes). **TICKER** is the exchange symbol (e.g. AAPL); it can be reused (e.g. after a merger or delisting) and can change when a company changes its symbol. For panel data and linking across databases, PERMNO avoids ambiguity and ensures we track the same firm through time.

## Q2: Price_Ret(T1) vs PRC

### (a) Is the difference a data error or correct?

**Correct, not an error.** PRC is the **total return** over the prior month (price appreciation plus reinvested dividends). Price_Ret(T1) is the **price-only** return (percentage change in price). They differ when the stock pays dividends or when there are adjustments (e.g. splits) that affect total return but may be reflected differently in price. So whenever dividends or other distributions occur, PRC will exceed (or differ from) the simple price return.

### (b) Why are they equal for some companies?

They are equal when there is **no dividend** (and no other distribution or adjustment) in that month—so the total return equals the price return. In our sample: **{n_equal}** row-level comparisons are equal (within 1e-6), **{n_diff}** are different. **{n_always}** companies have Price_Ret_T1 == PRC for every date they appear; for the rest, equality holds only in some months (typically no-dividend months).
"""
    (MD_DIR / "Q1_Q2_analysis.md").write_text(md, encoding="utf-8")
    print(f"Wrote md_files/Q1_Q2_analysis.md")


if __name__ == "__main__":
    main()
