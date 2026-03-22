# ApexLab API Overview

This document summarizes the currently implemented public Leg 1 surfaces.

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

These helpers write paired JSON and Markdown outputs for lightweight experiment summaries.

## `apexlab.utils.io`

- `read_single_column_csv(path)`
	- reads a simple single-column CSV file into a list of values

## `apexlab.utils.manifests`

- `write_manifest(path, payload)`
- `read_manifest(path)`

These manifest helpers support small reproducible demo/report workflows.
