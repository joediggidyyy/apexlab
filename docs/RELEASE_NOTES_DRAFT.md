# ApexLab Release Notes Draft

## 1.1.1

`1.1.1` is a focused patch release that corrects the ApexLab CLI version surface after the `1.1.0` publish.

### Fixed

- added top-level CLI version flags:
	- `apexlab --version`
	- `apexlab -v`
- added regression coverage so the CLI version surface is now explicitly tested

### Validation status

- targeted CLI regression tests passing
- version-flag behavior verified from the patched package surface

### Release note

- this patch is intentionally narrow and exists to repair the published command-line UX without changing the broader `1.1.0` analytical/reporting surface

## 1.1.0

`1.1.0` is the first post-initial ApexLab release: it keeps the package lean while adding the first Leg 2 analytical and reporting expansion required for public downstream consumption.

### Added

- simplex-constrained regression via `ApexRegressor`
- statistical comparison helpers:
	- `mann_whitney_u`
	- `ks_two_sample`
	- `welch_t_test`
	- `cohens_d`
	- `compare_distributions`
- lightweight regression-analysis helpers:
	- `ols_fit`
	- `ols_predict`
	- `logistic_fit`
	- `logistic_predict_proba`
	- `logistic_predict`
	- `summarize_coefficients`
- deterministic split utilities with optional stratification
- regression and classification metric helpers
- threshold selection and score-evaluation helpers
- JSON/Markdown evaluation report emission helpers
- comparison-report builder with stable report schema and machine-readable flags
- lite CLI commands:
	- `apexlab compare`
	- `apexlab report`
- runnable example scripts for regression and evaluation flows
- external reference-validation runner
- focused test coverage for core Leg 1 behaviors

### Validation status

- focused ApexLab test suite passing
- full ApexLab suite passing
- field test executed successfully via `examples/evaluation_demo.py`
- external reference-validation run passed against SciPy / scikit-learn baselines for the analytical lane

### Dependency posture

- runtime dependency surface kept lean with `numpy` as the only non-stdlib dependency

### Notes for publish

- this release is still intentionally compact rather than comprehensive
- the package is now suitable for public downstream consumers that depend on the analytical/reporting lane being available from the package index
- broader ML toolkit growth is still expected in later post-`1.1.0` legs, especially model-family expansion
