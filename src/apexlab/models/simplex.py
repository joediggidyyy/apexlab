"""Simplex/constrained model surface for ApexLab."""

from __future__ import annotations

from typing import Optional

import numpy as np


def project_simplex(v: np.ndarray) -> np.ndarray:
	"""Project a vector onto the probability simplex."""

	n_features = int(v.shape[0])
	if n_features == 0:
		return v.copy()

	u = np.sort(v)[::-1]
	cssv = np.cumsum(u)
	indices = np.arange(n_features) + 1
	cond = u + (1 - cssv) / indices > 0
	rho = int(indices[cond][-1] - 1)
	theta = float((cssv[rho] - 1) / (rho + 1.0))
	return np.maximum(v - theta, 0)


class ApexRegressor:
	"""Projected-gradient linear regression with simplex constraints."""

	def __init__(self, learning_rate: float = 0.01, max_iter: int = 1000, tol: float = 1e-6):
		self.learning_rate = float(learning_rate)
		self.max_iter = int(max_iter)
		self.tol = float(tol)
		self.weights: Optional[np.ndarray] = None
		self.history: list[float] = []

	def _project_simplex(self, v: np.ndarray) -> np.ndarray:
		return project_simplex(v)

	def fit(self, x: np.ndarray, y: np.ndarray) -> "ApexRegressor":
		if x.ndim != 2:
			raise ValueError("x must be a 2D array")
		if y.ndim != 1:
			raise ValueError("y must be a 1D array")
		if x.shape[0] != y.shape[0]:
			raise ValueError("x and y must have the same number of rows")

		n_samples, n_features = x.shape
		if n_samples == 0 or n_features == 0:
			raise ValueError("x must have at least one sample and one feature")

		if self.weights is None:
			self.weights = np.ones(n_features, dtype=float) / float(n_features)

		self.history = []
		for _ in range(self.max_iter):
			predictions = x @ self.weights
			errors = predictions - y
			gradient = (2.0 / float(n_samples)) * (x.T @ errors)

			w_new = self.weights - self.learning_rate * gradient
			w_projected = self._project_simplex(w_new)

			mse = float(np.mean(errors ** 2))
			self.history.append(mse)

			if np.linalg.norm(w_projected - self.weights) < self.tol:
				self.weights = w_projected
				break

			self.weights = w_projected

		return self

	def predict(self, x: np.ndarray) -> np.ndarray:
		if self.weights is None:
			raise ValueError("Model not fitted yet.")
		if x.ndim != 2:
			raise ValueError("x must be a 2D array")
		return x @ self.weights
