from __future__ import annotations

import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
	sys.path.insert(0, str(SRC_ROOT))

from apexlab.evaluation import (
	classification_metrics,
	evaluate_scores,
	regression_metrics,
	render_markdown_report,
	utc_now_iso,
	write_reports,
)


def main() -> None:
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

	with tempfile.TemporaryDirectory() as tmp_dir:
		paths = write_reports(report, Path(tmp_dir), stem="classification_demo")
		markdown_preview = render_markdown_report(report)
		print("ApexLab evaluation demo")
		print(f"regression metrics: {regression}")
		print(f"classification accuracy: {classification['accuracy']}")
		print(f"threshold result: {threshold_result}")
		print(f"report outputs: {paths}")
		print("markdown preview:")
		print(markdown_preview)


if __name__ == "__main__":
	main()
