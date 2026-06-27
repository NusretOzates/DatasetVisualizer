"""Tests for Terminal-Bench 2.1 GitHub loader."""

from __future__ import annotations

import shutil
import tomllib
from pathlib import Path

import pandas as pd
import pytest

from dataset_visualizer.loaders import terminal_bench as terminal_module
from dataset_visualizer.loaders.terminal_bench import (
    _normalize_terminal_bench_frame,
    _parse_task_dir,
    load_terminal_bench_21,
)

SAMPLE_TASK_TOML = b"""
schema_version = "1.1"

[task]
name = "terminal-bench/sample-task"
description = "Fix async cancellation bug."

[metadata]
author_name = "Test Author"
difficulty = "medium"
category = "software-engineering"
expert_time_estimate_min = 60.0
junior_time_estimate_min = 240.0

[environment]
docker_image = "example/sample:20260101"
cpus = 2
memory_mb = 4096
allow_internet = true
"""


def _write_sample_task(task_root: Path) -> Path:
    task_dir = task_root / "sample-task"
    task_dir.mkdir(parents=True)
    (task_dir / "task.toml").write_bytes(SAMPLE_TASK_TOML)
    (task_dir / "instruction.md").write_text("Cancel pending async tasks safely.", encoding="utf-8")
    (task_dir / "README.md").write_text("# Sample task\n\nDetails here.", encoding="utf-8")
    return task_dir


def test_parse_task_dir_reads_instruction_and_metadata(tmp_path: Path) -> None:
    task_dir = _write_sample_task(tmp_path)
    row = _parse_task_dir(task_dir)
    assert row is not None
    assert row["task_id"] == "sample-task"
    assert row["category"] == "software-engineering"
    assert row["difficulty"] == "medium"
    assert "Cancel pending async tasks" in row["instruction"]
    assert row["allow_internet"] is True
    assert row["docker_image"] == "example/sample:20260101"


def test_normalize_terminal_bench_frame_casts_bools() -> None:
    raw = pd.DataFrame([{"allow_internet": None}])
    df = _normalize_terminal_bench_frame(raw)
    assert bool(df.loc[0, "allow_internet"]) is False


def test_load_terminal_bench_21_uses_cached_archive(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    upstream_tasks = tmp_path / "upstream_tasks"
    _write_sample_task(upstream_tasks)

    def _mock_download(cache_root: Path) -> Path:
        extracted = cache_root / terminal_module.EXTRACTED_DIR_NAME / "tasks"
        shutil.copytree(upstream_tasks / "sample-task", extracted / "sample-task")
        (cache_root / ".extracted").write_text("ok", encoding="utf-8")
        return extracted

    monkeypatch.setattr(terminal_module, "_download_tasks_archive", _mock_download)
    monkeypatch.setattr(terminal_module, "cache_dir", lambda _key: tmp_path / "cache")
    load_terminal_bench_21.clear()

    df = load_terminal_bench_21()
    assert len(df) == 1
    assert df.loc[0, "task_id"] == "sample-task"
    assert tomllib.loads(SAMPLE_TASK_TOML.decode())["task"]["name"] == df.loc[0, "task_name"]
