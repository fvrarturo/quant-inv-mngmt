# Problem 3 — factor covariance

Ω_F = E[FFᵀ]  (as defined in the handout).
Correlation derived with σ_i = √Ω_F[i,i].

## Ω_F (monthly)

| | factor_1 | factor_2 | factor_3 | factor_4 | factor_5 |
|---|---|---|---|---|---|
| factor_1 | 0.001322 | 0.000277 | 0.000048 | -0.000149 | -0.000104 |
| factor_2 | 0.000277 | 0.000516 | 0.000107 | -0.000164 | 0.000001 |
| factor_3 | 0.000048 | 0.000107 | 0.000503 | -0.000034 | 0.000194 |
| factor_4 | -0.000149 | -0.000164 | -0.000034 | 0.000230 | 0.000021 |
| factor_5 | -0.000104 | 0.000001 | 0.000194 | 0.000021 | 0.000206 |

## Correlation matrix

| | factor_1 | factor_2 | factor_3 | factor_4 | factor_5 |
|---|---|---|---|---|---|
| factor_1 | 1.000 | 0.336 | 0.059 | -0.270 | -0.200 |
| factor_2 | 0.336 | 1.000 | 0.209 | -0.476 | 0.004 |
| factor_3 | 0.059 | 0.209 | 1.000 | -0.099 | 0.605 |
| factor_4 | -0.270 | -0.476 | -0.099 | 1.000 | 0.097 |
| factor_5 | -0.200 | 0.004 | 0.605 | 0.097 | 1.000 |

**Most-correlated pair:** `factor_3` / `factor_5` with ρ = 0.605.

Figures: `results/figures/03_corr_factors.png` (and the demeaned variant).
