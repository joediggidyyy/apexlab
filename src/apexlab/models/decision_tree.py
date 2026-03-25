"""Decision tree classifier surface for ApexLab."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Sequence

import numpy as np


def _coerce_matrix(x: Sequence[Sequence[float | int | str]] | np.ndarray, *, name: str = "x") -> np.ndarray:
	try:
		array = np.asarray(x, dtype=float)
	except (TypeError, ValueError) as exc:
		raise ValueError(f"{name} must be a 2D numeric array") from exc
	if array.ndim != 2:
		raise ValueError(f"{name} must be a 2D numeric array")
	if array.shape[0] == 0 or array.shape[1] == 0:
		raise ValueError(f"{name} must contain at least one row and one column")
	return array


def _coerce_binary_labels(y: Sequence[int | float | str] | np.ndarray, *, name: str = "y") -> np.ndarray:
	try:
		array = np.asarray(y, dtype=float)
	except (TypeError, ValueError) as exc:
		raise ValueError(f"{name} must be a 1D binary numeric array") from exc
	if array.ndim != 1 or array.shape[0] == 0:
		raise ValueError(f"{name} must be a non-empty 1D array")
	unique = set(float(value) for value in array.tolist())
	if not unique.issubset({0.0, 1.0}):
		raise ValueError(f"{name} must contain only binary values 0/1")
	return array.astype(int)


def _resolve_max_features(max_features: int | float | str | None, n_features: int) -> int:
	if max_features is None:
		return n_features
	if isinstance(max_features, str):
		if max_features == "sqrt":
			return max(1, int(np.sqrt(n_features)))
		raise ValueError("max_features must be None, 'sqrt', an integer count, or a fraction in (0, 1]")
	if isinstance(max_features, float):
		if not (0.0 < max_features <= 1.0):
			raise ValueError("Float max_features must be in the interval (0, 1]")
		return max(1, min(n_features, int(np.ceil(n_features * max_features))))
	resolved = int(max_features)
	if resolved <= 0:
		raise ValueError("Integer max_features must be positive")
	return min(n_features, resolved)


def _gini_impurity(y: np.ndarray) -> float:
	if y.size == 0:
		return 0.0
	positive_rate = float(np.mean(y))
	negative_rate = 1.0 - positive_rate
	return float(1.0 - (positive_rate**2 + negative_rate**2))


@dataclass
class _DecisionNode:
	feature_index: Optional[int]
	threshold: Optional[float]
	left: Optional["_DecisionNode"]
	right: Optional["_DecisionNode"]
	probabilities: tuple[float, float]
	depth: int

	@property
	def is_leaf(self) -> bool:
		return self.left is None or self.right is None or self.feature_index is None or self.threshold is None


class DecisionTreeClassifier:
	"""Deterministic binary decision tree classifier using Gini impurity."""

	def __init__(
		self,
		*,
		max_depth: int | None = None,
		min_samples_split: int = 2,
		max_features: int | float | str | None = None,
		random_state: int | None = None,
	):
		if max_depth is not None and int(max_depth) <= 0:
			raise ValueError("max_depth must be positive when provided")
		if int(min_samples_split) < 2:
			raise ValueError("min_samples_split must be at least 2")
		self.max_depth = None if max_depth is None else int(max_depth)
		self.min_samples_split = int(min_samples_split)
		self.max_features = max_features
		self.random_state = random_state
		self._rng = np.random.default_rng(random_state)
		self.n_features_in_: Optional[int] = None
		self.root_: Optional[_DecisionNode] = None

	def _leaf_probabilities(self, y: np.ndarray) -> tuple[float, float]:
		positive_rate = float(np.mean(y)) if y.size else 0.0
		return (1.0 - positive_rate, positive_rate)

	def _candidate_thresholds(self, values: np.ndarray) -> list[float]:
		unique = np.unique(values)
		if unique.size < 2:
			return []
		return [float((unique[index] + unique[index + 1]) / 2.0) for index in range(unique.size - 1)]

	def _best_split(self, x: np.ndarray, y: np.ndarray) -> tuple[Optional[int], Optional[float]]:
		n_rows, n_features = x.shape
		n_candidates = _resolve_max_features(self.max_features, n_features)
		candidate_features = np.arange(n_features)
		if n_candidates < n_features:
			candidate_features = np.sort(self._rng.choice(candidate_features, size=n_candidates, replace=False))

		best_feature: Optional[int] = None
		best_threshold: Optional[float] = None
		best_score = float("inf")
		for feature_index in candidate_features.tolist():
			thresholds = self._candidate_thresholds(x[:, feature_index])
			for threshold in thresholds:
				left_mask = x[:, feature_index] < threshold
				right_mask = ~left_mask
				if not np.any(left_mask) or not np.any(right_mask):
					continue
				left_y = y[left_mask]
				right_y = y[right_mask]
				score = (
					(left_y.size / float(n_rows)) * _gini_impurity(left_y)
					+ (right_y.size / float(n_rows)) * _gini_impurity(right_y)
				)
				if score < best_score:
					best_score = float(score)
					best_feature = int(feature_index)
					best_threshold = float(threshold)
		return best_feature, best_threshold

	def _build_tree(self, x: np.ndarray, y: np.ndarray, *, depth: int) -> _DecisionNode:
		probabilities = self._leaf_probabilities(y)
		if (
			y.size < self.min_samples_split
			or np.all(y == y[0])
			or (self.max_depth is not None and depth >= self.max_depth)
		):
			return _DecisionNode(None, None, None, None, probabilities, int(depth))

		feature_index, threshold = self._best_split(x, y)
		if feature_index is None or threshold is None:
			return _DecisionNode(None, None, None, None, probabilities, int(depth))

		left_mask = x[:, feature_index] < threshold
		right_mask = ~left_mask
		if not np.any(left_mask) or not np.any(right_mask):
			return _DecisionNode(None, None, None, None, probabilities, int(depth))

		left = self._build_tree(x[left_mask], y[left_mask], depth=depth + 1)
		right = self._build_tree(x[right_mask], y[right_mask], depth=depth + 1)
		return _DecisionNode(int(feature_index), float(threshold), left, right, probabilities, int(depth))

	def _traverse(self, row: np.ndarray, node: _DecisionNode) -> _DecisionNode:
		if node.is_leaf:
			return node
		assert node.feature_index is not None
		assert node.threshold is not None
		assert node.left is not None
		assert node.right is not None
		child = node.left if row[node.feature_index] < node.threshold else node.right
		return self._traverse(row, child)

	def fit(self, x: Sequence[Sequence[float | int | str]] | np.ndarray, y: Sequence[int | float | str] | np.ndarray) -> "DecisionTreeClassifier":
		matrix = _coerce_matrix(x, name="x")
		labels = _coerce_binary_labels(y, name="y")
		if matrix.shape[0] != labels.shape[0]:
			raise ValueError("x and y must have the same number of rows")
		self.n_features_in_ = int(matrix.shape[1])
		self._rng = np.random.default_rng(self.random_state)
		self.root_ = self._build_tree(matrix, labels, depth=0)
		return self

	def predict_proba(self, x: Sequence[Sequence[float | int | str]] | np.ndarray) -> list[list[float]]:
		if self.root_ is None:
			raise ValueError("Model not fitted yet.")
		matrix = _coerce_matrix(x, name="x")
		if self.n_features_in_ is not None and matrix.shape[1] != self.n_features_in_:
			raise ValueError(f"x must contain exactly {self.n_features_in_} features")
		return [list(self._traverse(row, self.root_).probabilities) for row in matrix]

	def predict(self, x: Sequence[Sequence[float | int | str]] | np.ndarray) -> list[int]:
		return [1 if row[1] >= 0.5 else 0 for row in self.predict_proba(x)]