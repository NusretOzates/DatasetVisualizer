"""Tests for the OSWorld V2.1 release-manifest loader."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from dataset_visualizer.loaders import osworld_v2 as osworld_module
from dataset_visualizer.loaders.osworld_v2 import _load_rows, load_osworld_v21


def _write_release_manifest(root: Path) -> None:
    manifest_dir = root / "benchmark_releases"
    manifest_dir.mkdir(parents=True)
    (manifest_dir / "osworld-v2.1.json").write_text(
        json.dumps({"release": "osworld-v2.1", "tasks": {"commit": "abc123"}}),
        encoding="utf-8",
    )
    (manifest_dir / "osworld-v2.1.task_hashes.json").write_text(
        json.dumps(
            {
                "files": {
                    "task_002.py": {"sha256": "def", "size": 20},
                    "task_001.py": {"sha256": "abc", "size": 10},
                }
            }
        ),
        encoding="utf-8",
    )


def test_load_rows_sorts_tasks_and_reads_revision(tmp_path: Path) -> None:
    _write_release_manifest(tmp_path)

    rows = _load_rows(tmp_path)

    assert [row["task_id"] for row in rows] == ["task_001", "task_002"]
    assert rows[0]["sha256"] == "abc"
    assert rows[0]["file_size_bytes"] == 10
    assert rows[0]["source_revision"] == "abc123"


def test_load_osworld_v21_uses_cached_archive(tmp_path: Path, monkeypatch) -> None:
    upstream = tmp_path / "upstream"
    _write_release_manifest(upstream)

    def _mock_download(cache_root: Path) -> Path:
        extracted = cache_root / osworld_module.EXTRACTED_DIR_NAME
        shutil.copytree(upstream, extracted, dirs_exist_ok=True)
        (cache_root / ".extracted").write_text("ok", encoding="utf-8")
        return extracted

    monkeypatch.setattr(osworld_module, "_download_release_archive", _mock_download)
    monkeypatch.setattr(osworld_module, "cache_dir", lambda _key: tmp_path / "cache")
    load_osworld_v21.clear()

    df = load_osworld_v21()
    assert len(df) == 2
    assert df.loc[0, "task_id"] == "task_001"
