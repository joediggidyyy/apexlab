"""Compare command for ApexLab."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Sequence

from apexlab.analysis import compare_distributions
from apexlab.evaluation.compare_report import build_compare_report
from apexlab.evaluation.reports import write_reports


def _parse_numeric_text(values: str, *, name: str) -> list[float]:
	items = [item.strip() for item in str(values).split(",") if item.strip()]
	if not items:
		raise ValueError(f"{name} must contain at least one numeric value")
	out: list[float] = []
	for index, item in enumerate(items, start=1):
		try:
			out.append(float(item))
		except Exception as exc:
			raise ValueError(f"Could not parse numeric value in {name} at position {index}: {item!r}") from exc
	return out


def _read_numeric_file(path: Path, *, column: str | None = None) -> list[float]:
	if not path.exists():
		raise ValueError(f"Input file not found: {path}")
	if path.suffix.lower() == ".json":
		payload = json.loads(path.read_text(encoding="utf-8"))
		if isinstance(payload, list):
			return [float(value) for value in payload]
		if isinstance(payload, dict) and column:
			payload_value = payload.get(column)
			if isinstance(payload_value, list):
				return [float(value) for value in payload_value]
			raise ValueError(f"Column {column!r} was not found as a list in {path}")
		raise ValueError("JSON input must be a list of numbers or a dict containing a list under --metric")
	if path.suffix.lower() in {".txt", ".log"}:
		lines = [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
		return [float(line) for line in lines]
	with path.open("r", encoding="utf-8", newline="") as handle:
		if column:
			reader = csv.DictReader(handle)
			if not reader.fieldnames or column not in reader.fieldnames:
				raise ValueError(f"Column {column!r} not found in CSV headers for {path}")
			return [float(row[column]) for row in reader if row.get(column, "").strip() != ""]
		reader = csv.reader(handle)
		values: list[float] = []
		for row_index, row in enumerate(reader, start=1):
			if not row:
				continue
			cell = row[0].strip()
			if cell == "":
				continue
			try:
				values.append(float(cell))
			except Exception:
				if row_index == 1:
					continue
				raise ValueError(f"Could not parse numeric value from {path} row {row_index}: {cell!r}")
		if not values:
			raise ValueError(f"No numeric values were found in {path}")
		return values


def _resolve_sample(
	inline_values: str | None,
	file_path: str | None,
	*,
	column: str | None,
	name: str,
) -> list[float]:
	if inline_values:
		return _parse_numeric_text(inline_values, name=name)
	if file_path:
		return _read_numeric_file(Path(file_path), column=column)
	raise ValueError(f"One of --{name.replace('_', '-')} or --{name.replace('_', '-')}-file is required")


def add_compare_subparser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
	parser = subparsers.add_parser("compare", help="Compare two numeric samples and emit a report")
	parser.add_argument("--sample-a", help="Comma-separated numeric values for sample A")
	parser.add_argument("--sample-b", help="Comma-separated numeric values for sample B")
	parser.add_argument("--sample-a-file", help="Path to sample A values (.json, .csv, .txt)")
	parser.add_argument("--sample-b-file", help="Path to sample B values (.json, .csv, .txt)")
	parser.add_argument("--metric", help="Optional column/key name when reading structured file inputs")
	parser.add_argument("--label-a", default="lane_a", help="Display label for sample A")
	parser.add_argument("--label-b", default="lane_b", help="Display label for sample B")
	parser.add_argument("--out-dir", type=Path, help="Optional directory for report artifacts")
	parser.add_argument("--stem", default="compare_report", help="Report filename stem when writing artifacts")
	parser.set_defaults(func=run_compare)


def run_compare(args: argparse.Namespace) -> int:
	sample_a = _resolve_sample(args.sample_a, args.sample_a_file, column=args.metric, name="sample_a")
	sample_b = _resolve_sample(args.sample_b, args.sample_b_file, column=args.metric, name="sample_b")
	comparison = compare_distributions(sample_a, sample_b, label_a=args.label_a, label_b=args.label_b)
	report = build_compare_report(
		comparison,
		inputs={
			"sample_a_source": "inline" if args.sample_a else args.sample_a_file,
			"sample_b_source": "inline" if args.sample_b else args.sample_b_file,
			"metric": args.metric,
		},
		context={"command": "apexlab compare"},
	)
	if args.out_dir is not None:
		paths = write_reports(report, args.out_dir, stem=str(args.stem))
		print(f"Wrote comparison report to {paths['json']} and {paths['markdown']}")
	else:
		print(json.dumps(report, ensure_ascii=True, indent=2))
	return 0
