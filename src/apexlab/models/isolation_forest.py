"""Isolation forest model surface for ApexLab."""

from __future__ import annotations

from dataclasses import dataclass
from math import ceil, log2
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


def _average_path_length_for_size(size: int) -> float:
	if size <= 1:
		return 0.0
	if size == 2:
		return 1.0
	harmonic = sum(1.0 / float(index) for index in range(1, size))
	return float((2.0 * harmonic) - (2.0 * (size - 1) / float(size)))


def _resolve_max_samples(max_samples: int | float | str, n_rows: int) -> int:
	if isinstance(max_samples, str):
		if max_samples != "auto":
			raise ValueError("max_samples must be 'auto', an integer count, or a fraction in (0, 1]")
		return min(256, n_rows)
	if isinstance(max_samples, float):
		if not (0.0 < max_samples <= 1.0):
			raise ValueError("Float max_samples must be in the interval (0, 1]")
		return max(1, min(n_rows, int(np.ceil(n_rows * max_samples))))
	resolved = int(max_samples)
	if resolved <= 0:
		raise ValueError("Integer max_samples must be positive")
	return min(n_rows, resolved)


@dataclass
class _IsolationNode:
	feature_index: Optional[int]
	split_value: Optional[float]
	left: Optional["_IsolationNode"]
	right: Optional["_IsolationNode"]
	size: int
	depth: int

	@property
	def is_leaf(self) -> bool:
		return self.left is None or self.right is None or self.feature_index is None or self.split_value is None


class IsolationForest:
	"""Deterministic isolation forest for lightweight anomaly scoring.

	Scores returned by ``score_samples`` use the conventional isolation-forest direction:
	higher values indicate more anomalous rows.
	"""

	def __init__(
		self,
		*,
		n_estimators: int = 100,
		max_samples: int | float | str = "auto",
		max_depth: int | None = None,
		random_state: int | None = None,
		contamination: float = 0.1,
	):
		if int(n_estimators) <= 0:
			raise ValueError("n_estimators must be positive")
		if contamination <= 0.0 or contamination >= 0.5:
			raise ValueError("contamination must be greater than 0.0 and less than 0.5")
		self.n_estimators = int(n_estimators)
		self.max_samples = max_samples
		self.max_depth = None if max_depth is None else int(max_depth)
		self.random_state = random_state
		self.contamination = float(contamination)
		self._rng = np.random.default_rng(random_state)
		self.trees_: list[_IsolationNode] = []
		self.max_samples_: Optional[int] = None
		self.max_depth_: Optional[int] = None
		self.threshold_: Optional[float] = None
		self.training_scores_: list[float] = []

	def _build_tree(self, x: np.ndarray, *, depth: int) -> _IsolationNode:
		n_rows, n_features = x.shape
		assert self.max_depth_ is not None
		if depth >= self.max_depth_ or n_rows <= 1:
			return _IsolationNode(None, None, None, None, int(n_rows), int(depth))

		feature_mins = np.min(x, axis=0)
		feature_maxs = np.max(x, axis=0)
		candidate_features = [index for index in range(n_features) if feature_maxs[index] > feature_mins[index]]
		if not candidate_features:
			return _IsolationNode(None, None, None, None, int(n_rows), int(depth))

		feature_index = int(self._rng.choice(candidate_features))
		feature_min = float(feature_mins[feature_index])
		feature_max = float(feature_maxs[feature_index])
		split_value = float(self._rng.uniform(feature_min, feature_max))
		left_mask = x[:, feature_index] < split_value
		right_mask = ~left_mask

		if not np.any(left_mask) or not np.any(right_mask):
			split_value = float((feature_min + feature_max) / 2.0)
			left_mask = x[:, feature_index] < split_value
			right_mask = ~left_mask
			if not np.any(left_mask) or not np.any(right_mask):
				return _IsolationNode(None, None, None, None, int(n_rows), int(depth))

		left = self._build_tree(x[left_mask], depth=depth + 1)
		right = self._build_tree(x[right_mask], depth=depth + 1)
		return _IsolationNode(feature_index, split_value, left, right, int(n_rows), int(depth))

	def _path_length_for_row(self, row: np.ndarray, node: _IsolationNode) -> float:
		if node.is_leaf:
			return float(node.depth) + _average_path_length_for_size(node.size)
		assert node.feature_index is not None
		assert node.split_value is not None
		assert node.left is not None
		assert node.right is not None
		child = node.left if row[node.feature_index] < node.split_value else node.right
		return self._path_length_for_row(row, child)

	def fit(self, x: Sequence[Sequence[float | int | str]] | np.ndarray) -> "IsolationForest":
		matrix = _coerce_matrix(x, name="x")
		n_rows = int(matrix.shape[0])
		self.max_samples_ = _resolve_max_samples(self.max_samples, n_rows)
		self.max_depth_ = self.max_depth if self.max_depth is not None else max(1, int(ceil(log2(self.max_samples_))))
		self._rng = np.random.default_rng(self.random_state)
		self.trees_ = []

		for _ in range(self.n_estimators):
			if self.max_samples_ >= n_rows:
				sample = matrix
			else:
				indices = self._rng.choice(n_rows, size=self.max_samples_, replace=False)
				sample = matrix[indices]
			self.trees_.append(self._build_tree(sample, depth=0))

		self.training_scores_ = self.score_samples(matrix)
		self.threshold_ = float(np.quantile(np.asarray(self.training_scores_, dtype=float), 1.0 - self.contamination))
		return self

	def score_samples(self, x: Sequence[Sequence[float | int | str]] | np.ndarray) -> list[float]:
		if not self.trees_:
			raise ValueError("Model not fitted yet.")
		matrix = _coerce_matrix(x, name="x")
		assert self.max_samples_ is not None
		normalizer = _average_path_length_for_size(self.max_samples_)
		if normalizer <= 0.0:
			return [0.0 for _ in range(matrix.shape[0])]
		scores: list[float] = []
		for row in matrix:
			mean_path_length = float(np.mean([self._path_length_for_row(row, tree) for tree in self.trees_]))
			score = float(2.0 ** (-mean_path_length / normalizer))
			scores.append(score)
		return scores

	def predict(self, x: Sequence[Sequence[float | int | str]] | np.ndarray) -> list[int]:
		if self.threshold_ is None:
			raise ValueError("Model not fitted yet.")
		return [1 if score >= self.threshold_ else 0 for score in self.score_samples(x)]