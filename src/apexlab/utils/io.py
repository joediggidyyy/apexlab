"""I/O helpers for ApexLab."""

from __future__ import annotations

import csv
from pathlib import Path


def read_single_column_csv(path: Path, *, encoding: str = "utf-8", delimiter: str = ",") -> list[str]:
	with path.open("r", encoding=encoding, newline="") as handle:
		rows = list(csv.reader(handle, delimiter=delimiter))

	if not rows:
		return []

	start = 1 if len(rows[0]) == 1 and len(rows) > 1 else 0
	output: list[str] = []
	for row in rows[start:]:
		if row:
			output.append(row[0].strip())
	return output
