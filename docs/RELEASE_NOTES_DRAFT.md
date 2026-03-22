# ApexLab Release Notes Draft

## 1.0.0

`1.0.0` is the first public ApexLab release: a deliberately lean toolkit centered on constrained modeling, deterministic data handling, compact evaluation helpers, and lightweight report generation.

### Added

- initial ApexLab package release
- simplex-constrained regression via `ApexRegressor`
- deterministic split utilities with optional stratification
- regression and classification metric helpers
- threshold selection and score-evaluation helpers
- JSON/Markdown evaluation report emission helpers
- runnable example scripts for regression and evaluation flows
- focused test coverage for core Leg 1 behaviors

### Dependency posture

- runtime dependency surface kept lean with `numpy` as the only non-stdlib dependency

### Validation status

- focused package test suite passing
- wheel build verified
- source distribution build verified
- wheel install smoke-tested
- source distribution install smoke-tested

### Notes for first publish

- this release is intentionally compact rather than comprehensive
- public surface area is kept small on purpose to support a clean first package publication
- broader ML toolkit growth is expected in later post-1.0 legs
