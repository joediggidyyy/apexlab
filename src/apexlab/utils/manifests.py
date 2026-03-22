"""Manifest helpers for ApexLab."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def write_manifest(path: Path, payload: dict[str, Any]) -> Path:
	path.parent.mkdir(parents=True, exist_ok=True)
	path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
	return path


def read_manifest(path: Path) -> dict[str, Any]:
	return json.loads(path.read_text(encoding="utf-8"))
