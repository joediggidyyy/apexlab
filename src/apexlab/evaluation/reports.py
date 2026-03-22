"""Report helpers for ApexLab."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utc_now_iso() -> str:
	return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def render_markdown_report(report: dict[str, Any]) -> str:
	task = str(report.get("task", "")).strip().lower()
	metrics = report.get("metrics", {}) if isinstance(report.get("metrics", {}), dict) else {}

	lines = [
		"# ApexLab Evaluation Report",
		"",
		f"Generated: `{report.get('generated_at_utc', '')}`",
		f"Task: `{task}`",
		"",
		"## Metrics",
		"",
	]

	if task == "regression":
		for key in ("n", "mae", "mse", "rmse", "r2"):
			lines.append(f"- **{key}**: {metrics.get(key)}")
	elif task == "classification":
		lines.append(f"- **n**: {metrics.get('n')}")
		lines.append(f"- **accuracy**: {metrics.get('accuracy')}")
		labels = metrics.get("labels", [])
		cm = metrics.get("confusion_matrix", [])
		if labels and cm:
			lines.extend(["", "## Confusion matrix", ""])
			lines.append("| true\\pred | " + " | ".join(str(x) for x in labels) + " |")
			lines.append("|---|" + "|".join(["---"] * len(labels)) + "|")
			for idx, row in enumerate(cm):
				lines.append("| " + str(labels[idx]) + " | " + " | ".join(str(x) for x in row) + " |")
	lines.append("")
	return "\n".join(lines)


def write_reports(report: dict[str, Any], out_dir: Path, *, stem: str = "report") -> dict[str, Path]:
	out_dir.mkdir(parents=True, exist_ok=True)
	json_path = out_dir / f"{stem}.json"
	md_path = out_dir / f"{stem}.md"
	json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
	md_path.write_text(render_markdown_report(report), encoding="utf-8")
	return {"json": json_path, "markdown": md_path}
