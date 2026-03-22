from pathlib import Path

from apexlab.utils.manifests import read_manifest, write_manifest


def test_write_and_read_manifest_round_trip(tmp_path: Path) -> None:
    path = tmp_path / "manifest.json"
    payload = {"name": "apexlab", "version": 1}
    write_manifest(path, payload)
    assert read_manifest(path) == payload
