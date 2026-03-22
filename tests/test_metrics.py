import pytest

from apexlab.evaluation.metrics import classification_metrics, regression_metrics


def test_regression_metrics_computes_expected_values() -> None:
    result = regression_metrics([1.0, 2.0, 3.0], [1.0, 2.0, 4.0])
    assert result["n"] == 3
    assert result["mae"] == pytest.approx(1.0 / 3.0)
    assert result["mse"] == pytest.approx(1.0 / 3.0)
    assert result["rmse"] == pytest.approx((1.0 / 3.0) ** 0.5)


def test_classification_metrics_computes_accuracy_and_matrix() -> None:
    result = classification_metrics(["a", "b", "a", "b"], ["a", "a", "a", "b"])
    assert result["n"] == 4
    assert result["accuracy"] == pytest.approx(0.75)
    assert result["labels"] == ["a", "b"]
    assert result["confusion_matrix"] == [[2, 0], [1, 1]]
