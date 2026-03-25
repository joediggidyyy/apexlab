# ApexLab API Overview

This document summarizes the currently implemented public ApexLab surfaces.

## Package root

- `apexlab.ApexRegressor`
	- projected-gradient linear regressor with simplex-constrained weights

## `apexlab.models.simplex`

- `project_simplex(v)`
	- projects a numeric vector onto the probability simplex
- `ApexRegressor(learning_rate=0.01, max_iter=1000, tol=1e-6)`
	- `fit(x, y)` trains simplex-constrained weights
	- `predict(x)` produces predictions after fitting
	- `history` stores per-iteration mean-squared-error values

## `apexlab.models.isolation_forest`

- `IsolationForest(n_estimators=100, max_samples='auto', max_depth=None, random_state=None, contamination=0.1)`
	- `fit(x)` trains a deterministic isolation forest under the configured seed
	- `score_samples(x)` returns anomaly-oriented scores where higher values indicate more anomalous rows
	- `predict(x)` returns binary anomaly labels using the fitted contamination threshold

## `apexlab.models.decision_tree`

- `DecisionTreeClassifier(max_depth=None, min_samples_split=2, max_features=None, random_state=None)`
	- `fit(x, y)` trains a deterministic binary decision tree using Gini impurity
	- `predict_proba(x)` returns per-row class probabilities as `[p_negative, p_positive]`
	- `predict(x)` returns binary class predictions from the fitted tree

## `apexlab.models.random_forest`

- `RandomForestClassifier(n_estimators=100, max_depth=None, min_samples_split=2, max_features='sqrt', bootstrap=True, random_state=None)`
	- `fit(x, y)` trains a deterministic binary random forest over decision-tree estimators
	- `predict_proba(x)` returns mean class probabilities aggregated across the fitted trees
	- `predict(x)` returns binary class predictions from the aggregated probabilities

## `apexlab.diagnostics.convergence`

- `summarize_history(history, tolerance=None)`
	- returns a compact summary of optimization progress and convergence state

## `apexlab.datasets.split`

- `SplitResult`
	- dataclass containing `train_indices` and `test_indices`
- `parse_test_size(test_size)`
	- parses count or fraction text input into a normalized form
- `allocate_counts_proportionally(total_test, bucket_sizes)`
	- distributes test counts across label buckets
- `split_indices(n_rows, *, test_size, seed, stratify=None)`
	- deterministic split helper with optional stratification

## `apexlab.evaluation.metrics`

- `regression_metrics(y_true, y_pred)`
	- returns `n`, `mae`, `mse`, `rmse`, and `r2`
- `classification_metrics(y_true, y_pred)`
	- returns accuracy, labels, confusion matrix, and per-label report content

## `apexlab.evaluation.compare_report`

- `build_compare_report(comparison, *, generated_at_utc=None, inputs=None, context=None, code=None)`
	- wraps a comparison payload into a stable report artifact with identity, inputs, interpretation, flags, and producer metadata
	- intended to be the canonical comparison-report builder for the current Leg 2 reporting lane

## `apexlab.evaluation.thresholds`

- `confusion_counts(y_true, y_pred)`
- `binary_metrics(conf)`
- `choose_threshold(scores, y_true, max_fpr)`
- `select_lower_tail_threshold(scores, target_fpr)`
- `ThresholdEvaluationResult`
- `evaluate_scores(scores, *, ids=None, label_map=None, positive_label='1', max_fpr=0.01)`

These helpers support both labeled threshold selection and unlabeled lower-tail score flagging.

## `apexlab.evaluation.reports`

- `utc_now_iso()`
- `render_markdown_report(report)`
- `write_reports(report, out_dir, *, stem='report')`

These helpers write paired JSON and Markdown outputs for lightweight experiment summaries and now support richer comparison and regression reporting sections.

## `apexlab.utils.io`

- `read_single_column_csv(path)`
	- reads a simple single-column CSV file into a list of values

## `apexlab.utils.manifests`

- `write_manifest(path, payload)`
- `read_manifest(path)`

These manifest helpers support small reproducible demo/report workflows.

## Example validation and field-test surfaces

- `examples/evaluation_demo.py`
	- canonical **field test** surface for end-to-end package execution across current Leg 1 + Leg 2 lite functionality
- `examples/reference_validation_run.py`
	- canonical external reference-validation surface for comparison against SciPy / scikit-learn baselines
