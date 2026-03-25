"""Command-line entry point for ApexLab."""

from __future__ import annotations

import argparse
from typing import Sequence

from .compare import add_compare_subparser
from .report import add_report_subparser


def build_parser() -> argparse.ArgumentParser:
	parser = argparse.ArgumentParser(prog="apexlab", description="ApexLab command-line toolkit")
	subparsers = parser.add_subparsers(dest="command")
	add_compare_subparser(subparsers)
	add_report_subparser(subparsers)
	return parser


def main(argv: Sequence[str] | None = None) -> int:
	parser = build_parser()
	args = parser.parse_args(list(argv) if argv is not None else None)
	if not hasattr(args, "func"):
		parser.print_help()
		return 1
	return int(args.func(args))


if __name__ == "__main__":
	raise SystemExit(main())
