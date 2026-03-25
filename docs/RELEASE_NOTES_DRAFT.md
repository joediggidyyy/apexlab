# ApexLab Release Notes Draft

## 1.2.0

`1.2.0` is the next clean minor release after the GitHub/PyPI patch-lane mismatch. It rolls the current validated ApexLab tree forward under a single coherent version and promotes the recent model-family expansion into the public package surface.

### Added

- deterministic anomaly detection via `IsolationForest`
- deterministic binary `DecisionTreeClassifier`
- deterministic binary `RandomForestClassifier`

### Retained and validated

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
- lite CLI commands:
	- `apexlab compare`
	- `apexlab report`
	- `apexlab --version`
	- `apexlab -v`
- stable comparison-report emission and rerendering
- field-test execution via `examples/evaluation_demo.py`
- reference validation against SciPy / scikit-learn baselines for the analytical lane

### Release rationale

- resolves the current GitHub/PyPI version drift by moving to a fresh minor release instead of extending the confusing `1.1.x` patch lane further
- packages the now-validated Leg 2 model-family expansion under a single release identity
- preserves the lean runtime dependency posture with `numpy` as the only non-stdlib dependency

### Validation status

- supervised-model slice passing
- full ApexLab suite passing
- release version surfaces synchronized to `1.2.0`

## 1.1.2

`1.1.2` is the corrected patch-release lane after the failed `1.1.1` PyPI upload attempt.

### Fixed

- retains the CLI version-surface repair:
	- `apexlab --version`
	- `apexlab -v`
- corrects the package/release lane after the aborted `1.1.1` publish attempt
- supersedes the deleted `v1.1.1` release/tag path with a clean patch-version continuation

### Validation status

- targeted CLI regression tests passing
- full ApexLab suite passing on the repaired patch lane
- fresh build artifacts verified for the corrected patch version before release

### Release note

- this patch remains intentionally narrow and exists to deliver the CLI version fix through a clean publishable release after the failed `1.1.1` upload path

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
