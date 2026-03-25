"""Regression-analysis helpers for ApexLab."""

from __future__ import annotations

from typing import Any, Sequence

import numpy as np

from apexlab.evaluation.metrics import regression_metrics


_EPSILON = 1e-12


def _coerce_matrix(x: Sequence[Sequence[float | int | str]], *, name: str = "x") -> np.ndarray:
	if not x:
		raise ValueError(f"{name} must not be empty")
	rows = [list(row) for row in x]
	if not rows or not rows[0]:
		raise ValueError(f"{name} must contain at least one row and one column")
	width = len(rows[0])
	for index, row in enumerate(rows, start=1):
		if len(row) != width:
			raise ValueError(f"{name} must not contain ragged rows (row {index} has length {len(row)}; expected {width})")
	try:
		array = np.asarray(rows, dtype=float)
	except Exception as exc:
		raise ValueError(f"{name} contains non-numeric values") from exc
	if array.ndim != 2 or array.shape[0] == 0 or array.shape[1] == 0:
		raise ValueError(f"{name} must be a non-empty 2D matrix")
	return array


def _coerce_vector(y: Sequence[float | int | str], *, name: str = "y") -> np.ndarray:
	if not y:
		raise ValueError(f"{name} must not be empty")
	try:
		array = np.asarray(list(y), dtype=float)
	except Exception as exc:
		raise ValueError(f"{name} contains non-numeric values") from exc
	if array.ndim != 1 or array.shape[0] == 0:
		raise ValueError(f"{name} must be a non-empty 1D vector")
	return array


def _validate_binary_vector(y: np.ndarray, *, name: str = "y") -> None:
	unique = set(float(value) for value in y.tolist())
	if not unique.issubset({0.0, 1.0}):
		raise ValueError(f"{name} must contain only binary values 0/1 for logistic regression")


def prepare_design_matrix(
	x: Sequence[Sequence[float | int | str]],
	*,
	add_intercept: bool = True,
) -> np.ndarray:
	matrix = _coerce_matrix(x, name="x")
	if not add_intercept:
		return matrix
	intercept = np.ones((matrix.shape[0], 1), dtype=float)
	return np.hstack((intercept, matrix))


def ols_predict(
	x: Sequence[Sequence[float | int | str]],
	coefficients: Sequence[float | int | str],
	*,
	add_intercept: bool = True,
) -> list[float]:
	design = prepare_design_matrix(x, add_intercept=add_intercept)
	coef = _coerce_vector(coefficients, name="coefficients")
	if design.shape[1] != coef.shape[0]:
		raise ValueError(
			f"Coefficient length mismatch: design has {design.shape[1]} columns but coefficients has {coef.shape[0]} values"
		)
	return (design @ coef).astype(float).tolist()


def ols_fit(
	x: Sequence[Sequence[float | int | str]],
	y: Sequence[float | int | str],
	*,
	add_intercept: bool = True,
) -> dict[str, Any]:
	design = prepare_design_matrix(x, add_intercept=add_intercept)
	target = _coerce_vector(y, name="y")
	if design.shape[0] != target.shape[0]:
		raise ValueError(f"Row mismatch: x has {design.shape[0]} rows but y has {target.shape[0]} values")
	coefficients, *_ = np.linalg.lstsq(design, target, rcond=None)
	predictions = design @ coefficients
	metrics = regression_metrics(target.astype(float).tolist(), predictions.astype(float).tolist())
	return {
		"model_type": "ols",
		"coefficients": coefficients.astype(float).tolist(),
		"predictions": predictions.astype(float).tolist(),
		"metrics": metrics,
		"converged": True,
		"notes": "Fitted using numpy least-squares on the provided design matrix.",
	}


def sigmoid(values: Sequence[float] | np.ndarray) -> np.ndarray:
	array = np.asarray(values, dtype=float)
	clipped = np.clip(array, -500.0, 500.0)
	return 1.0 / (1.0 + np.exp(-clipped))


def binary_cross_entropy(y_true: np.ndarray, probabilities: np.ndarray) -> float:
	probs = np.clip(probabilities, _EPSILON, 1.0 - _EPSILON)
	loss = -(y_true * np.log(probs) + (1.0 - y_true) * np.log(1.0 - probs))
	return float(np.mean(loss))


def _classification_accuracy(y_true: np.ndarray, y_pred: np.ndarray) -> float:
	return float(np.mean(y_true == y_pred)) if y_true.size else 0.0


def pseudo_r_squared(y_true: np.ndarray, probabilities: np.ndarray) -> float:
	probs = np.clip(probabilities, _EPSILON, 1.0 - _EPSILON)
	ll_model = float(np.sum(y_true * np.log(probs) + (1.0 - y_true) * np.log(1.0 - probs)))
	mean_rate = float(np.mean(y_true)) if y_true.size else 0.0
	null_probs = np.full_like(y_true, fill_value=min(max(mean_rate, _EPSILON), 1.0 - _EPSILON), dtype=float)
	ll_null = float(np.sum(y_true * np.log(null_probs) + (1.0 - y_true) * np.log(1.0 - null_probs)))
	if ll_null == 0.0:
		return 0.0
	return float(1.0 - (ll_model / ll_null))


