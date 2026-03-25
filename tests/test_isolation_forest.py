from pathlib import Path

import numpy as np
import pytest

from conftest import import_module_from_path


module = import_module_from_path(
	"apexlab_isolation_forest_mod",
	Path(__file__).resolve().parents[1] / "src" / "apexlab" / "models" / "isolation_forest.py",
)

IsolationForest = module.IsolationForest


def test_isolation_forest_fit_returns_self() -> None:
	x = np.array([[0.0, 0.0], [0.1, 0.2], [0.2, 0.1], [8.0, 8.0]])
	model = IsolationForest(n_estimators=16, random_state=42)
	assert model.fit(x) is model


def test_score_samples_returns_one_score_per_row() -> None:
	x = np.array([[0.0, 0.0], [0.1, 0.2], [0.2, 0.1], [8.0, 8.0]])
	model = IsolationForest(n_estimators=16, random_state=42).fit(x)
	scores = model.score_samples(x)
	assert len(scores) == len(x)
	assert all(isinstance(score, float) for score in scores)


def test_obvious_outlier_receives_highest_anomaly_score() -> None:
	x = np.array([
		[0.0, 0.0],
		[0.1, -0.1],
		[-0.1, 0.1],
		[0.2, 0.0],
		[0.0, 0.2],
		[9.0, 9.0],
	])
	model = IsolationForest(n_estimators=64, random_state=7).fit(x)
	scores = model.score_samples(x)
	assert int(np.argmax(scores)) == len(x) - 1


def test_predict_is_deterministic_under_fixed_seed() -> None:
	x = np.array([
		[0.0, 0.0],
		[0.1, -0.1],
		[-0.1, 0.1],
		[0.2, 0.0],
		[0.0, 0.2],
		[9.0, 9.0],
	])
	model_a = IsolationForest(n_estimators=32, random_state=123, contamination=0.2).fit(x)
	model_b = IsolationForest(n_estimators=32, random_state=123, contamination=0.2).fit(x)
	assert model_a.score_samples(x) == pytest.approx(model_b.score_samples(x))
	assert model_a.predict(x) == model_b.predict(x)


def test_invalid_input_shapes_raise_clear_errors() -> None:
	with pytest.raises(ValueError, match="2D numeric array"):
		IsolationForest().fit([1.0, 2.0, 3.0])
	with pytest.raises(ValueError, match="at least one row and one column"):
		IsolationForest().fit(np.empty((0, 2)))
	with pytest.raises(ValueError, match="2D numeric array"):
		IsolationForest().fit(np.asarray([[1.0, 2.0], [3.0, "oops"]], dtype=object))


def test_degenerate_rows_do_not_crash_tree_construction() -> None:
	x = np.array([[1.0, 1.0], [1.0, 1.0], [1.0, 1.0], [1.0, 1.0]])
	model = IsolationForest(n_estimators=8, random_state=1).fit(x)
	scores = model.score_samples(x)
	assert len(scores) == 4
	assert all(np.isfinite(score) for score in scores)


def test_max_samples_is_respected_and_recorded() -> None:
	x = np.array([[float(index), float(index % 3)] for index in range(20)])
	model = IsolationForest(n_estimators=8, max_samples=5, random_state=11).fit(x)
	assert model.max_samples_ == 5
	assert model.max_depth_ is not None


def test_predict_requires_fit() -> None:
	with pytest.raises(ValueError, match="Model not fitted yet"):
		IsolationForest().predict([[0.0, 0.0]])