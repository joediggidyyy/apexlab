"""Report command for ApexLab."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from apexlab.evaluation.reports import write_reports


def add_report_subparser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
	parser = subparsers.add_parser("report", help="Render Markdown and JSON artifacts from an ApexLab report JSON file")
	parser.add_argument("--input", required=True, type=Path, help="Path to an existing ApexLab report JSON file")
	parser.add_argument("--out-dir", type=Path, help="Optional output directory; defaults to the input file's directory")
	parser.add_argument("--stem", help="Optional output filename stem; defaults to the input file's stem")
	parser.set_defaults(func=run_report)


def run_report(args: argparse.Namespace) -> int:
	input_path = Path(args.input)
	if not input_path.exists():
		raise ValueError(f"Report input not found: {input_path}")
	report = json.loads(input_path.read_text(encoding="utf-8"))
	out_dir = args.out_dir or input_path.parent
	stem = args.stem or input_path.stem
	paths = write_reports(report, out_dir, stem=str(stem))
	print(f"Wrote report to {paths['json']} and {paths['markdown']}")
	return 0