def logistic_predict_proba(
	x: Sequence[Sequence[float | int | str]],
	coefficients: Sequence[float | int | str],
	*,
	add_intercept: bool = True,
) -> list[float]:
	design = prepare_design_matrix(x, add_intercept=add_intercept)
	coef = _coerce_vector(coefficients, name="coefficients")
	if design.shape[1] != coef.shape[0]:
		raise ValueError(
			f"Coefficient length mismatch: design has {design.shape[1]} columns but coefficients has {coef.shape[0]} values"
		)
	return sigmoid(design @ coef).astype(float).tolist()


def logistic_predict(
	x: Sequence[Sequence[float | int | str]],
	coefficients: Sequence[float | int | str],
	*,
	threshold: float = 0.5,
	add_intercept: bool = True,
) -> list[int]:
	return [1 if probability >= float(threshold) else 0 for probability in logistic_predict_proba(x, coefficients, add_intercept=add_intercept)]


def logistic_fit(
	x: Sequence[Sequence[float | int | str]],
	y: Sequence[float | int | str],
	*,
	learning_rate: float = 0.1,
	max_iter: int = 1000,
	tol: float = 1e-6,
	add_intercept: bool = True,
) -> dict[str, Any]:
	design = prepare_design_matrix(x, add_intercept=add_intercept)
	target = _coerce_vector(y, name="y")
	if design.shape[0] != target.shape[0]:
		raise ValueError(f"Row mismatch: x has {design.shape[0]} rows but y has {target.shape[0]} values")
	_validate_binary_vector(target, name="y")
	weights = np.zeros(design.shape[1], dtype=float)
	history: list[float] = []
	converged = False
	iterations = 0
	for iteration in range(1, int(max_iter) + 1):
		logits = design @ weights
		probabilities = sigmoid(logits)
		loss = binary_cross_entropy(target, probabilities)
		history.append(float(loss))
		gradient = (design.T @ (probabilities - target)) / float(design.shape[0])
		new_weights = weights - float(learning_rate) * gradient
		if np.linalg.norm(new_weights - weights) < float(tol):
			weights = new_weights
			iterations = iteration
			converged = True
			break
		weights = new_weights
		iterations = iteration
	if not converged and history:
		converged = len(history) > 1 and abs(history[-1] - history[-2]) < float(tol)
	probabilities = sigmoid(design @ weights)
	predictions = (probabilities >= 0.5).astype(int)
	metrics = {
		"n": int(target.shape[0]),
		"log_loss": float(binary_cross_entropy(target, probabilities)),
		"accuracy": float(_classification_accuracy(target.astype(int), predictions)),
		"positive_rate": float(np.mean(predictions)) if predictions.size else 0.0,
		"pseudo_r2": float(pseudo_r_squared(target, probabilities)),
	}
	return {
		"model_type": "logistic",
		"coefficients": weights.astype(float).tolist(),
		"probabilities": probabilities.astype(float).tolist(),
		"predictions": predictions.astype(int).tolist(),
		"metrics": metrics,
		"converged": bool(converged),
		"iterations": int(iterations),
		"history": [float(value) for value in history],
		"notes": "Fitted using deterministic gradient descent on binary cross-entropy loss.",
	}


def summarize_coefficients(
	coefficients: Sequence[float | int | str],
	*,
	feature_names: Sequence[str] | None = None,
	intercept_label: str = "intercept",
) -> list[dict[str, Any]]:
	coef = _coerce_vector(coefficients, name="coefficients")
	if feature_names is None:
		feature_names = [intercept_label] + [f"feature_{index}" for index in range(1, len(coef))]
	else:
		feature_names = list(feature_names)
		if len(feature_names) == len(coef) - 1:
			feature_names = [intercept_label] + feature_names
		if len(feature_names) != len(coef):
			raise ValueError(
				f"feature_names length mismatch: expected {len(coef)} names including intercept or {len(coef) - 1} without intercept"
			)
	rows: list[dict[str, Any]] = []
	for feature, coefficient in zip(feature_names, coef.tolist()):
		magnitude = abs(float(coefficient))
		if coefficient > 0:
			sign = "positive"
			interpretation = "positive association with outcome"
		elif coefficient < 0:
			sign = "negative"
			interpretation = "negative association with outcome"
		else:
			sign = "zero"
			interpretation = "near-zero contribution in current fit"
		rows.append(
			{
				"feature": str(feature),
				"coefficient": float(coefficient),
				"sign": sign,
				"magnitude": float(magnitude),
				"interpretation": interpretation,
			}
		)
	return rows
