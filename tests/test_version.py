import re
from pathlib import Path

import apexlab


def test_package_root_exports_release_version_and_core_symbol() -> None:
    assert apexlab.__version__ == "1.0.0"
    assert "ApexRegressor" in apexlab.__all__


def test_pyproject_version_matches_package_version() -> None:
    pyproject_path = Path(__file__).resolve().parents[1] / "pyproject.toml"
    content = pyproject_path.read_text(encoding="utf-8")
    match = re.search(r'^version\s*=\s*"([^"]+)"', content, re.MULTILINE)
    assert match is not None
    assert match.group(1) == apexlab.__version__
