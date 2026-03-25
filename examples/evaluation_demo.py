from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
	sys.path.insert(0, str(SRC_ROOT))

from apexlab.analysis import compare_distributions, logistic_fit, ols_fit, summarize_coefficients
from apexlab.cli.main import main as cli_main
from apexlab.evaluation import (
	classification_metrics,
	evaluate_scores,
	regression_metrics,
	render_markdown_report,
	utc_now_iso,
	write_reports,
)


def main() -> None:
	# Leg 1 evaluation surfaces
	regression = regression_metrics([1.0, 2.0, 3.0, 4.0], [1.1, 1.9, 2.8, 4.2])
	classification = classification_metrics(
		["cat", "dog", "cat", "fox", "dog"],
		["cat", "dog", "fox", "fox", "dog"],
	)
	threshold_result = evaluate_scores(
		[0.95, 0.75, 0.2, 0.15, 0.85],
		ids=["a", "b", "c", "d", "e"],
		label_map={"a": "1", "b": "1", "c": "0", "d": "0", "e": "1"},
		positive_label="1",
		max_fpr=0.25,
	)

	report = {
		"generated_at_utc": utc_now_iso(),
		"task": "classification",
		"metrics": classification,
	}

	# Leg 2 analysis surfaces
	comparison = compare_distributions([0.1, 0.2, 0.25, 0.3], [0.6, 0.7, 0.8, 0.9], label_a="baseline", label_b="candidate")
	ols_result = ols_fit([[1.0], [2.0], [3.0], [4.0]], [3.0, 5.0, 7.0, 9.0])
	logistic_result = logistic_fit(
		[[0.0], [1.0], [2.0], [3.0], [4.0], [5.0]],
		[0, 0, 0, 1, 1, 1],
		learning_rate=0.2,
		max_iter=4000,
		tol=1e-7,
	)
	coefficient_summary = summarize_coefficients(logistic_result["coefficients"], feature_names=["signal"])
	compare_report = {
		"generated_at_utc": utc_now_iso(),
		"task": "compare",
		"metrics": {
			"n_a": comparison["samples"]["n_a"],
			"n_b": comparison["samples"]["n_b"],
			"direction": comparison["direction"],
		},
		"comparison": comparison,
	}

	with tempfile.TemporaryDirectory() as tmp_dir:
		tmp_path = Path(tmp_dir)
		paths = write_reports(report, tmp_path, stem="classification_demo")
		compare_paths = write_reports(compare_report, tmp_path, stem="compare_demo")
		cli_compare_out = tmp_path / "cli_compare"
		cli_report_out = tmp_path / "cli_report"
		cli_compare_exit = cli_main(
			[
				"compare",
				"--sample-a",
				"0.1,0.2,0.25,0.3",
				"--sample-b",
				"0.6,0.7,0.8,0.9",
				"--label-a",
				"baseline",
				"--label-b",
				"candidate",
				"--out-dir",
				str(cli_compare_out),
				"--stem",
				"wet_compare",
			]
		)
		cli_report_input = cli_compare_out / "wet_compare.json"
		cli_report_exit = cli_main(
			[
				"report",
				"--input",
				str(cli_report_input),
				"--out-dir",
				str(cli_report_out),
				"--stem",
				"wet_rerendered",
			]
		)
		markdown_preview = render_markdown_report(report)
		print("ApexLab wet test (Leg 1 + Leg 2 lite)")
		print(f"regression metrics: {regression}")
		print(f"classification accuracy: {classification['accuracy']}")
		print(f"threshold result: {threshold_result}")
		print(f"comparison direction: {comparison['direction']}")
		print(f"ols coefficients: {ols_result['coefficients']}")
		print(f"logistic metrics: {logistic_result['metrics']}")
		print(f"logistic coefficient summary: {coefficient_summary}")
		print(f"classification report outputs: {paths}")
		print(f"compare report outputs: {compare_paths}")
		print(f"cli compare exit: {cli_compare_exit}")
		print(f"cli report exit: {cli_report_exit}")
		print(f"cli compare report json exists: {(cli_compare_out / 'wet_compare.json').exists()}")
		print(f"cli rerendered markdown exists: {(cli_report_out / 'wet_rerendered.md').exists()}")
		print("cli compare json preview:")
		print(json.loads((cli_compare_out / "wet_compare.json").read_text(encoding="utf-8")))
		print("markdown preview:")
		print(markdown_preview)


if __name__ == "__main__":
	main()
