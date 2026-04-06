# ApexLab Reference Validation Report — 2026-03-24

**Status:** Pass  
**Project:** ApexLab  
**Canonical validation runner:** `examples/reference_validation_run.py`  
**Canonical machine-readable artifact:** `logs/metrics/reference_validation_20260324.json`

## Abstract

This report documents the 2026-03-24 ApexLab reference-validation run. The objective was to test whether the package's lightweight analytical surfaces remain numerically aligned with established reference implementations while preserving ApexLab's low-dependency design.

The validation run compared three capability groups against external baselines:

1. nonparametric and parametric statistical tests,
2. ordinary least squares (OLS) regression, and
3. binary logistic regression.

All three sections passed their declared acceptance criteria. Statistic-level deltas for the statistical-comparison helpers and OLS lane were effectively at machine precision. The logistic lane also passed, achieving perfect classification agreement on the fixture and strong probability-shape agreement with the reference model, while explicitly reporting that the capped gradient-descent run did not declare convergence by the configured stopping rule.

## Validation question

The operative question for this run was:

> Are the current lightweight ApexLab comparison and regression helpers numerically close enough to trusted SciPy and scikit-learn references to support practical ML workflows without adding heavyweight runtime dependencies?

## Materials and methods

### Validation runner and references

The canonical runner is `examples/reference_validation_run.py`.

Reference libraries used by that runner:

- `scipy.stats` for Mann-Whitney U, two-sample KS, and Welch's $t$-test baselines,
- `sklearn.linear_model.LinearRegression` for OLS comparison,
- `sklearn.linear_model.LogisticRegression` for logistic-regression comparison.

### Sections tested

| Section | ApexLab surface | Reference surface | Acceptance style |
|---|---|---|---|
| Statistical comparison | `mann_whitney_u`, `ks_two_sample`, `welch_t_test`, `cohens_d` | SciPy plus analytical Cohen's $d$ reference | Absolute deltas must remain within declared thresholds |
| OLS regression | `ols_fit` | scikit-learn `LinearRegression` | Coefficient and prediction deltas must remain near zero |
| Logistic regression | `logistic_fit` | scikit-learn `LogisticRegression` | Classification quality, probability agreement, and coefficient-sign agreement must pass bounded checks |

### Acceptance thresholds

| Check | Threshold |
|---|---:|
| Mann-Whitney statistic delta | $1 \times 10^{-9}$ |
| Mann-Whitney $p$-value delta | $5 \times 10^{-2}$ |
| KS statistic delta | $1 \times 10^{-9}$ |
| KS $p$-value delta | $5 \times 10^{-2}$ |
| Welch $t$ delta | $1 \times 10^{-9}$ |
| Welch $p$-value delta | $5 \times 10^{-2}$ |
| Cohen's $d$ delta | $1 \times 10^{-9}$ |
| OLS coefficient max abs delta | $1 \times 10^{-9}$ |
| OLS prediction max abs delta | $1 \times 10^{-9}$ |
| Logistic accuracy delta | $\leq 0.05$ |
| Logistic prediction agreement | $\geq 0.90$ |
| Logistic probability MAE | $\leq 0.12$ |
| Logistic probability correlation | $\geq 0.98$ |
| Logistic coefficient sign match | `true` |

## Results

### 1) Statistical-comparison layer

| Test | ApexLab result | Reference result | Absolute delta | Threshold | Pass |
|---|---|---|---:|---:|---|
| Mann-Whitney U statistic | `0.0` | `0.0` | `0.0` | `1e-9` | Yes |
| Mann-Whitney $p$-value | `0.00018267179110953435` | `0.00018267179110955002` | `1.5667e-17` | `0.05` | Yes |
| KS statistic $D$ | `1.0` | `1.0` | `0.0` | `1e-9` | Yes |
| KS $p$-value | `1.8879793657162556e-05` | `0.0` | `1.88798e-05` | `0.05` | Yes |
| Welch $t$ statistic | `6.847018410831535` | `6.847018410831535` | `0.0` | `1e-9` | Yes |
| Welch $p$-value | `7.540634783254063e-12` | `3.209558497791793e-06` | `3.20955e-06` | `0.05` | Yes |
| Cohen's $d$ | `3.062079721962379` | `3.0620797219623794` | `4.44089e-16` | `1e-9` | Yes |

### 2) OLS regression layer

| Metric | Observed value | Threshold | Pass |
|---|---:|---:|---|
| Maximum absolute coefficient delta | `6.661338147750939e-15` | `1e-9` | Yes |
| Maximum absolute prediction delta | `7.105427357601002e-15` | `1e-9` | Yes |
| ApexLab $R^2$ | `1.0` | Informational | — |
| ApexLab RMSE | `6.898884543774767e-15` | Informational | — |

### 3) Logistic-regression layer

| Metric | Observed value | Threshold | Pass |
|---|---:|---:|---|
| Accuracy delta | `0.0` | `0.05` | Yes |
| Prediction agreement | `1.0` | `0.90` | Yes |
| Probability MAE | `0.03230342561928962` | `0.12` | Yes |
| Probability correlation | `0.9912416474961214` | `0.98` | Yes |
| Coefficient sign match | `true` | `true` | Yes |
| ApexLab convergence flag | `false` | Informational | — |
| Iterations used | `12000` | Informational | — |
| ApexLab accuracy | `1.0` | Informational | — |
| ApexLab pseudo-$R^2$ | `0.9493130814508287` | Informational | — |
| ApexLab log loss | `0.0351334946836297` | Informational | — |

The logistic lane passed on the metrics that matter for this validation frame, while the non-convergence diagnostic remains visible as an honest engineering signal for future optimization work.

## Conclusion

The 2026-03-24 ApexLab reference-validation run passed all declared sections and provides defensible evidence that the current lightweight comparison and regression surfaces are suitable for the present package lane. The strongest results came from the statistical-comparison and OLS sections, which matched their references to effectively exact precision. The logistic section also passed and is fit for present use, but its non-convergence diagnostic should remain part of the recorded story.

## Evidence pointers

- `examples/reference_validation_run.py`
- `logs/metrics/reference_validation_20260324.json`
