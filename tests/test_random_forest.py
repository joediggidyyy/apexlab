from pathlib import Path

import numpy as np

import pytest

from conftest import import_module_from_path


module = import_module_from_path(
	"apexlab_random_forest_mod",
	Path(__file__).resolve().parents[1] / "src" / "apexlab" / "models" / "random_forest.py",
)

RandomForestClassifier = module.RandomForestClassifier


def _toy_dataset() -> tuple[np.ndarray, np.ndarray]:
	x = np.array([
		[0.0, 0.0],
		[0.1, 0.2],
		[0.2, 0.1],
		[1.0, 1.0],
		[1.1, 1.2],
		[1.2, 1.1],
	])
	y = np.array([0, 0, 0, 1, 1, 1])
	return x, y


def test_random_forest_fit_returns_self() -> None:
	x, y = _toy_dataset()
	model = RandomForestClassifier(n_estimators=8, random_state=42)
	assert model.fit(x, y) is model


def test_random_forest_predict_proba_shape_is_stable() -> None:
	x, y = _toy_dataset()
	model = RandomForestClassifier(n_estimators=8, random_state=42).fit(x, y)
	probas = model.predict_proba(x)
	assert len(probas) == len(x)
	for row in probas:
		assert len(row) == 2
		assert row[0] + row[1] == pytest.approx(1.0)


def test_random_forest_predicts_simple_binary_fixture() -> None:
	x, y = _toy_dataset()
	model = RandomForestClassifier(n_estimators=16, random_state=7, bootstrap=False).fit(x, y)
	assert model.predict(x) == y.tolist()


def test_random_forest_is_deterministic_under_fixed_seed() -> None:
	x, y = _toy_dataset()
	model_a = RandomForestClassifier(n_estimators=16, random_state=123).fit(x, y)
	model_b = RandomForestClassifier(n_estimators=16, random_state=123).fit(x, y)
	assert np.allclose(np.asarray(model_a.predict_proba(x)), np.asarray(model_b.predict_proba(x)))
	assert model_a.predict(x) == model_b.predict(x)


def test_random_forest_handles_feature_subsampling_and_predict_requires_fit() -> None:
	x, y = _toy_dataset()
	model = RandomForestClassifier(n_estimators=8, max_features="sqrt", random_state=42).fit(x, y)
	preds = model.predict(x)
	assert len(preds) == len(x)
	with pytest.raises(ValueError, match="Model not fitted yet"):
		RandomForestClassifier().predict(x)