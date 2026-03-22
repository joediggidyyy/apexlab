# ApexLab

ApexLab is a lean standalone Python package for practical machine-learning utilities.

Leg 1 is intentionally compact. The current package focuses on:

- simplex-constrained regression via `ApexRegressor`
- deterministic dataset splitting with optional stratification
- regression and classification metrics
- threshold selection and anomaly-style score evaluation
- lightweight JSON/Markdown report emission

The design goal is simple: ship a small, coherent toolkit first, then broaden it in later legs without dragging in a kitchen sink of dependencies. At the moment, `numpy` is the only non-stdlib runtime dependency.

Current shipped-version target: `1.0.0`.

## What ApexLab is for

ApexLab 1.0.0 is aimed at small, reproducible ML workflows where you want lightweight numerical tooling without depending on a full framework stack. The initial release is especially suited to:

- constrained linear modeling experiments
- deterministic train/test split generation
- compact evaluation and reporting flows
- threshold-based score review for anomaly-style or binary decisions

## Current status

The repository is past pure scaffolding and now contains working Leg 1 modules, runnable examples, focused tests, and validated source/wheel build artifacts.

## Install

For development from `projects/apexlab/`:

- `pip install -e .`

For a release artifact install:

- `pip install dist/apexlab-1.0.0-py3-none-any.whl`

Both the wheel and source distribution for `1.0.0` have been install-verified locally.

## Quick start

After installation:

- `python examples/simplex_regression_demo.py`
- `python examples/evaluation_demo.py`

The first demo trains a simplex-constrained regressor and prints learned weights plus a convergence summary. The second demo computes metrics, evaluates a thresholded score surface, and writes paired JSON/Markdown report output.

## Quick examples

From `projects/apexlab/`:

- `python examples/simplex_regression_demo.py`
- `python examples/evaluation_demo.py`

Representative demo output includes:

- simplex demo learning weights close to `[0.6, 0.3, 0.1]`
- evaluation demo producing regression metrics, classification accuracy, and paired JSON/Markdown report files

## Package lanes

- `src/apexlab/models/` — constrained model surfaces
- `src/apexlab/datasets/` — deterministic data split helpers
- `src/apexlab/evaluation/` — metrics, thresholds, and report generation
- `src/apexlab/diagnostics/` — training-history summaries
- `src/apexlab/utils/` — small reusable helpers
- `tests/` — focused behavior tests
- `examples/` — runnable demos using current package APIs

## Dependency posture

ApexLab currently avoids heavyweight ML frameworks. There is no `scikit-learn` dependency in Leg 1.

## Release posture

The `1.0.0` lane currently includes:

- passing focused test coverage
- install-verified wheel and source distributions
- a clean active `dist/` containing only `1.0.0` artifacts

## More detail

- `docs/APEXLAB_TOOLKIT_AUTHORITATIVE_SCHEMATIC.md` — authoritative package definitions
- `docs/API_OVERVIEW.md` — current public Leg 1 API overview
- `docs/INITIAL_RELEASE_SCOPE.md` — release-shape summary
- `docs/RELEASE_NOTES_DRAFT.md` — current release notes draft for `1.0.0`
- `docs/PUBLISH_CHECKLIST.md` — compact pre-publish checklist
