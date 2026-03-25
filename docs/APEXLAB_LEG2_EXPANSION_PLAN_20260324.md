# ApexLab Leg 2 — Analysis Expansion, CLI Surface & Reporting

**Owner**: `joediggidyyy`  
**Prepared by**: `ORACL-Prime`  
**Date**: 2026-03-24  
**Status**: active plan  
**Driver**: Calamum grad-course deadline (24hr window) + ApexLab maturity sequencing

---

## Context

Leg 1 shipped: constrained optimization (`ApexRegressor`), evaluation/metrics/thresholds (stdlib-only), deterministic splits, demos, PyPI.

Leg 2 objective: add the statistical analysis layer, expand the model family, and ship a real CLI surface with structured reporting — so ApexLab fully owns the stack currently split across sklearn + custom project code.

Secondary objective: enable the Calamum Observer project to drop sklearn entirely and replace it with ApexLab calls for both training and evaluation.

### What already exists and can be leveraged immediately

Leg 2 is not a cold start. The following Leg 1 surfaces are already implemented and should be treated as stable foundations rather than rebuilt:

- `apexlab.models.simplex.ApexRegressor` — constrained regression with tracked optimization history
- `apexlab.evaluation.metrics.regression_metrics()` — MAE, MSE, RMSE, $R^2$
- `apexlab.evaluation.metrics.classification_metrics()` — confusion matrix, per-label precision/recall/F1, accuracy
- `apexlab.evaluation.thresholds.choose_threshold()` — FPR-constrained threshold search
- `apexlab.evaluation.thresholds.select_lower_tail_threshold()` — deterministic percentile-style threshold selection
- `apexlab.evaluation.thresholds.evaluate_scores()` — labeled and unlabeled threshold evaluation flow
- `apexlab.evaluation.reports.write_reports()` — JSON + Markdown report emission
- `apexlab.datasets.split` — deterministic data splitting helpers
- `apexlab.diagnostics.convergence.summarize_history()` — optimization-history summarization

This matters because Leg 2 should extend these surfaces instead of inventing parallel ones. In practice, the statistical-analysis lane and reporting lane are additive work; only the model lane requires wholly new estimator implementations.

---

## High-Level Work Areas

### Area A — Statistical Analysis Layer (`apexlab/analysis/`)

New subpackage. Core academic deliverable. Highest payoff per hour.

| Module | Contents |
|---|---|
| `analysis/compare.py` | Mann-Whitney U, KS two-sample, Cohen's d, Welch's t-test, lane-to-lane comparison entry point |
| `analysis/regression.py` | OLS linear regression (numpy normal equation), logistic regression (gradient descent), coefficient table output |
| `analysis/__init__.py` | Package root |

#### Area A implementation intent

This area closes the academic gap in the current Calamum workflow. The existing observer pipeline can already score and threshold data, but it does not yet produce the classical inferential outputs a graduate reviewer expects.

Planned public functions:

- `mann_whitney_u(sample_a, sample_b) -> dict`
- `ks_two_sample(sample_a, sample_b) -> dict`
- `cohens_d(sample_a, sample_b) -> dict`
- `welch_t_test(sample_a, sample_b) -> dict`
- `compare_distributions(sample_a, sample_b, *, labels=None) -> dict`
- `ols_fit(x, y, *, add_intercept=True) -> dict`
- `logistic_fit(x, y, *, learning_rate=..., max_iter=..., tol=...) -> dict`
- `summarize_coefficients(...) -> list[dict]`

Expected output shape for comparison functions:

- sample sizes per lane
- central tendency summary (mean, median)
- spread summary (std, IQR if implemented)
- test statistic(s)
- p-value or approximate p-value where mathematically supported in a scipy-free implementation
- effect size
- directionality statement (which lane trends higher/lower)
- interpretation note suitable for direct report inclusion

Expected output shape for regression functions:

- coefficient table with intercept + feature weights
- fit diagnostics (`n`, loss, convergence, pseudo-$R^2$ or $R^2$ where applicable)
- prediction helper surface
- serializable model state for report embedding or later reuse

### Area B — Model Expansion (`apexlab/models/`)

Replaces sklearn's training surfaces entirely.

| Module | Contents |
|---|---|
| `models/isolation_forest.py` | IsolationForest — random feature + random split trees, mean path length anomaly score, `fit()` / `score_samples()` / `predict()` |
| `models/decision_tree.py` | CART decision tree — Gini impurity, recursive partitioning, leaf probability storage |
| `models/random_forest.py` | Random forest ensemble — bagging, feature subsampling, `predict_proba()`, `predict()` |

#### Area B implementation intent

This is the most technically expensive area and the least urgent from a course-delivery standpoint, but it is the decisive step if the goal is a true sklearn-free ApexLab.

Minimum estimator parity targets:

- sklearn-like constructor arguments where practical (`random_state`, `n_estimators`, `max_depth`, `max_features`)
- `fit()` returns `self`
- `predict()` available on all estimators
- `predict_proba()` available on classifiers
- `score_samples()` / `decision_function()` style anomaly scoring for isolation forest
- pickle-safe internal state without `joblib`

Non-goals for the first Leg 2 pass:

- exhaustive sklearn API parity
- pruning, feature importance variants, OOB scoring, class weights, sparse matrix support
- highly optimized vectorized trees

Target outcome is functional parity for the specific Calamum pipeline, not immediate framework-scale parity with sklearn.

