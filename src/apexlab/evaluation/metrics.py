"""Metric helpers for ApexLab."""

from __future__ import annotations

import math
from typing import Any


def _to_float_list(values: list[str]) -> list[float]:
	out: list[float] = []
	for i, value in enumerate(values, start=1):
		try:
			out.append(float(value))
		except Exception as exc:
			raise ValueError(f"Could not parse float on row {i}: {value!r}") from exc
	return out


def regression_metrics(y_true: list[str] | list[float], y_pred: list[str] | list[float]) -> dict[str, Any]:
	if len(y_true) != len(y_pred):
		raise ValueError(f"Length mismatch: y_true={len(y_true)} y_pred={len(y_pred)}")

	yt = _to_float_list([str(v) for v in y_true])
	yp = _to_float_list([str(v) for v in y_pred])
	n = len(yt)
	if n == 0:
		return {"n": 0, "mae": 0.0, "mse": 0.0, "rmse": 0.0, "r2": 0.0}

	abs_errors = [abs(t - p) for t, p in zip(yt, yp)]
	sq_errors = [(t - p) ** 2 for t, p in zip(yt, yp)]
	mean_y = sum(yt) / float(n)
	ss_res = sum(sq_errors)
	ss_tot = sum((t - mean_y) ** 2 for t in yt)
	mse = ss_res / float(n)
	r2 = 1.0 - (ss_res / ss_tot) if ss_tot > 0 else 0.0
	return {
		"n": n,
		"mae": sum(abs_errors) / float(n),
		"mse": mse,
		"rmse": math.sqrt(mse),
		"r2": r2,
	}


def classification_metrics(y_true: list[str], y_pred: list[str]) -> dict[str, Any]:
	if len(y_true) != len(y_pred):
		raise ValueError(f"Length mismatch: y_true={len(y_true)} y_pred={len(y_pred)}")

	labels = sorted(set(y_true) | set(y_pred))
	label_to_idx = {label: i for i, label in enumerate(labels)}
	cm = [[0 for _ in labels] for _ in labels]
	for true_label, pred_label in zip(y_true, y_pred):
		cm[label_to_idx[true_label]][label_to_idx[pred_label]] += 1

	correct = sum(1 for t, p in zip(y_true, y_pred) if t == p)
	report: dict[str, Any] = {}
	for label in labels:
		idx = label_to_idx[label]
		tp = float(cm[idx][idx])
		fp = float(sum(cm[r][idx] for r in range(len(labels)) if r != idx))
		fn = float(sum(cm[idx][c] for c in range(len(labels)) if c != idx))
		support = float(sum(cm[idx]))
		precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
		recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
		f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0
		report[label] = {
			"precision": precision,
			"recall": recall,
			"f1-score": f1,
			"support": int(support),
		}

	accuracy = float(correct / len(y_true)) if y_true else 0.0
	report["accuracy"] = accuracy
	return {
		"n": len(y_true),
		"accuracy": accuracy,
		"labels": labels,
		"confusion_matrix": cm,
		"classification_report": report,
	}
