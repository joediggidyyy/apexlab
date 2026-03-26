# ApexLab

ApexLab is a lean standalone Python package for practical machine-learning utilities.

The current public package now spans a lean Leg 1 core plus an expanded Leg 2 analysis/model/reporting lane. ApexLab currently focuses on:

- simplex-constrained regression via `ApexRegressor`
- statistical comparison helpers (`Mann-Whitney U`, `KS two-sample`, `Welch t-test`, `Cohen's d`)
- lightweight OLS and binary logistic regression helpers
- deterministic anomaly detection via `IsolationForest`
- supervised binary classification via `DecisionTreeClassifier` and `RandomForestClassifier`
- deterministic dataset splitting with optional stratification
- regression and classification metrics
- threshold selection and anomaly-style score evaluation
- lightweight JSON/Markdown report emission
- lite CLI support for `apexlab compare` and `apexlab report`

The design goal is simple: ship a small, coherent toolkit first, then broaden it in later legs without dragging in a kitchen sink of dependencies. At the moment, `numpy` is the only non-stdlib runtime dependency.

Current shipped-version target: `1.2.0`.

## What ApexLab is for

ApexLab 1.2.0 is aimed at small, reproducible ML workflows where you want lightweight numerical tooling without depending on a full framework stack. The current release is especially suited to:

- constrained linear modeling experiments
- distribution-comparison and effect-size review
- lightweight explanatory regression analysis
- anomaly-oriented score review with a package-owned isolation forest
- deterministic supervised classification experiments using package-owned tree and forest models
- deterministic train/test split generation
- compact evaluation and reporting flows
- threshold-based score review for anomaly-style or binary decisions

## Current status

The repository is past pure scaffolding and now contains working Leg 1 modules, runnable examples, focused tests, and validated source/wheel build artifacts.

## Install

For development from `projects/apexlab/`:

- `pip install -e .`

For a release artifact install:

- `pip install dist/apexlab-1.2.0-py3-none-any.whl`

The wheel and source distribution for `1.2.0` should be treated as the active release artifact lane.

## Quick start

After installation:

- `python examples/simplex_regression_demo.py`
- `python examples/evaluation_demo.py`

Or, after installing the package entry point:

- `apexlab compare --sample-a 1,2,3 --sample-b 4,5,6 --out-dir out`
- `apexlab report --input out/compare_report.json --out-dir out/rerendered`

The first demo trains a simplex-constrained regressor and prints learned weights plus a convergence summary. The second demo computes metrics, evaluates a thresholded score surface, and writes paired JSON/Markdown report output.

The evaluation demo now also acts as the canonical **field test** surface for the current Leg 1 + Leg 2 lite package lane.

## Quick examples

From `projects/apexlab/`:

- `python examples/simplex_regression_demo.py`
- `python examples/evaluation_demo.py`

Representative demo output includes:

- simplex demo learning weights close to `[0.6, 0.3, 0.1]`
- evaluation demo producing regression metrics, classification accuracy, comparison artifacts, and paired JSON/Markdown report files
- successful `apexlab compare` and `apexlab report` execution during the field test

## Package lanes

- `src/apexlab/models/` — constrained model surfaces
- `src/apexlab/datasets/` — deterministic data split helpers
- `src/apexlab/evaluation/` — metrics, thresholds, and report generation
- `src/apexlab/diagnostics/` — training-history summaries
- `src/apexlab/utils/` — small reusable helpers
- `tests/` — focused behavior tests
- `examples/` — runnable demos using current package APIs

## Dependency posture

ApexLab currently avoids heavyweight ML frameworks. There is no `scikit-learn` runtime dependency in `1.2.0`.

## Release posture

The `1.2.0` lane currently includes:

- passing focused test coverage
- comparison, regression, CLI-lite, and reporting expansion surfaces
- package-owned `IsolationForest`, `DecisionTreeClassifier`, and `RandomForestClassifier` surfaces
- CLI version-flag support via `apexlab --version` and `apexlab -v`
- reference validation against external baselines
- confirmed field-test execution via `examples/evaluation_demo.py`
- a release workflow that can skip already-published files during reruns

## More detail

- `REFERENCE_VALIDATION_REPORT_20260324.md` — public-facing scientific write-up of the 2026-03-24 reference-validation run
- `examples/reference_validation_run.py` — canonical external reference-validation runner for the current Leg 2 analytical lane
- `examples/evaluation_demo.py` — canonical field-test surface for the current package lane
- `tests/` — focused package validation surfaces
- `src/apexlab/` — current public implementation surface