### Area C — CLI Surface (`apexlab/cli/`)

New subpackage. Registered as `apexlab` entry point in `pyproject.toml`.

| Module | Subcommand | Function |
|---|---|---|
| `cli/main.py` | `apexlab` | Top-level dispatch |
| `cli/train.py` | `apexlab train` | Train RF or IsolationForest from CSV dataset |
| `cli/evaluate.py` | `apexlab evaluate` | Run evaluation harness, emit JSON + MD report |
| `cli/compare.py` | `apexlab compare` | Run lane-to-lane statistical comparison |
| `cli/report.py` | `apexlab report` | Render structured report from prior run artifacts |

#### Area C implementation intent

The CLI is required because course evaluation and cross-project reuse both improve dramatically when the toolkit can be exercised without dropping into Python imports.

Command posture:

- all commands must support `-h`
- all commands must emit ASCII-safe stdout
- all commands must support deterministic file outputs
- error messages must identify bad input files, shape mismatches, or unsupported model names explicitly

Planned command shapes:

- `apexlab train --dataset <manifest.json> --out-dir <dir> --model <random-forest|isolation-forest|simplex>`
- `apexlab evaluate --features <features.csv> --labels <labels.csv> --out-dir <dir> [--model-path <file>] [--max-fpr <float>]`
- `apexlab compare --lane-a <file> --lane-b <file> --metric <column> --out-dir <dir>`
- `apexlab report --input <report.json> --out-dir <dir> [--format md|json|both]`

The exact flags may evolve, but the surface should be thin, unsurprising, and directly scriptable.

### Area D — Reporting Expansion (`apexlab/evaluation/`)

Extend existing `reports.py` and add comparison reporting.

| Item | Contents |
|---|---|
| `evaluation/reports.py` (expand) | Add comparison section, per-lane stats table, threshold summary block |
| `evaluation/compare_report.py` (new) | Comparison report: stat test results table, effect sizes, recommend/warn logic |

#### Area D implementation intent

Leg 1 reporting already proves the report-writing pattern. Leg 2 should standardize a richer artifact family rather than scatter ad hoc JSON blobs across downstream projects.

Required report sections:

- run identity (timestamp, operator, version)
- input provenance (dataset paths, hashes when available)
- model metadata (family, hyperparameters, feature set)
- evaluation metrics
- threshold summary
- statistical comparison section when applicable
- plain-language interpretation block
- machine-readable recommendation/warning flags

### Area E — Package Housekeeping

| Item | Action |
|---|---|
| `__init__.py` | Expose new public API (`analysis`, `models`, `cli`) |
| `pyproject.toml` | Add `apexlab` CLI entry point, bump version to `1.1.0` |
| `tests/` | New test files for all new modules |
| `docs/APEXLAB_TOOLKIT_AUTHORITATIVE_SCHEMATIC.md` | Update UNSPECIFIED surfaces to DEFINED |

#### Area E implementation intent

This area keeps Leg 2 from becoming a pile of useful but undocumented capabilities. The package surface, versioning surface, and authoritative schematic must move in lockstep with the code.

---

## Proposed package surface after Leg 2

```text
src/apexlab/
	analysis/
		__init__.py
		compare.py
		regression.py
	cli/
		__init__.py
		main.py
		train.py
		evaluate.py
		compare.py
		report.py
	diagnostics/
		convergence.py
	datasets/
		split.py
	evaluation/
		__init__.py
		compare_report.py
		metrics.py
		reports.py
		thresholds.py
	models/
		__init__.py
		decision_tree.py
		isolation_forest.py
		random_forest.py
		simplex.py
```

The net-new package roots are `analysis/` and `cli/`. The net-new evaluator artifact is `compare_report.py`. The rest are expansions of already-shipped lanes.

---

## Artifact contract for Leg 2 outputs

The reporting surface should converge on a small family of predictable artifacts:

| Artifact | Purpose |
|---|---|
| `report.json` | canonical machine-readable evaluation or comparison output |
| `report.md` | human-readable narrative summary |
| `model.pkl` | serialized ApexLab model state |
| `train_manifest.json` | training metadata, params, feature columns, provenance |
| `compare_manifest.json` | lane comparison metadata, selected metric, test suite executed |

Minimum `report.json` sections:

- `identity`
- `context`
- `inputs`
- `model` (if applicable)
- `evaluation`
- `comparison` (if applicable)
- `interpretation`
- `code`

This mirrors the stronger parts of the existing Calamum `run.json` pattern while generalizing it into reusable ApexLab package behavior.

---

## Frame Breakdown

| Frame | Area | Deliverable | Est. complexity |
|---|---|---|---|
| **F1** | A | `analysis/compare.py` + tests | Medium (~200 lines) |
| **F2** | A | `analysis/regression.py` + tests | Medium (~250 lines) |
| **F3** | B | `models/isolation_forest.py` + tests | Hard (~400 lines) |
| **F4** | B | `models/decision_tree.py` + `models/random_forest.py` + tests | Hard (~900 lines total) |
| **F5** | C | `cli/` subpackage (all 5 modules) + entry point wiring | Medium (~400 lines) |
| **F6** | D | `evaluation/compare_report.py` + `reports.py` expansion | Medium (~200 lines) |
| **F7** | E | Calamum integration — drop sklearn, wire to ApexLab | Medium (callsite swaps) |
| **F8** | E | Package finalization — `__init__.py`, `pyproject.toml`, full test run, version bump | Light |

