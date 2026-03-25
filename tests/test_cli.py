import importlib
import json
import sys
from pathlib import Path

import pytest


SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import apexlab

cli_main = importlib.import_module("apexlab.cli").main


def test_cli_help_renders_cleanly(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = cli_main([])
    captured = capsys.readouterr()
    assert exit_code == 1
    assert "ApexLab command-line toolkit" in captured.out
    assert "compare" in captured.out


@pytest.mark.parametrize("flag", ["--version", "-v"])
def test_cli_version_flags_render_package_version(flag: str, capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc_info:
        cli_main([flag])
    captured = capsys.readouterr()
    assert exc_info.value.code == 0
    assert captured.out.strip() == f"apexlab {apexlab.__version__}"


def test_compare_command_writes_report_bundle(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = cli_main(
        [
            "compare",
            "--sample-a",
            "1,2,3",
            "--sample-b",
            "4,5,6",
            "--label-a",
            "baseline",
            "--label-b",
            "candidate",
            "--out-dir",
            str(tmp_path),
            "--stem",
            "cmp",
        ]
    )
    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Wrote comparison report" in captured.out
    report_json = json.loads((tmp_path / "cmp.json").read_text(encoding="utf-8"))
    report_md = (tmp_path / "cmp.md").read_text(encoding="utf-8")
    assert report_json["task"] == "compare"
    assert report_json["comparison"]["direction"] == "candidate_mean_gt_baseline_mean"
    assert "Task: `compare`" in report_md
    assert "candidate_mean_gt_baseline_mean" in report_md


def test_report_command_rerenders_existing_json(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    report_input = tmp_path / "input.json"
    report_input.write_text(
        json.dumps(
            {
                "generated_at_utc": "2026-03-24T00:00:00Z",
                "task": "compare",
                "metrics": {"n_a": 3, "n_b": 3, "direction": "b_mean_gt_a_mean"},
                "comparison": {
                    "labels": {"a": "a", "b": "b"},
                    "samples": {"n_a": 3, "n_b": 3},
                    "summary": {"a": {"mean": 1.0}, "b": {"mean": 2.0}},
                    "tests": {"mann_whitney_u": {"statistic": 0.0, "p_value": 0.1}},
                    "effect_size": {"cohens_d": {"cohens_d": 0.8, "effect_bucket": "large"}},
                    "direction": "b_mean_gt_a_mean",
                    "interpretation": "b is higher than a.",
                },
            }
        ),
        encoding="utf-8",
    )
    output_dir = tmp_path / "rendered"
    exit_code = cli_main(["report", "--input", str(report_input), "--out-dir", str(output_dir), "--stem", "rerendered"])
    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Wrote report" in captured.out
    assert (output_dir / "rerendered.json").exists()
    assert (output_dir / "rerendered.md").exists()
