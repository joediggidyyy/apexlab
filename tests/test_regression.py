from pathlib import Path

import pytest

from conftest import import_module_from_path


regression = import_module_from_path(
    "apexlab_regression_mod",
    Path(__file__).resolve().parents[1] / "src" / "apexlab" / "analysis" / "regression.py",
)


def test_prepare_design_matrix_adds_intercept() -> None:
    matrix = regression.prepare_design_matrix([[1.0], [2.0], [3.0]], add_intercept=True)
    assert matrix.shape == (3, 2)
    assert matrix[:, 0].tolist() == pytest.approx([1.0, 1.0, 1.0])


def test_ols_fit_recovers_simple_linear_relationship() -> None:
    result = regression.ols_fit([[1.0], [2.0], [3.0], [4.0]], [3.0, 5.0, 7.0, 9.0])
    assert result["model_type"] == "ols"
    assert result["coefficients"] == pytest.approx([1.0, 2.0], rel=1e-5, abs=1e-5)
    assert result["metrics"]["r2"] > 0.999
    assert result["converged"] is True


def test_ols_predict_uses_coefficients_correctly() -> None:
    preds = regression.ols_predict([[5.0], [6.0]], [1.0, 2.0])
    assert preds == pytest.approx([11.0, 13.0])


def test_logistic_fit_handles_separable_toy_data() -> None:
    x = [[0.0], [1.0], [2.0], [3.0], [4.0], [5.0]]
    y = [0, 0, 0, 1, 1, 1]
    result = regression.logistic_fit(x, y, learning_rate=0.2, max_iter=4000, tol=1e-7)
    assert result["model_type"] == "logistic"
    assert result["metrics"]["accuracy"] >= 0.83
    assert result["iterations"] > 0
    assert len(result["history"]) == result["iterations"]
    assert result["coefficients"][1] > 0.0


def test_logistic_fit_rejects_non_binary_labels() -> None:
    with pytest.raises(ValueError, match="binary values 0/1"):
        regression.logistic_fit([[0.0], [1.0], [2.0]], [0, 1, 2])


def test_invalid_shapes_raise_clear_errors() -> None:
    with pytest.raises(ValueError, match="ragged rows"):
        regression.prepare_design_matrix([[1.0, 2.0], [3.0]])
    with pytest.raises(ValueError, match="Row mismatch"):
        regression.ols_fit([[1.0], [2.0]], [1.0])


def test_summarize_coefficients_returns_stable_structure() -> None:
    rows = regression.summarize_coefficients([0.5, -2.0, 0.0], feature_names=["f1", "f2"])
    assert [row["feature"] for row in rows] == ["intercept", "f1", "f2"]
    assert rows[1]["sign"] == "negative"
    assert "association" in rows[1]["interpretation"]


def test_logistic_fit_exposes_history_and_prediction_helpers() -> None:
    x = [[0.0], [1.0], [2.0], [3.0]]
    y = [0, 0, 1, 1]
    result = regression.logistic_fit(x, y, learning_rate=0.2, max_iter=3000, tol=1e-7)
    probabilities = regression.logistic_predict_proba(x, result["coefficients"])
    predictions = regression.logistic_predict(x, result["coefficients"])
    assert len(probabilities) == 4
    assert all(0.0 <= value <= 1.0 for value in probabilities)
    assert set(predictions).issubset({0, 1})
    assert len(result["history"]) >= 1