### Frame-by-frame definition of done

#### F1 — `analysis/compare.py`

Done when:

- two-sample comparison helpers exist and are importable
- unit tests cover identical samples, separated samples, and uneven sample counts
- result objects are stable dicts/dataclasses rather than ad hoc tuples
- at least one end-to-end comparison example can be embedded directly into a report

#### F2 — `analysis/regression.py`

Done when:

- OLS fit returns coefficients and predictions correctly for a simple synthetic dataset
- logistic fit converges on a linearly separable toy problem
- coefficient summaries are report-ready
- convergence state is exposed for diagnostics

#### F3 — `models/isolation_forest.py`

Done when:

- model fits on a toy dataset without sklearn
- anomaly scores rank obvious outliers higher than inliers
- model state serializes and deserializes cleanly
- test suite verifies deterministic behavior under fixed seed

#### F4 — `models/decision_tree.py` + `models/random_forest.py`

Done when:

- decision tree can separate a simple binary dataset
- random forest aggregates tree predictions into stable probabilities
- training and inference are deterministic with fixed seed
- the API is sufficient to replace Calamum supervised training code

#### F5 — CLI

Done when:

- `apexlab -h` and subcommand help pages render cleanly
- a training command can create model + manifest artifacts
- an evaluation command can create JSON + Markdown output
- a compare command can create statistical-comparison output from two input lanes

#### F6 — reporting expansion

Done when:

- comparison results render into both JSON and Markdown
- reports include machine-readable flags plus plain-language interpretation
- report schema is stable enough for downstream parsing

#### F7 — Calamum integration

Done when:

- Calamum analysis code imports ApexLab instead of sklearn for all supported paths
- legacy custom threshold logic is removed or delegated to ApexLab
- at least one smoke run produces equivalent artifact structure

#### F8 — finalization

Done when:

- public exports are coherent
- version + entry points are updated
- full test suite passes
- package builds and imports from wheel/sdist successfully

---

## 24hr Priority Order

Given the course deadline, the academic-value ordering is:

