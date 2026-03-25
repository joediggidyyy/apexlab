import json
import sys
from pathlib import Path


SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
	sys.path.insert(0, str(SRC))

from apexlab.analysis.compare import compare_distributions
from apexlab.evaluation.compare_report import build_compare_report
from apexlab.evaluation.reports import render_markdown_report, write_reports


def test_build_compare_report_returns_stable_top_level_schema() -> None:
	comparison = compare_distributions([1, 2, 3], [5, 6, 7], label_a="baseline", label_b="candidate")
	report = build_compare_report(comparison, generated_at_utc="2026-03-24T00:00:00Z")
	assert sorted(report.keys()) == [
		"code",
		"comparison",
		"context",
		"flags",
		"generated_at_utc",
		"identity",
		"inputs",
		"interpretation",
		"metrics",
		"task",
	]
	assert report["task"] == "compare"
	assert report["identity"]["schema_version"] == "1.0"
	assert report["flags"]["recommended_action"]


def test_build_compare_report_sets_small_sample_caution_flag() -> None:
	comparison = compare_distributions([1, 2, 3], [10, 11, 12], label_a="a", label_b="b")
	report = build_compare_report(comparison, generated_at_utc="2026-03-24T00:00:00Z")
	assert report["flags"]["small_sample_caution"] is True
	assert report["flags"]["p_value_supports_difference"] is True


def test_render_markdown_report_for_compare_includes_tables_and_flags() -> None:
	comparison = compare_distributions([1, 1, 2, 2], [10, 11, 12, 13], label_a="baseline", label_b="candidate")
	report = build_compare_report(comparison, generated_at_utc="2026-03-24T00:00:00Z")
	markdown = render_markdown_report(report)
	assert "## Summary statistics" in markdown
	assert "## Statistical tests" in markdown
	assert "## Flags" in markdown
	assert "candidate" in markdown
	assert "mann_whitney_u" in markdown


def test_render_markdown_report_for_regression_includes_coefficients_and_diagnostics() -> None:
	report = {
		"generated_at_utc": "2026-03-24T00:00:00Z",
		"task": "regression",
		"metrics": {"n": 4, "mae": 0.1, "mse": 0.02, "rmse": 0.141, "r2": 0.98},
		"model_type": "ols",
		"converged": True,
		"iterations": 12,
		"history": [0.5, 0.25, 0.1],
		"coefficient_summary": [
			{
				"feature": "intercept",
				"coefficient": 1.0,
				"sign": "positive",
				"magnitude": 1.0,
				"interpretation": "positive association with outcome",
			}
		],
	}
	markdown = render_markdown_report(report)
	assert "## Coefficients" in markdown
	assert "## Fit diagnostics" in markdown
	assert "history_points" in markdown


def test_write_reports_persists_compare_report_bundle(tmp_path: Path) -> None:
	comparison = compare_distributions([1, 2, 3], [4, 5, 6], label_a="baseline", label_b="candidate")
	report = build_compare_report(comparison, generated_at_utc="2026-03-24T00:00:00Z")
	paths = write_reports(report, tmp_path, stem="compare_frame6")
	stored = json.loads(paths["json"].read_text(encoding="utf-8"))
	markdown = paths["markdown"].read_text(encoding="utf-8")
	assert stored["flags"]["consistent_directionality"] is True
	assert "recommended_action" in markdown