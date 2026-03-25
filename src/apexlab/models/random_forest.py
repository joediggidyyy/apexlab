"""Random forest classifier surface for ApexLab."""

from __future__ import annotations

from typing import Optional, Sequence

import numpy as np

from apexlab.models.decision_tree import DecisionTreeClassifier, _coerce_binary_labels, _coerce_matrix


class RandomForestClassifier:
	"""Deterministic binary random forest classifier."""

	def __init__(
		self,
		*,
		n_estimators: int = 100,
		max_depth: int | None = None,
		min_samples_split: int = 2,
		max_features: int | float | str | None = "sqrt",
		bootstrap: bool = True,
		random_state: int | None = None,
	):
		if int(n_estimators) <= 0:
			raise ValueError("n_estimators must be positive")
		self.n_estimators = int(n_estimators)
		self.max_depth = max_depth
		self.min_samples_split = int(min_samples_split)
		self.max_features = max_features
		self.bootstrap = bool(bootstrap)
		self.random_state = random_state
		self._rng = np.random.default_rng(random_state)
		self.trees_: list[DecisionTreeClassifier] = []
		self.n_features_in_: Optional[int] = None

	def fit(self, x: Sequence[Sequence[float | int | str]] | np.ndarray, y: Sequence[int | float | str] | np.ndarray) -> "RandomForestClassifier":
		matrix = _coerce_matrix(x, name="x")
		labels = _coerce_binary_labels(y, name="y")
		if matrix.shape[0] != labels.shape[0]:
			raise ValueError("x and y must have the same number of rows")
		self.n_features_in_ = int(matrix.shape[1])
		self._rng = np.random.default_rng(self.random_state)
		self.trees_ = []

		for _ in range(self.n_estimators):
			if self.bootstrap:
				indices = self._rng.integers(0, matrix.shape[0], size=matrix.shape[0])
			else:
				indices = np.arange(matrix.shape[0])
			tree = DecisionTreeClassifier(
				max_depth=self.max_depth,
				min_samples_split=self.min_samples_split,
				max_features=self.max_features,
				random_state=int(self._rng.integers(0, 2**31 - 1)),
			)
			tree.fit(matrix[indices], labels[indices])
			self.trees_.append(tree)
		return self

	def predict_proba(self, x: Sequence[Sequence[float | int | str]] | np.ndarray) -> list[list[float]]:
		if not self.trees_:
			raise ValueError("Model not fitted yet.")
		matrix = _coerce_matrix(x, name="x")
		if self.n_features_in_ is not None and matrix.shape[1] != self.n_features_in_:
			raise ValueError(f"x must contain exactly {self.n_features_in_} features")
		per_tree = np.asarray([tree.predict_proba(matrix) for tree in self.trees_], dtype=float)
		return np.mean(per_tree, axis=0).astype(float).tolist()

	def predict(self, x: Sequence[Sequence[float | int | str]] | np.ndarray) -> list[int]:
		return [1 if row[1] >= 0.5 else 0 for row in self.predict_proba(x)]