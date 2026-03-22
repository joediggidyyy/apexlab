from pathlib import Path

import pytest

from conftest import import_module_from_path


thresholds = import_module_from_path(
    "apexlab_thresholds_mod",
    Path(__file__).resolve().parents[1] / "src" / "apexlab" / "evaluation" / "thresholds.py",
)


def test_select_lower_tail_threshold_targets_lower_scores() -> None:
    threshold = thresholds.select_lower_tail_threshold([0.1, 0.2, 0.8, 0.9], target_fpr=0.25)
    assert threshold == pytest.approx(0.2)


def test_evaluate_scores_supports_labeled_mode() -> None:
    scores = [0.1, 0.2, 0.8, 0.9]
    ids = ["a", "b", "c", "d"]
    labels = {"a": "0", "b": "0", "c": "1", "d": "1"}
    result = thresholds.evaluate_scores(scores, ids=ids, label_map=labels, positive_label="1", max_fpr=0.5)
    assert result.has_labels is True
    assert result.metrics["f1"] >= 0.0


def test_evaluate_scores_supports_unlabeled_mode() -> None:
    result = thresholds.evaluate_scores([0.1, 0.2, 0.8, 0.9], max_fpr=0.25)
    assert result.has_labels is False
    assert result.counts["total"] == 4
    assert result.metrics["flag_rate"] == pytest.approx(0.5)
