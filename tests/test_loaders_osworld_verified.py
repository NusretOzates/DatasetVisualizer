"""Tests for the OSWorld-Verified GitHub loader."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from dataset_visualizer.loaders import osworld_verified as osworld_module
from dataset_visualizer.loaders.osworld_verified import _parse_task_file, load_osworld_verified

SAMPLE_TASK = {
    "id": "030eeff7-b492-4218-b312-701ec99ee0cc",
    "snapshot": "chrome",
    "instruction": "Enable Do Not Track in Chrome.",
    "source": "https://example.com/dnt",
    "config": [{"type": "launch", "parameters": {"command": ["google-chrome"]}}],
    "related_apps": ["chrome"],
    "evaluator": {"func": "exact_match", "expected": {"type": "enable_do_not_track"}},
}


def test_parse_task_file_reads_instruction_and_evaluator(tmp_path: Path) -> None:
    task_path = tmp_path / "chrome" / f"{SAMPLE_TASK['id']}.json"
    task_path.parent.mkdir(parents=True)
    task_path.write_text(json.dumps(SAMPLE_TASK), encoding="utf-8")

    row = _parse_task_file(task_path, "chrome")
    assert row is not None
    assert row["task_id"] == SAMPLE_TASK["id"]
    assert row["domain"] == "chrome"
    assert row["instruction"] == "Enable Do Not Track in Chrome."
    assert row["evaluator_func"] == "exact_match"
    assert row["config_step_count"] == 1
    assert row["related_apps"] == ["chrome"]


def test_load_osworld_verified_uses_cached_archive(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    extracted = tmp_path / osworld_module.EXTRACTED_DIR_NAME
    manifest = {"chrome": [SAMPLE_TASK["id"]]}
    (extracted / "evaluation_examples").mkdir(parents=True)
    (extracted / osworld_module.VERIFIED_MANIFEST).write_text(
        json.dumps(manifest), encoding="utf-8"
    )
    task_dir = extracted / osworld_module.EXAMPLES_ROOT / "chrome"
    task_dir.mkdir(parents=True)
    (task_dir / f"{SAMPLE_TASK['id']}.json").write_text(json.dumps(SAMPLE_TASK), encoding="utf-8")

    def _mock_download(cache_root: Path) -> Path:
        target = cache_root / osworld_module.EXTRACTED_DIR_NAME
        shutil.copytree(extracted, target, dirs_exist_ok=True)
        (cache_root / ".extracted").write_text("ok", encoding="utf-8")
        return target

    monkeypatch.setattr(osworld_module, "_download_osworld_archive", _mock_download)
    load_osworld_verified.clear()

    df = load_osworld_verified()
    assert len(df) == 1
    assert df.loc[0, "task_id"] == SAMPLE_TASK["id"]
