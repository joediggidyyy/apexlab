"""Threshold-selection helpers for ApexLab."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional


def confusion_counts(y_true: list[int], y_pred: list[int]) -> dict[str, int]:
	tp = fp = tn = fn = 0
	for true_value, pred_value in zip(y_true, y_pred):
		if true_value == 1 and pred_value == 1:
			tp += 1
		elif true_value == 0 and pred_value == 1:
			fp += 1
		elif true_value == 0 and pred_value == 0:
			tn += 1
		elif true_value == 1 and pred_value == 0:
			fn += 1
	return {"tp": tp, "fp": fp, "tn": tn, "fn": fn}


def binary_metrics(conf: dict[str, int]) -> dict[str, float]:
	tp = float(conf.get("tp", 0))
	fp = float(conf.get("fp", 0))
	tn = float(conf.get("tn", 0))
	fn = float(conf.get("fn", 0))
	precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
	recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
	f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0
	fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
	return {"precision": precision, "recall": recall, "f1": f1, "fpr": fpr}


def choose_threshold(scores: list[float], y_true: list[int], max_fpr: float) -> float:
	if not scores:
		return 0.0
	candidates = sorted(set(scores))
	best_thr = float(candidates[0])
	best_f1 = -1.0
	for threshold in candidates:
		y_pred = [1 if s >= threshold else 0 for s in scores]
		metrics = binary_metrics(confusion_counts(y_true, y_pred))
		if metrics["fpr"] <= max_fpr and metrics["f1"] >= best_f1:
			best_f1 = metrics["f1"]
			best_thr = float(threshold)
	return best_thr


def select_lower_tail_threshold(scores: list[float], target_fpr: float) -> float:
	if not scores:
		return 0.0
	ordered = sorted(scores)
	idx = int(max(0, min(len(ordered) - 1, round(target_fpr * (len(ordered) - 1)))))
	return float(ordered[idx])


@dataclass
class ThresholdEvaluationResult:
	threshold: float
	max_fpr: float
	has_labels: bool
	counts: dict[str, int]
	metrics: dict[str, float]


def evaluate_scores(
	scores: list[float],
	*,
	ids: Optional[list[str]] = None,
	label_map: Optional[dict[str, str]] = None,
	positive_label: str = "1",
	max_fpr: float = 0.01,
) -> ThresholdEvaluationResult:
	ids = ids or [str(i) for i in range(len(scores))]
	label_map = label_map or {}

	if label_map:
		y_true = [1 if label_map.get(record_id) == positive_label else 0 for record_id in ids]
		threshold = choose_threshold(scores, y_true, max_fpr=max_fpr)
		y_pred = [1 if score >= threshold else 0 for score in scores]
		counts = confusion_counts(y_true, y_pred)
		return ThresholdEvaluationResult(
			threshold=float(threshold),
			max_fpr=float(max_fpr),
			has_labels=True,
			counts=counts,
			metrics=binary_metrics(counts),
		)

	threshold = select_lower_tail_threshold(scores, target_fpr=max_fpr)
	flagged = sum(1 for score in scores if score <= threshold)
	total = len(scores)
	return ThresholdEvaluationResult(
		threshold=float(threshold),
		max_fpr=float(max_fpr),
		has_labels=False,
		counts={"flagged": int(flagged), "total": int(total)},
		metrics={"flag_rate": (float(flagged) / float(total)) if total else 0.0},
	)
