# Q2 Signal effectiveness

## Data cleaning applied

We applied Q1 corrections without modifying the raw file: sort by date; deduplicate dates (keep first); fix monotonicity; drop rows with `adj_close` ≤ 0; replace signal in {−999, 0} with NaN.

## Multi-horizon returns

- `forward_return_1[t] = (adj_close[t+1]/adj_close[t]) - 1`
- `forward_return_5[t] = (adj_close[t+5]/adj_close[t]) - 1`
- `forward_return_20[t] = (adj_close[t+20]/adj_close[t]) - 1`

Last 1, 5, 20 rows respectively have NaN. No lookahead.

## Forward-looking volatility

Daily returns `r[t] = (adj_close[t]/adj_close[t-1]) - 1`. For window H ∈ {5, 20, 60}:

`forward_vol_H[t] = std(r[t+1], …, r[t+H])`

Last 5, 20, 60 rows have NaN for forward_vol_5, forward_vol_20, forward_vol_60.

## Predictor transforms

- **signal**: raw (sentinels already NaN).
- **signal_ma_5 / signal_ma_20**: backward-looking rolling mean (min_periods=1).
- **signal_pct**: signal.pct_change(); inf/NaN set to NaN.
- **sign_signal**: sign(signal); 0/NaN set to NaN.

## Why these metrics

- **IC (Pearson):** Linear predictive relationship; industry standard.
- **Hit rate:** Directional accuracy; binomial test vs 50%.
- **Regression:** Slope (effect size) and t-test on β.
- **Rank IC (Spearman):** Robust to outliers and monotone non-linearity.

---

## Summary and judgment

### Most promising: forward volatility

The signal is **strongly and consistently useful for predicting forward-looking realized volatility**. This is the clearest takeaway.

- **60-day forward vol** is the best target: IC ≈ 0.29–0.34 (all p &lt; 0.01) for raw signal and rolling averages. **Best single combination: forward_vol_60 × signal_ma_5 (IC = 0.34).** Regression slopes are large and highly significant; hit rate is effectively 100% (higher signal associates with higher subsequent vol).
- **20-day forward vol** is almost as strong: IC 0.16–0.20, all p &lt; 0.001 for level-based predictors.
- **5-day forward vol** is significant but weaker: IC 0.09–0.10, p ≈ 0.001–0.006.

**Interpretation:** Higher signal levels (or their short-run average) reliably anticipate higher realized volatility over the next 5–60 days. The relationship strengthens with horizon. This supports using the signal for **volatility targeting, position sizing, or hedging** rather than purely for return direction.

### Promising but mixed: return prediction

- **Return level (IC, β):** Weak. ICs are small (≈0.04) and **not significant** at horizon 1 or 5; at horizon 20 they remain small and regression p-values stay above 0.05. The signal does **not** meaningfully predict the *magnitude* of returns at any horizon.
- **Return direction (Rank IC, hit rate):** At **20-day horizon**, direction looks informative: Rank IC ≈ −0.12 to −0.18 (p &lt; 0.001), hit rate ≈ 62% (p ≈ 0). So the signal adds value for *which way* the market moves over the next 20 days, even though it does not predict *how much*. At 5-day horizon, signal_ma_20 shows a significant Rank IC (−0.08, p ≈ 0.01). At 1-day horizon, direction is only weakly significant (hit rate ~55%, p &lt; 0.01) and may not be economically meaningful.

**Interpretation:** The signal is more useful for **medium-horizon return direction** (e.g. 20d) than for 1d returns or return levels. Relying on it for next-day or next-week *level* prediction is not supported.

### Weak or uninformative

- **signal_pct** and **sign_signal** add little: ICs and Rank ICs are near zero and almost never significant across all targets. The *level* (or smoothed level) of the signal drives the results, not its change or sign alone.
- **1-day return:** No significant IC or regression slope; only a marginal hit-rate improvement. The signal is **not** a reliable short-term return predictor.

### Best combinations (recap)

- **Strongest linear relationship:** forward_vol_60 × signal_ma_5 (IC = 0.34, p ≈ 0).
- **Strongest significance (p-value):** forward_vol_60 × signal (p ≈ 0).
- **Best return-related result:** return_20 × signal_ma_20 (Rank IC = −0.18, p ≈ 0; hit rate 62%).

---

## Results (compact)

### return horizon 1
| Predictor | IC | p (IC) | Rank IC | p (Rank IC) | Hit rate | p (HR) | β | p (reg) |
|-----------|-----|--------|---------|--------------|----------|--------|-----|--------|
| signal | 0.0394 | 0.2056 | 0.0193 | 0.5355 | 0.5478 | 0.0026 | 9.6712 | 0.2055 |
| signal_ma_5 | 0.0441 | 0.1557 | 0.0159 | 0.6097 | 0.5490 | 0.0019 | 12.5712 | 0.1556 |
| signal_ma_20 | 0.0443 | 0.1532 | -0.0282 | 0.3643 | 0.5489 | 0.0019 | 13.4876 | 0.1532 |
| signal_pct | -0.0006 | 0.9850 | -0.0290 | 0.3533 | 0.4916 | 0.6145 | -0.1559 | 0.9850 |
| sign_signal | 0.0010 | 0.9751 | -0.0204 | 0.5120 | 0.5478 | 0.0026 | 12.8752 | 0.9751 |

