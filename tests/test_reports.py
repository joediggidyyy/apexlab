from pathlib import Path

from apexlab.evaluation.reports import render_markdown_report, utc_now_iso, write_reports


def test_utc_now_iso_uses_utc_z_suffix() -> None:
    stamp = utc_now_iso()
    assert stamp.endswith("Z")
    assert "T" in stamp


def test_render_markdown_report_includes_classification_matrix() -> None:
    report = {
        "generated_at_utc": "2026-03-22T00:00:00Z",
        "task": "classification",
        "metrics": {
            "n": 4,
            "accuracy": 0.75,
            "labels": ["a", "b"],
            "confusion_matrix": [[2, 0], [1, 1]],
        },
    }

    rendered = render_markdown_report(report)

    assert "# ApexLab Evaluation Report" in rendered
    assert "Task: `classification`" in rendered
    assert "## Confusion matrix" in rendered
    assert "| true\\pred | a | b |" in rendered


def test_render_markdown_report_supports_compare_reports() -> None:
    report = {
        "generated_at_utc": "2026-03-24T00:00:00Z",
        "task": "compare",
        "comparison": {
            "labels": {"a": "baseline", "b": "candidate"},
            "samples": {"n_a": 3, "n_b": 3},
            "tests": {"mann_whitney_u": {"statistic": 0.0, "p_value": 0.1}},
            "effect_size": {"cohens_d": {"cohens_d": 0.8, "effect_bucket": "large"}},
            "direction": "candidate_mean_gt_baseline_mean",
            "interpretation": "Candidate trends higher than baseline.",
        },
    }

    rendered = render_markdown_report(report)

    assert "Task: `compare`" in rendered
    assert "## Interpretation" in rendered
    assert "candidate_mean_gt_baseline_mean" in rendered
    assert "## Statistical tests" in rendered


def test_write_reports_writes_json_and_markdown_files(tmp_path: Path) -> None:
    report = {
        "generated_at_utc": "2026-03-22T00:00:00Z",
        "task": "regression",
        "metrics": {
            "n": 3,
            "mae": 0.1,
            "mse": 0.02,
            "rmse": 0.1414213562,
            "r2": 0.98,
        },
    }

    paths = write_reports(report, tmp_path, stem="demo_report")

    assert paths["json"] == tmp_path / "demo_report.json"
    assert paths["markdown"] == tmp_path / "demo_report.md"
    assert paths["json"].read_text(encoding="utf-8").startswith("{")
    markdown = paths["markdown"].read_text(encoding="utf-8")
    assert "Task: `regression`" in markdown
    assert "- **rmse**: 0.1414213562" in markdown
