from pathlib import Path

import pytest

from conftest import import_module_from_path


compare = import_module_from_path(
    "apexlab_compare_mod",
    Path(__file__).resolve().parents[1] / "src" / "apexlab" / "analysis" / "compare.py",
)


def test_summary_stats_returns_expected_core_fields() -> None:
    result = compare.summary_stats([1, 2, 3, 4])
    assert result["n"] == 4
    assert result["mean"] == pytest.approx(2.5)
    assert result["median"] == pytest.approx(2.5)
    assert result["min"] == pytest.approx(1.0)
    assert result["max"] == pytest.approx(4.0)
    assert "variance" in result
    assert "std" in result


def test_compare_distributions_handles_identical_samples() -> None:
    result = compare.compare_distributions([1, 2, 3], [1, 2, 3], label_a="lane_a", label_b="lane_b")
    assert result["direction"] == "lane_b_mean_eq_lane_a_mean"
    assert result["effect_size"]["cohens_d"]["cohens_d"] == pytest.approx(0.0)
    assert result["tests"]["ks_two_sample"]["d_statistic"] == pytest.approx(0.0)


def test_compare_distributions_detects_clear_separation() -> None:
    result = compare.compare_distributions([1, 1, 2, 2], [10, 11, 12, 13], label_a="baseline", label_b="candidate")
    assert result["direction"] == "candidate_mean_gt_baseline_mean"
    assert result["effect_size"]["cohens_d"]["cohens_d"] > 0.0
    assert result["tests"]["ks_two_sample"]["d_statistic"] > 0.0
    assert "candidate shows higher central tendency" in result["interpretation"]


def test_compare_helpers_support_uneven_sample_sizes() -> None:
    mw = compare.mann_whitney_u([1, 2, 3], [4, 5, 6, 7, 8])
    ks = compare.ks_two_sample([1, 2, 3], [4, 5, 6, 7, 8])
    wt = compare.welch_t_test([1, 2, 3], [4, 5, 6, 7, 8])
    assert mw["n_a"] == 3 and mw["n_b"] == 5
    assert ks["n_a"] == 3 and ks["n_b"] == 5
    assert wt["n_a"] == 3 and wt["n_b"] == 5


def test_mann_whitney_handles_ties() -> None:
    result = compare.mann_whitney_u([1, 2, 2, 3], [2, 2, 4, 5])
    assert 0.0 <= result["p_value"] <= 1.0
    assert result["u_statistic"] >= 0.0


def test_cohens_d_reports_effect_bucket() -> None:
    result = compare.cohens_d([1, 2, 3, 4], [5, 6, 7, 8])
    assert result["effect_bucket"] in {"negligible", "small", "medium", "large"}


def test_non_numeric_values_raise_clear_error() -> None:
    with pytest.raises(ValueError, match="Could not parse numeric value"):
        compare.summary_stats([1, "oops", 3])


def test_compare_distributions_returns_stable_top_level_schema() -> None:
    result = compare.compare_distributions([1, 2, 3], [3, 4, 5])
    assert sorted(result.keys()) == [
        "direction",
        "effect_size",
        "interpretation",
        "labels",
        "samples",
        "summary",
        "tests",
    ]