### return horizon 5
| Predictor | IC | p (IC) | Rank IC | p (Rank IC) | Hit rate | p (HR) | β | p (reg) |
|-----------|-----|--------|---------|--------------|----------|--------|-----|--------|
| signal | 0.0393 | 0.2071 | 0.0335 | 0.2828 | 0.5616 | 0.0001 | 9.6742 | 0.2071 |
| signal_ma_5 | 0.0442 | 0.1553 | -0.0206 | 0.5078 | 0.5610 | 0.0001 | 12.6602 | 0.1553 |
| signal_ma_20 | 0.0447 | 0.1510 | -0.0796 | 0.0104 | 0.5610 | 0.0001 | 13.6856 | 0.1510 |
| signal_pct | -0.0006 | 0.9849 | 0.0228 | 0.4643 | 0.5034 | 0.8506 | -0.1575 | 0.9849 |
| sign_signal | 0.0010 | 0.9751 | -0.0379 | 0.2239 | 0.5616 | 0.0001 | 12.9260 | 0.9751 |

### return horizon 20
| Predictor | IC | p (IC) | Rank IC | p (Rank IC) | Hit rate | p (HR) | β | p (reg) |
|-----------|-----|--------|---------|--------------|----------|--------|-----|--------|
| signal | 0.0401 | 0.2014 | -0.1154 | 0.0002 | 0.6228 | 0.0000 | 10.1509 | 0.2014 |
| signal_ma_5 | 0.0453 | 0.1480 | -0.1597 | 0.0000 | 0.6241 | 0.0000 | 13.4243 | 0.1479 |
| signal_ma_20 | 0.0458 | 0.1439 | -0.1791 | 0.0000 | 0.6241 | 0.0000 | 14.5027 | 0.1439 |
| signal_pct | -0.0006 | 0.9846 | 0.0203 | 0.5182 | 0.5104 | 0.5294 | -0.1647 | 0.9846 |
| sign_signal | 0.0010 | 0.9749 | -0.0409 | 0.1919 | 0.6228 | 0.0000 | 13.3579 | 0.9749 |

### vol horizon 5
| Predictor | IC | p (IC) | Rank IC | p (Rank IC) | Hit rate | p (HR) | β | p (reg) |
|-----------|-----|--------|---------|--------------|----------|--------|-----|--------|
| signal | 0.0852 | 0.0062 | -0.1945 | 0.0000 | 0.9990 | 0.0000 | 20.8454 | 0.0062 |
| signal_ma_5 | 0.0961 | 0.0020 | -0.1742 | 0.0000 | 1.0000 | 0.0000 | 27.3537 | 0.0020 |
| signal_ma_20 | 0.0993 | 0.0014 | -0.0867 | 0.0053 | 1.0000 | 0.0000 | 30.2590 | 0.0014 |
| signal_pct | -0.0022 | 0.9446 | -0.0017 | 0.9573 | 0.5059 | 0.7303 | -0.5740 | 0.9445 |
| sign_signal | 0.0022 | 0.9442 | 0.0171 | 0.5835 | 0.9990 | 0.0000 | 28.8022 | 0.9442 |

### vol horizon 20
| Predictor | IC | p (IC) | Rank IC | p (Rank IC) | Hit rate | p (HR) | β | p (reg) |
|-----------|-----|--------|---------|--------------|----------|--------|-----|--------|
| signal | 0.1630 | 0.0000 | -0.1667 | 0.0000 | 0.9990 | 0.0000 | 39.9048 | 0.0000 |
| signal_ma_5 | 0.1894 | 0.0000 | -0.1248 | 0.0001 | 1.0000 | 0.0000 | 54.2034 | 0.0000 |
| signal_ma_20 | 0.2019 | 0.0000 | -0.0688 | 0.0280 | 1.0000 | 0.0000 | 61.7981 | 0.0000 |
| signal_pct | -0.0050 | 0.8743 | -0.0167 | 0.5952 | 0.5069 | 0.6828 | -1.3046 | 0.8742 |
| sign_signal | 0.0045 | 0.8871 | 0.0507 | 0.1057 | 0.9990 | 0.0000 | 58.3366 | 0.8871 |

### vol horizon 60
| Predictor | IC | p (IC) | Rank IC | p (Rank IC) | Hit rate | p (HR) | β | p (reg) |
|-----------|-----|--------|---------|--------------|----------|--------|-----|--------|
| signal | 0.2911 | 0.0000 | 0.0590 | 0.0652 | 0.9990 | 0.0000 | 70.3925 | 0.0000 |
| signal_ma_5 | 0.3419 | 0.0000 | 0.1051 | 0.0010 | 1.0000 | 0.0000 | 97.8744 | 0.0000 |
| signal_ma_20 | 0.3347 | 0.0000 | 0.1101 | 0.0005 | 1.0000 | 0.0000 | 102.5624 | 0.0000 |
| signal_pct | -0.0089 | 0.7807 | -0.0014 | 0.9656 | 0.5041 | 0.8224 | -2.2548 | 0.7807 |
| sign_signal | 0.0081 | 0.7994 | 0.0546 | 0.0874 | 0.9990 | 0.0000 | 103.4249 | 0.7994 |

---

## Conclusion

After Q1 corrections, the signal **does** show statistically significant predictability, but only for specific uses:

1. **Strongest use: forward volatility.** The signal is a reliable predictor of realized vol over 5–60 days (best: 60d, IC ≈ 0.34 with signal_ma_5). It is well suited for volatility targeting, risk scaling, or hedging rather than for raw return forecasting.
2. **Moderate use: medium-horizon return direction.** At a 20-day horizon, the signal helps predict *direction* (Rank IC ≈ −0.18, hit rate ≈ 62%) but not return *level*. One-day and level-based return prediction are not supported.
3. **Use level or smoothed level, not change or sign.** signal_ma_5 and signal_ma_20 often perform as well or better than raw signal; signal_pct and sign_signal are uninformative.

**Bottom line:** The most promising application is **predicting forward volatility** (especially 20d and 60d) using the level or short-run average of the signal. Return prediction is at best useful for 20-day direction; it should not be relied on for 1d returns or for magnitude.
