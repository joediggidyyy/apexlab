from pathlib import Path

import numpy as np

import pytest

from conftest import import_module_from_path


module = import_module_from_path(
	"apexlab_decision_tree_mod",
	Path(__file__).resolve().parents[1] / "src" / "apexlab" / "models" / "decision_tree.py",
)

DecisionTreeClassifier = module.DecisionTreeClassifier


def test_decision_tree_fit_returns_self() -> None:
	x = np.array([[0.0], [0.1], [0.2], [1.0], [1.1], [1.2]])
	y = np.array([0, 0, 0, 1, 1, 1])
	model = DecisionTreeClassifier(random_state=42)
	assert model.fit(x, y) is model


def test_decision_tree_separates_simple_binary_dataset() -> None:
	x = np.array([[0.0], [0.1], [0.2], [1.0], [1.1], [1.2]])
	y = np.array([0, 0, 0, 1, 1, 1])
	model = DecisionTreeClassifier(random_state=42).fit(x, y)
	assert model.predict(x) == y.tolist()


def test_decision_tree_predict_proba_returns_valid_rows() -> None:
	x = np.array([[0.0], [0.1], [0.2], [1.0], [1.1], [1.2]])
	y = np.array([0, 0, 0, 1, 1, 1])
	model = DecisionTreeClassifier(random_state=42).fit(x, y)
	probas = model.predict_proba(x)
	assert len(probas) == len(x)
	for row in probas:
		assert len(row) == 2
		assert row[0] + row[1] == pytest.approx(1.0)


def test_decision_tree_rejects_non_binary_labels() -> None:
	with pytest.raises(ValueError, match="binary values 0/1"):
		DecisionTreeClassifier().fit([[0.0], [1.0], [2.0]], [0, 1, 2])


def test_decision_tree_rejects_invalid_shapes() -> None:
	with pytest.raises(ValueError, match="same number of rows"):
		DecisionTreeClassifier().fit([[0.0], [1.0]], [0])
	with pytest.raises(ValueError, match="2D numeric array"):
		DecisionTreeClassifier().fit([0.0, 1.0, 2.0], [0, 1, 1])


def test_decision_tree_respects_stopping_rules() -> None:
	x = np.array([[0.0], [0.1], [0.2], [1.0], [1.1], [1.2]])
	y = np.array([0, 0, 0, 1, 1, 1])
	model = DecisionTreeClassifier(max_depth=1, min_samples_split=4, random_state=42).fit(x, y)
	preds = model.predict(x)
	assert len(preds) == len(x)
	assert set(preds).issubset({0, 1})


def test_decision_tree_predict_requires_fit() -> None:
	with pytest.raises(ValueError, match="Model not fitted yet"):
		DecisionTreeClassifier().predict([[0.0], [1.0]])