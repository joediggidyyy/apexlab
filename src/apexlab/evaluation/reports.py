"""Report helpers for ApexLab."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utc_now_iso() -> str:
	return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _as_dict(value: Any) -> dict[str, Any]:
	return value if isinstance(value, dict) else {}


def _format_scalar(value: Any) -> str:
	if value is None:
		return "n/a"
	if isinstance(value, bool):
		return "true" if value else "false"
	if isinstance(value, float):
		return f"{value:.6g}"
	return str(value)


def _append_table(lines: list[str], headers: list[str], rows: list[list[Any]]) -> None:
	lines.append("| " + " | ".join(headers) + " |")
	lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
	for row in rows:
		lines.append("| " + " | ".join(_format_scalar(cell) for cell in row) + " |")


def _render_compare_report(lines: list[str], report: dict[str, Any]) -> None:
	comparison = _as_dict(report.get("comparison"))
	labels = _as_dict(comparison.get("labels"))
	samples = _as_dict(comparison.get("samples"))
	summary = _as_dict(comparison.get("summary"))
	tests = _as_dict(comparison.get("tests"))
	effect = _as_dict(_as_dict(comparison.get("effect_size")).get("cohens_d"))
	interpretation = report.get("interpretation")
	interpretation_summary = (
		str(_as_dict(interpretation).get("summary", "")).strip()
		if isinstance(interpretation, dict)
		else str(comparison.get("interpretation", "")).strip()
	)
	flags = _as_dict(report.get("flags"))

	lines.extend(
		[
			"## Comparison overview",
			"",
			f"- **label_a**: {labels.get('a')}",
			f"- **label_b**: {labels.get('b')}",
			f"- **n_a**: {samples.get('n_a')}",
			f"- **n_b**: {samples.get('n_b')}",
			f"- **direction**: {comparison.get('direction')}",
			f"- **cohens_d**: {effect.get('cohens_d')}",
			f"- **effect_bucket**: {effect.get('effect_bucket')}",
			"",
		]
	)

	summary_a = _as_dict(summary.get("a"))
	summary_b = _as_dict(summary.get("b"))
	if summary_a or summary_b:
		lines.extend(["## Summary statistics", ""])
		_append_table(
			lines,
			["label", "n", "mean", "median", "std", "min", "max", "iqr"],
			[
				[
					labels.get("a"),
					summary_a.get("n"),
					summary_a.get("mean"),
					summary_a.get("median"),
					summary_a.get("std"),
					summary_a.get("min"),
					summary_a.get("max"),
					summary_a.get("iqr"),
				],
				[
					labels.get("b"),
					summary_b.get("n"),
					summary_b.get("mean"),
					summary_b.get("median"),
					summary_b.get("std"),
					summary_b.get("min"),
					summary_b.get("max"),
					summary_b.get("iqr"),
				],
			],
		)
		lines.append("")

	if tests:
		lines.extend(["## Statistical tests", ""])
		rows: list[list[Any]] = []
		for test_name, test_payload in tests.items():
			payload = _as_dict(test_payload)
			rows.append(
				[
					test_name,
					payload.get("statistic"),
					payload.get("p_value"),
					payload.get("notes"),
				]
			)
		_append_table(lines, ["test", "statistic", "p_value", "notes"], rows)
		lines.append("")

	if interpretation_summary:
		lines.extend(["## Interpretation", "", interpretation_summary, ""])

	if flags:
		lines.extend(["## Flags", ""])
		for key, value in flags.items():
			lines.append(f"- **{key}**: {_format_scalar(value)}")
		lines.append("")


def _render_regression_report(lines: list[str], report: dict[str, Any], metrics: dict[str, Any]) -> None:
	for key in ("n", "mae", "mse", "rmse", "r2", "log_loss", "accuracy", "positive_rate", "pseudo_r2"):
		if key in metrics:
			lines.append(f"- **{key}**: {metrics.get(key)}")
	coefficient_summary = report.get("coefficient_summary", [])
	if isinstance(coefficient_summary, list) and coefficient_summary:
		lines.extend(["", "## Coefficients", ""])
		rows: list[list[Any]] = []
		for row in coefficient_summary:
			if isinstance(row, dict):
				rows.append(
					[
						row.get("feature"),
						row.get("coefficient"),
						row.get("sign"),
						row.get("magnitude"),
						row.get("interpretation"),
					]
				)
		if rows:
			_append_table(lines, ["feature", "coefficient", "sign", "magnitude", "interpretation"], rows)
	if "converged" in report or "iterations" in report:
		lines.extend(["", "## Fit diagnostics", ""])
		if "model_type" in report:
			lines.append(f"- **model_type**: {report.get('model_type')}")
		if "converged" in report:
			lines.append(f"- **converged**: {_format_scalar(report.get('converged'))}")
		if "iterations" in report:
			lines.append(f"- **iterations**: {_format_scalar(report.get('iterations'))}")
		history = report.get("history", [])
		if isinstance(history, list) and history:
			lines.append(f"- **history_points**: {len(history)}")
			lines.append(f"- **final_history_value**: {_format_scalar(history[-1])}")


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
		_render_regression_report(lines, report, metrics)
	elif task == "compare":
		_render_compare_report(lines, report)
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
