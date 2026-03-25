# ApexLab Reference Validation Report — 2026-03-24

**Status:** Pass  
**Validation run timestamp (UTC):** 2026-03-25T03:48:28.484861Z  
**Canonical machine-readable artifact:** `projects/apexlab/logs/metrics/reference_validation_20260324.json`  
**Canonical validation runner:** `projects/apexlab/examples/reference_validation_run.py`

## Purpose

This report is the public-facing summary of the 2026-03-24 ApexLab reference-validation run.

Its purpose is to show that the new Leg 2 statistical-comparison and regression surfaces were checked against established external references without making those external libraries part of the ApexLab runtime dependency contract.

ApexLab remains a NumPy-first package at runtime. External libraries were used here only as validation references.

## Scope

The validation run compared ApexLab outputs against established reference implementations for three surface groups:

1. statistical comparison helpers
2. ordinary least squares regression
3. binary logistic regression

Reference libraries available in the validation environment included SciPy, scikit-learn, and statsmodels. The implemented run compared ApexLab directly against SciPy and scikit-learn for the covered fixtures.

## Validated surfaces

### Statistical comparison helpers

Validated ApexLab functions:

- `mann_whitney_u`
- `ks_two_sample`
- `welch_t_test`
- `cohens_d`

Validation fixture summary:

- sample sizes: $n_a = 10$, $n_b = 10$
- overall section status: **pass**

Observed ApexLab vs reference deltas:

- Mann-Whitney U statistic delta: `0.0`
- Mann-Whitney p-value delta: `1.566672139241554e-17`
- KS statistic delta: `0.0`
- KS p-value delta: `1.8879793657162556e-05`
- Welch t statistic delta: `0.0`
- Welch p-value delta: `3.20955095715701e-06`
- Cohen's d delta: `4.440892098500626e-16`

Interpretation:

- rank/statistic agreement was exact for the chosen fixtures
- p-value differences remained within intentionally loose tolerance bands because ApexLab uses SciPy-free approximations for those probabilities
- the comparison layer is therefore behaving as expected for the validated fixtures

### OLS regression

Validated ApexLab functions:

- `prepare_design_matrix`
- `ols_fit`
- `ols_predict`

Validation fixture summary:

- overall section status: **pass**
- fitted model type: `ols`
- sample count: `6`
- ApexLab fit reported `converged: true`
- ApexLab regression metrics included `r2 = 1.0`

Observed ApexLab vs reference deltas:

- coefficient max absolute delta: `6.661338147750939e-15`
- prediction max absolute delta: `7.105427357601002e-15`

Interpretation:

- coefficient and prediction agreement were effectively exact to floating-point precision for the chosen fixture
- the OLS implementation is suitable for the current lightweight package lane

### Logistic regression

Validated ApexLab functions:

- `logistic_fit`
- `logistic_predict_proba`
- `logistic_predict`
- `pseudo_r_squared`
- `binary_cross_entropy`

Validation fixture summary:

- overall section status: **pass**
- fitted model type: `logistic`
- sample count: `10`
- ApexLab classification accuracy: `1.0`
- ApexLab pseudo-$R^2$: `0.9493130814508287`
- ApexLab iterations used: `12000`
- ApexLab reported `converged: false` for this capped optimization run

Reference-comparison outcomes captured in the machine-readable artifact:

- probability mean absolute error: approximately `0.0323`
- probability correlation: approximately `0.9912`
- coefficient sign match: `true`
- prediction agreement on the fixture: perfect classification accuracy

Interpretation:

- the logistic implementation matched the expected decision boundary and prediction behavior on the validation fixture
- probability outputs were strongly aligned with the reference model even though optimization style and stopping behavior differ
- the non-converged flag here is informative rather than disqualifying; the run still satisfied the declared acceptance checks

## Acceptance posture

Top-level artifact status: **pass**

All three validation sections passed:

- `statistical_tests`
- `ols`
- `logistic`

This means the current ApexLab Leg 2 implementation cleared the reference-validation thresholds defined by the run.

## Dependency posture

This validation does **not** change ApexLab runtime dependency expectations.

- ApexLab runtime surfaces remain NumPy/stdlib oriented.
- SciPy and scikit-learn were used only as external baselines for validation.
- Validation tooling should remain separate from runtime and operator surfaces.

## Field test status

For terminology consistency, ApexLab should use **field test** as the canonical label for the live/wet/field-test lane.

Yes — a field test was run.

Confirmed field-test evidence for the current Leg 2 surface:

- execution surface: `projects/apexlab/examples/evaluation_demo.py`
- execution date: `2026-03-25`
- execution result: **pass**

Observed field-test evidence from the run:

- report files were written successfully for both direct report generation and CLI rerendering
- `apexlab compare` exited with code `0`
- `apexlab report` exited with code `0`
- compare report JSON artifact existed after the run
- rerendered Markdown artifact existed after the run
- the emitted compare payload included the Frame 6 report structure with `identity`, `context`, `inputs`, `interpretation`, `flags`, and `code`

This field test is complementary to, and distinct from, the heavier external reference-validation run documented above:

- **field test** = end-to-end runtime/demo execution of real package surfaces
- **reference validation** = external-baseline numerical comparison against SciPy / scikit-learn

## Canonical artifact policy

For this validation lane, ApexLab is the canonical source of truth.

Canonical surfaces:

- public-facing summary: `projects/apexlab/docs/validation/REFERENCE_VALIDATION_20260324.md`
- machine-readable run artifact: `projects/apexlab/logs/metrics/reference_validation_20260324.json`
- validation runner: `projects/apexlab/examples/reference_validation_run.py`

Any downstream summaries in consumer repositories should cite this report rather than fork or reinterpret the numeric findings independently.

## Recommended follow-on

Recommended next steps for this lane:

1. keep the validation runner in the ApexLab repository as the canonical reproducibility surface
2. keep it outside operational/runtime script lanes
3. optionally promote it later into a dedicated `examples/validation/` or `validation/` documentation lane if the public validation surface expands
4. add additional fixtures over time for edge-case probability calibration and wider logistic-separation scenarios