1. **F1 — Statistical comparison** (Mann-Whitney, KS, Cohen's d) — this is the gap evaluators notice
2. **F2 — Regression analysis** (OLS + logistic) — core ML course surface
3. **F5 — CLI** (makes the whole thing runnable by the TA/evaluator without code inspection)
4. **F6 — Reporting** (structured output, presentable tables)
5. **F3 — IsolationForest** (sklearn drop for unsupervised)
6. **F4 — RF + decision tree** (sklearn drop for supervised — hardest, do last)
7. **F7 — Calamum integration** (depends on F3/F4 being stable)
8. **F8 — Finalization** (gate before any push)

### Compression strategy if the 24hr window gets tight

If the deadline pressure wins a cage match with engineering ambition, the fallback order is:

1. finish F1
2. finish F2
3. finish the CLI only for `compare` + `report`
4. finish F6
5. defer F3/F4 behind a documented Phase 2 note

That compressed path still yields a course-credible package story: ApexLab owns the analytical rigor, report generation, and reproducible CLI surface even if the tree models remain temporarily external.

---

## Dependencies and sequencing constraints

| Frame | Depends on | Why |
|---|---|---|
| F1 | none | foundational stats lane |
| F2 | none | foundational regression lane |
| F3 | none | standalone model lane |
| F4 | none, but benefits from F3 patterns | shared estimator conventions |
| F5 | F1/F2/F3/F4 partially | CLI should wrap real surfaces, not placeholders |
| F6 | F1/F2 | report structure depends on analysis outputs |
| F7 | F3/F4/F5/F6 | integration should happen only after stable APIs exist |
| F8 | all prior frames | finalization gate |

Practical sequence for implementation remains: F1 -> F2 -> F5 -> F6 -> F3 -> F4 -> F7 -> F8.

---

## Main technical risks

| Risk | Why it matters | Mitigation |
|---|---|---|
| scipy-free p-value accuracy | inferential credibility can get wobbly if approximations are sloppy | clearly document approximation method; test against known reference values |
| logistic regression convergence | gradient descent can oscillate on poorly scaled features | add normalization guidance and convergence diagnostics |
| isolation forest score semantics | anomaly score direction can easily be inverted | write explicit toy tests with known outliers |
| decision-tree bug surface | tree implementations fail in lots of boring but deadly corner cases | start with small deterministic fixtures, then broaden |
| CLI schema drift | downstream projects may script against unstable outputs | define `report.json` sections before wiring commands |
| overbuilding in 24hr window | heroic scope can vaporize delivery | prefer analytical/reporting completeness over full estimator parity |

---

## Validation strategy

Validation should happen at three layers:

1. **Unit** — pure function correctness for tests, metrics, split logic, regression math
2. **Component** — estimator fit/predict behavior and report generation behavior
3. **Workflow** — CLI-driven train/evaluate/compare runs against tiny fixture datasets

Target new tests:

- `tests/test_compare.py`
- `tests/test_regression.py`
- `tests/test_isolation_forest.py`
- `tests/test_decision_tree.py`
- `tests/test_random_forest.py`
- `tests/test_cli.py`
- `tests/test_compare_report.py`

The first acceptance gate for the 24hr window is not "all models are perfect." It is "the analysis/reporting/CLI story is coherent, tested, and demoable."

---

## Exit Criteria (Leg 2)

- [ ] `apexlab compare` runs against two Calamum lanes and emits a stat-test report
- [ ] `apexlab train` trains RF or IsolationForest from a dataset manifest
- [ ] `apexlab evaluate` emits a full JSON + MD report with threshold summary
- [ ] `apexlab report` renders a comparison report with stat test table
- [ ] Calamum `train_model.py` has zero sklearn imports
- [ ] All existing Leg 1 tests still pass
- [ ] All new modules have test coverage
- [ ] `apexlab==1.1.0` installs cleanly from the built dist

### Preferred demo narrative at completion

At completion, `joediggidyyy` should be able to demonstrate the following simple storyline:

1. train or load an ApexLab model
2. evaluate a lane and produce thresholded metrics
3. compare two lanes statistically
4. emit a clean Markdown + JSON report bundle
5. point to ApexLab as the package that now owns the core data-science/reporting surface

---

## Notes

- Keep all new `analysis/` and `evaluation/` code numpy-only or stdlib-only (no scipy)
- All stat tests must document the null hypothesis and interpretation clearly in docstrings
- CLI outputs must be ASCII-safe (no unicode symbols in table borders)
- Model serialization: use `pickle` or `numpy.savez` — no joblib dependency
- Each frame should be committed independently before moving to the next

---

## Frame 1 micro-plan — `analysis/compare.py`

### Operating reminders for every micro-frame

Before and during implementation, ORACL-Prime should periodically realign with both ApexLab project intent and broader CodeSentinel operating expectations.

Required reminders for this frame and all later micro-frames:

- pause at natural checkpoints to confirm the frame still matches the active 24-hour tranche rather than silently expanding into a broader leg
- re-check the ApexLab authoritative surfaces before making public-API decisions
- re-check relevant CodeSentinel operating expectations when work touches packaging, reporting, CLI surfaces, or cross-project integration assumptions
- review source docs and adjacent system surfaces before locking interfaces that downstream projects may consume
- when a frame uses design guidance from docs or neighboring systems, include a concise reference list of materials reviewed in the frame summary or handoff notes

Minimum review expectation for implementation-facing frames:

- core ApexLab schematic / package docs
- adjacent Calamum consumer surfaces if the frame is intended for immediate integration
- any existing report or artifact schema the new code is expected to align with

This reminder is deliberately repetitive: it is meant to prevent local optimization from drifting away from repository policy, adjacent consumers, or the actual delivery window.

### Frame purpose

Frame 1 delivers the first academically credible analysis surface for ApexLab: reproducible, scipy-free, two-sample comparison utilities that can be used directly by Calamum and later wrapped by `apexlab compare`.

This frame is intentionally analysis-first. It does **not** attempt to build the full CLI, the full reporting layer, or any tree-based estimators. Its job is to create the statistical backbone those later surfaces will consume.

### Why Frame 1 comes first

The current gap in the observer workflow is not basic scoring or thresholding; those already exist. The missing layer is inferential comparison:

- are two lanes measurably different?
- how large is the difference?
- in which direction does the effect run?
- can ORACL-Prime emit a result that is immediately reportable and course-defensible?

That is why F1 has the highest value per hour in the 24-hour window.

### In-scope deliverables

Files to create:

- `src/apexlab/analysis/__init__.py`
- `src/apexlab/analysis/compare.py`
- `tests/test_compare.py`

Code surfaces to implement in `compare.py`:

- `summary_stats(values)`
- `rank_values(values)` or equivalent internal helper
- `mann_whitney_u(sample_a, sample_b)`
- `ks_two_sample(sample_a, sample_b)`
- `cohens_d(sample_a, sample_b)`
- `welch_t_test(sample_a, sample_b)`
- `compare_distributions(sample_a, sample_b, *, label_a="lane_a", label_b="lane_b")`

Public export goal for `analysis/__init__.py`:

- re-export `compare_distributions`
- re-export the individual stat helpers that are intended to be stable public surface

### Out of scope for F1

The following are explicitly deferred to later frames:

- regression fitting (`analysis/regression.py`)
- CLI command wiring (`apexlab compare`)
- markdown/json comparison report renderers
- multi-column dataset ingestion
- batch comparison across many metrics
- model training or threshold selection changes
- exact scipy numerical parity across all tail cases

F1 should stay narrow and strong.

### Data contract for F1 inputs

All public functions in F1 should accept simple numeric sequences:

- `list[float]`
- `list[int]`
- values coercible to float where reasonable

Validation rules:

- reject empty paired comparison if a test mathematically requires non-empty samples
- reject non-numeric values with clear `ValueError`
- permit unequal sample lengths for two-sample tests
- preserve deterministic ordering in outputs and summaries

### Proposed result shapes

#### Summary statistics result

`summary_stats(values)` should return a stable dict with at least:

- `n`
- `mean`
- `median`
- `min`
- `max`
- `variance`
- `std`

Optional if cheap to implement cleanly:

- `q1`
- `q3`
- `iqr`

#### Individual test result shape

Each individual test helper should return a dict with a predictable structure such as:

- `test`
- `statistic`
- `p_value`
- `interpretation`
- `notes`

Where relevant, also include:

- `u_statistic`
- `d_statistic`
- `degrees_of_freedom`
- `n_a`
- `n_b`

#### Aggregate comparison result shape

`compare_distributions(...)` should return a top-level dict with these sections:

- `labels`
- `samples`
- `summary`
- `tests`
- `effect_size`
- `direction`
- `interpretation`

Recommended concrete shape:

- `labels`: `{ "a": ..., "b": ... }`
- `samples`: `{ "n_a": ..., "n_b": ... }`
- `summary`: `{ "a": {...}, "b": {...} }`
- `tests`: `{ "mann_whitney_u": {...}, "ks_two_sample": {...}, "welch_t_test": {...} }`
- `effect_size`: `{ "cohens_d": {...} }`
- `direction`: short statement such as `"lane_b_mean_gt_lane_a_mean"`
- `interpretation`: plain-language summary sentence block

This shape is intentionally report-friendly so F6 can consume it without schema churn.

### Statistical implementation targets

#### Mann-Whitney U

Implementation target:

- combine samples
- assign ranks with tie handling by average rank
- compute $U_1$ and $U_2$
- report the smaller or primary U consistently
- include approximate p-value if feasible without scipy

Expectation:

- exact small-sample table lookup is **not** required in F1
- normal approximation is acceptable if documented clearly

#### KS two-sample

Implementation target:

- sort both samples
- compute empirical CDF step difference
- report maximum absolute difference $D$
- provide approximate p-value if using asymptotic form

Expectation:

- deterministic, transparent implementation matters more than perfect asymptotic nuance

#### Cohen's d

Implementation target:

- pooled standard deviation
- signed effect size
- interpretation bucket (`negligible`, `small`, `medium`, `large`)

#### Welch's t-test

Implementation target:

- compute unequal-variance t statistic
- approximate degrees of freedom via Welch-Satterthwaite
- approximate p-value if feasible

Expectation:

- if p-value approximation is too brittle for day-one reliability, retain statistic + df + note that p-value is approximate

### Interpretation rules

Each comparison result should contain an interpretation block that ORACL-Prime can drop into a report with minimal rewriting.

Interpretation requirements:

- identify which sample trends higher on mean or median
- mention whether distributional separation appears weak/moderate/strong
- mention effect size bucket
- explicitly note when sample sizes are tiny and interpretation should be cautious

Example style target:

> Lane B shows a higher central tendency than Lane A, with a medium positive effect size and measurable distributional separation; because sample counts are small, inferential confidence should be treated cautiously.

### Test matrix for `tests/test_compare.py`

Minimum cases:

1. **summary statistics sanity**
	- simple numeric list
	- verify `n`, `mean`, `median`, `min`, `max`

2. **identical sample comparison**
	- same values in both lanes
	- expect near-zero or null-looking separation measures

3. **clearly separated sample comparison**
	- one low cluster, one high cluster
	- expect strong direction and non-zero effect size

4. **uneven sample sizes**
	- ensure functions work with different `n`

5. **ties present**
	- exercise rank handling in Mann-Whitney

6. **single-value failure or edge behavior**
	- verify explicit, documented response

7. **non-numeric input rejection**
	- verify `ValueError` with useful message

8. **aggregate result schema stability**
	- assert top-level keys exist exactly as planned

### Implementation order inside the frame

Step 1:

- create `analysis/__init__.py`
- set package exports

Step 2:

- implement numeric coercion + validation helpers
- implement `summary_stats()`

Step 3:

- implement rank helper with tie handling
- implement `mann_whitney_u()`

Step 4:

- implement `ks_two_sample()`
- implement `cohens_d()`
- implement `welch_t_test()`

Step 5:

- implement `compare_distributions()` aggregator
- add plain-language interpretation logic

Step 6:

- write tests for all above cases
- run targeted ApexLab tests

### Validation commands for the frame

Primary validation target:

- run the ApexLab test file for F1 only first

Secondary validation target:

- run the full current ApexLab test suite to ensure F1 does not break Leg 1 surfaces

### Periodic realignment checkpoints during execution

Checkpoint 1 — before writing code:

- re-open the F1 scope and confirm no CLI/report/model work is accidentally entering the frame
- note the source docs and adjacent code surfaces reviewed

Checkpoint 2 — after core stat helpers compile:

- verify result schema still matches the planned report-friendly contract
- verify naming is consistent with existing ApexLab public surfaces

Checkpoint 3 — after tests pass:

- confirm no new dependency drift
- confirm the implementation is still appropriate for both ApexLab packaging and near-term Calamum consumption
- capture a concise reference list of docs/code surfaces reviewed during the frame

### Frame 1 exit criteria

F1 is complete when all of the following are true:

- `apexlab.analysis.compare` imports cleanly
- `compare_distributions()` returns a stable, report-ready dict
- targeted F1 tests pass
- existing ApexLab tests still pass
- no scipy dependency has been introduced
- the result schema is good enough that F5/F6 can wrap it without redesign

### Frame 1 handoff to next frame

If F1 exits cleanly, Frame 2 should immediately consume its structural decisions:

- match result-shape discipline in `analysis/regression.py`
- preserve the same interpretation style
- keep outputs naturally serializable for the later reporting and CLI lanes

In short: F1 defines the statistical grammar for the rest of Leg 2.

---

## Frame 2 micro-plan — `analysis/regression.py`

### Operating reminders for every micro-frame

Before and during implementation, ORACL-Prime should periodically realign with both ApexLab project intent and broader CodeSentinel operating expectations.

Required reminders for this frame and all later micro-frames:

- pause at natural checkpoints to confirm the frame still matches the active 24-hour tranche rather than silently expanding into a broader leg
- re-check the ApexLab authoritative surfaces before making public-API decisions
- re-check relevant CodeSentinel operating expectations when work touches packaging, reporting, CLI surfaces, or cross-project integration assumptions
- review source docs and adjacent system surfaces before locking interfaces that downstream projects may consume
- when a frame uses design guidance from docs or neighboring systems, include a concise reference list of materials reviewed in the frame summary or handoff notes

Minimum review expectation for implementation-facing frames:

- core ApexLab schematic / package docs
- adjacent Calamum consumer surfaces if the frame is intended for immediate integration
- any existing report or artifact schema the new code is expected to align with

This reminder is deliberately repetitive: it is meant to prevent local optimization from drifting away from repository policy, adjacent consumers, or the actual delivery window.

### Frame purpose

Frame 2 delivers the first regression-analysis surface for ApexLab: a lightweight, numpy-based modeling and coefficient-summary layer that can support course-facing explanatory analysis without requiring sklearn or scipy.

This frame is meant to answer the next academic question after F1's distributional comparisons:

- which features are associated with the outcome?
- in what direction do they push predictions?
- can the model emit coefficients and convergence details that are interpretable in a course setting?

This frame is still analysis-first. It does **not** build the CLI, report renderers, dataset-ingestion framework, or tree models.

### Why Frame 2 comes immediately after Frame 1

F1 answers whether two lanes differ. F2 answers what explanatory model can be fit to structured feature data and how to narrate that model.

Together, F1 and F2 create the course-credible analytics core:

- F1 = inferential comparison
- F2 = interpretable regression surface

The CLI/reporting lanes are wrappers around these analytical primitives, so F2 should lock its result shapes before those wrapper frames begin.

### In-scope deliverables

Files to create:

- `src/apexlab/analysis/regression.py`
- `tests/test_regression.py`

Files to update:

- `src/apexlab/analysis/__init__.py`

Code surfaces to implement in `regression.py`:

- `prepare_design_matrix(x, *, add_intercept=True)`
- `ols_fit(x, y, *, add_intercept=True)`
- `ols_predict(x, coefficients, *, add_intercept=True)`
- `sigmoid(values)`
- `logistic_fit(x, y, *, learning_rate=..., max_iter=..., tol=..., add_intercept=True)`
- `logistic_predict_proba(x, coefficients, *, add_intercept=True)`
- `logistic_predict(x, coefficients, *, threshold=0.5, add_intercept=True)`
- `summarize_coefficients(coefficients, *, feature_names=None, intercept_label="intercept")`

Optional helper surfaces if they simplify the implementation cleanly:

- `binary_cross_entropy(...)`
- `r_squared(...)`
- `pseudo_r_squared(...)`

Public export goal for `analysis/__init__.py`:

- re-export `ols_fit`
- re-export `logistic_fit`
- re-export `summarize_coefficients`
- optionally re-export predict helpers if they are intended as stable public surface

### Out of scope for F2

The following are explicitly deferred to later frames:

- ridge / lasso / elastic-net variants
- multiclass logistic regression
- regularization tuning
- feature scaling pipelines
- p-value tables for coefficients
- full statistical inference for parameter confidence intervals
- CLI wiring (`apexlab train`, `apexlab evaluate`)
- persistence / manifest writing for regression models
- dataframe-specific ergonomics

F2 should remain focused on interpretable baseline regression capabilities.

### Data contract for F2 inputs

Accepted input shapes:

- `x` as a 2D numeric matrix-like structure
- `y` as a 1D numeric sequence for OLS
- `y` as a binary sequence (`0/1`) for logistic regression

Validation rules:

- reject empty datasets
- reject row-count mismatch between `x` and `y`
- reject ragged feature rows
- reject non-binary `y` for logistic regression
- support deterministic intercept handling via `add_intercept`

Expected internal representation:

- use `numpy.ndarray`
- coerce to `float`
- keep outputs serializable by converting final public-return values to plain Python lists/floats where practical

### Proposed result shapes

#### OLS fit result

`ols_fit(...)` should return a stable dict with at least:

- `model_type`
- `coefficients`
- `predictions`
- `metrics`
- `converged`
- `notes`

Recommended `metrics` contents:

- `n`
- `mse`
- `rmse`
- `mae`
- `r2`

#### Logistic fit result

`logistic_fit(...)` should return a stable dict with at least:

- `model_type`
- `coefficients`
- `probabilities`
- `predictions`
- `metrics`
- `converged`
- `iterations`
- `history`
- `notes`

Recommended `metrics` contents:

- `n`
- `log_loss`
- `accuracy`
- `positive_rate`
- `pseudo_r2` if implemented cleanly

#### Coefficient summary result

`summarize_coefficients(...)` should return a list of dicts with stable keys such as:

- `feature`
- `coefficient`
- `sign`
- `magnitude`
- `interpretation`

Interpretation examples:

- `positive association with outcome`
- `negative association with outcome`
- `near-zero contribution in current fit`

This summary should be naturally consumable by later report-rendering code.

### Modeling implementation targets

#### OLS

Implementation target:

- build design matrix
- optionally prepend intercept column
- fit coefficients using numpy linear algebra
- prefer pseudoinverse or least-squares routine over brittle hand-rolled inversion
- emit predictions on the training matrix for the frame's baseline surface

Expectation:

- robustness and readability matter more than fancy inference output
- singular matrices should be handled gracefully via least-squares / pseudoinverse approach

#### Logistic regression

Implementation target:

- binary logistic regression only
- gradient descent optimization
- sigmoid activation
- binary cross-entropy loss tracking
- deterministic initialization
- convergence based on parameter delta or loss delta

Expectation:

- this is a practical explanatory model, not a production-optimized solver
- feature scaling is not required in the frame, but warnings/notes are acceptable if convergence is sensitive

### Interpretation rules

Each regression fit should contain enough narrative scaffolding that ORACL-Prime can summarize the fit without reverse-engineering raw arrays.

Interpretation requirements:

- identify the strongest positive coefficient
- identify the strongest negative coefficient when present
- note whether the fit appears stable/converged
- clearly separate descriptive interpretation from causal claims

Example style target:

> The fitted logistic model converged and assigns the strongest positive weight to feature X, suggesting higher values of X are associated with a higher predicted probability of the positive class in this dataset; this is an associative, not causal, interpretation.

### Test matrix for `tests/test_regression.py`

Minimum cases:

1. **design-matrix sanity**
	- verify intercept handling and expected output shape

2. **OLS on simple linear data**
	- fit a near-perfect linear relationship
	- verify coefficient count and strong $R^2$

3. **OLS predict helper**
	- verify predictions align with fitted coefficients

4. **logistic regression on separable toy data**
	- verify convergence or near-convergence
	- verify useful classification accuracy

5. **binary validation**
	- reject non-binary logistic labels

6. **ragged / invalid input rejection**
	- reject inconsistent row lengths or row/label mismatch

7. **coefficient summary stability**
	- assert stable list-of-dicts structure and interpretation strings

8. **history / convergence reporting**
	- verify logistic fit exposes optimization history and iteration count

### Implementation order inside the frame

Step 1:

- create `regression.py`
- implement matrix coercion and validation helpers
- implement `prepare_design_matrix()`

Step 2:

- implement `ols_fit()`
- implement `ols_predict()`
- compute regression metrics using existing ApexLab metric helpers where practical

Step 3:

- implement `sigmoid()`
- implement binary cross-entropy helper if needed
- implement `logistic_fit()` with deterministic gradient descent

Step 4:

- implement `logistic_predict_proba()` and `logistic_predict()`
- implement `summarize_coefficients()`

Step 5:

- export the chosen public surfaces from `analysis/__init__.py`
- write `tests/test_regression.py`

Step 6:

- run targeted regression tests
- run the full ApexLab suite to ensure no regressions to F1 or Leg 1 surfaces

### Validation commands for the frame

Primary validation target:

- run the ApexLab regression test file for F2 only first

Secondary validation target:

- run the full ApexLab test suite to ensure F2 does not break earlier analysis/evaluation lanes

### Periodic realignment checkpoints during execution

Checkpoint 1 — before writing code:

- re-open the F2 scope and confirm no CLI/report/model-family work is entering the frame
- note the source docs and adjacent code surfaces reviewed

Checkpoint 2 — after OLS is working:

- verify result shape discipline matches F1's stable, report-friendly style
- verify coefficient summaries are naturally serializable and human-readable

Checkpoint 3 — after logistic helpers compile:

- confirm optimization history and convergence reporting are present
- verify naming and return structure align with existing ApexLab patterns

Checkpoint 4 — after tests pass:

- confirm no dependency drift
- confirm the surface is appropriate for later CLI/report wrapping
- capture a concise reference list of docs/code surfaces reviewed during the frame

### Frame 2 exit criteria

F2 is complete when all of the following are true:

- `apexlab.analysis.regression` imports cleanly
- OLS fit works on a simple synthetic dataset and emits metrics
- logistic fit works on a simple binary dataset and emits convergence/history details
- coefficient summaries are stable and report-ready
- targeted F2 tests pass
- existing ApexLab tests still pass
- no scipy or sklearn dependency has been introduced
- the result schema is good enough that F5/F6 can wrap it without redesign

### Frame 2 handoff to next frame

If F2 exits cleanly, later frames should consume its structural decisions directly:

- F5 can wrap regression surfaces into CLI commands without inventing new schemas
- F6 can render coefficient summaries and fit diagnostics directly into reports
- future model/training lanes can borrow the same convergence-reporting and result-shape discipline

In short: F2 defines the regression grammar for the rest of Leg 2.

---

## Next-frame micro-report — F5-lite CLI surface

### Frame identity

- frame lane: `F5-lite`
- frame class: CLI wrapper / operator surface
- primary objective: expose the completed F1/F2 analysis primitives behind a clean command surface
- immediate driver: make ApexLab runnable and demonstrable without requiring direct Python imports

### Why this is the next frame

ORACL-Prime has already completed the analytical core needed for the 24-hour tranche:

- F1: two-sample comparison helpers
- F2: interpretable regression helpers

The highest-value next move is to give those surfaces an operator-facing entry point. That makes the work easier to demo, easier to script, and easier to hand to a course evaluator or downstream consumer.

This is why the next frame is not tree-model work yet. The package already has useful math; now it needs a steering wheel.

### Frame scope

The next frame should stay intentionally narrow.

Primary in-scope work:

- create the `apexlab` CLI entry point skeleton
- implement top-level dispatch and `-h` support
- implement `apexlab compare`
- implement `apexlab report` if it is needed to make `compare` output immediately usable
- wire those commands only to already-implemented F1/F2 surfaces

Likely touched files:

- `src/apexlab/cli/__init__.py`
- `src/apexlab/cli/main.py`
- `src/apexlab/cli/compare.py`
- `src/apexlab/cli/report.py` (if included in the lite slice)
- `pyproject.toml`
- `tests/test_cli.py`

### Explicitly out of scope for this next frame

- `apexlab train`
- `apexlab evaluate` full workflow
- report-schema expansion beyond what is needed to support the lite CLI surface
- tree-model implementation
- Calamum code swapping
- package version bump and full release-finalization paperwork

This frame should wrap existing analysis, not introduce a second analytics project by accident.

### Readiness assessment

Current readiness is strong.

What is already available for CLI wrapping:

- `apexlab.analysis.compare_distributions()`
- `apexlab.analysis.ols_fit()`
- `apexlab.analysis.logistic_fit()`
- `apexlab.evaluation.write_reports()`
- existing ApexLab tests and package structure

What is not yet available and may need light glue code:

- CSV/JSON ingestion for compare/regression command inputs
- CLI argument parsing and validation
- command-to-artifact translation layer

### Expected operator outcome

At the end of the next frame, `joediggidyyy` should be able to do something like the following in concept:

1. invoke `apexlab compare` against two numeric inputs or two lane-derived metric surfaces
2. receive a stable JSON result and readable summary output
3. optionally emit a Markdown/JSON report bundle
4. demonstrate ApexLab as a usable command-line toolkit rather than a library-only package

### Main risks for the next frame

| Risk | Why it matters | Mitigation |
|---|---|---|
| CLI scope creep | the command surface can balloon into full workflow orchestration | keep to compare/report only in the lite tranche |
| input-shape ambiguity | command UX gets messy if supported input types are unclear | define one or two supported input forms only |
| report coupling too early | trying to solve all report design concerns here will stall the CLI | support only the minimal artifact shape already enabled by F1/F2 |
| pyproject entry-point drift | command works locally but packaging lags behind | wire the console script during this frame, not later |

### Required realignment reminders for the next frame

Before and during the next frame, ORACL-Prime should periodically realign with ApexLab and CodeSentinel operating expectations.

Required reminders:

- confirm the frame is still the 24-hour CLI tranche rather than a full packaging or workflow lane
- re-check authoritative ApexLab docs before exposing new public command names
- review adjacent consumer expectations so the command shape is actually useful to Calamum and future report lanes
- capture a concise reference list of docs and code surfaces reviewed when the frame closes

### Source docs and adjacent systems to review before execution

Minimum expected review list for the next frame:

- `projects/apexlab/docs/APEXLAB_LEG2_EXPANSION_PLAN_20260324.md`
- `projects/apexlab/docs/APEXLAB_TOOLKIT_AUTHORITATIVE_SCHEMATIC.md`
- `projects/apexlab/src/apexlab/analysis/__init__.py`
- `projects/apexlab/src/apexlab/analysis/compare.py`
- `projects/apexlab/src/apexlab/analysis/regression.py`
- `projects/apexlab/src/apexlab/evaluation/reports.py`
- `projects/apexlab/pyproject.toml`
- adjacent Calamum analysis/report surfaces that the CLI will likely serve soon

### Frame-opening checklist

Before writing code for the next frame:

- confirm the exact supported command set for the lite slice
- confirm the expected input form(s) for `compare`
- confirm whether `report` is in-scope for the same pass or should be split
- confirm artifact-writing behavior and where output files should land

### Preferred exit state

The next frame should end with:

- a working `apexlab` console entry point
- at least one useful subcommand built on F1/F2 surfaces
- targeted CLI tests passing
- full ApexLab suite still passing
- a concise reference list of docs/code surfaces reviewed during the frame

### ORACL-Prime recommendation

Proceed with the next frame as **F5-lite: `compare` first, `report` second if needed**.

That keeps the 24-hour tranche aligned with the current strategy:

- analytical core first
- usable command surface second
- richer reporting and broader model replacement later

---

## Frame 6 completion note — reporting expansion

**Completion status:** complete  
**Completion date:** 2026-03-25

Frame 6 has now been executed.

Delivered surfaces:

- `src/apexlab/evaluation/compare_report.py`
- expanded `src/apexlab/evaluation/reports.py`
- compare CLI updated to emit the richer Frame 6 comparison report shape
- `tests/test_compare_report.py`

Implemented outcomes:

- comparison reports now carry stable top-level report structure
- machine-readable comparison flags are now emitted
- Markdown reporting now includes summary-statistics and statistical-test tables
- regression rendering can now include coefficient summaries and fit diagnostics when present

Validation evidence recorded for this frame:

- targeted ApexLab test slice passed: `24 passed`
- full ApexLab suite passed: `41 passed`
- a confirmed **field test** was run via `examples/evaluation_demo.py`

Terminology note:

- use **field test** as the canonical term for the live/wet/field-test lane in ApexLab docs and status reporting

Field-test evidence summary:

- `apexlab compare` completed successfully during the field test
- `apexlab report` completed successfully during the field test
- comparison JSON + Markdown artifacts were written successfully
- rerendered report artifacts were written successfully

This leaves the next natural implementation lane as F3 unless packaging/final-doc polish is prioritized first.
