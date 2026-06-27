"""Tests for the Toolathlon GitHub loader."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from dataset_visualizer.loaders import toolathlon as toolathlon_module
from dataset_visualizer.loaders.toolathlon import _parse_task_dir, load_toolathlon

SAMPLE_TASK_CONFIG = {
    "needed_mcp_servers": ["filesystem", "terminal"],
    "needed_local_tools": ["web_search", "claim_done"],
    "meta": {},
}
SAMPLE_TASK_MD = "Plan a round-trip train itinerary and write the result to JSON."


def test_parse_task_dir_reads_instruction_and_tools(tmp_path: Path) -> None:
    task_dir = tmp_path / "train-ticket-plan"
    docs_dir = task_dir / "docs"
    docs_dir.mkdir(parents=True)
    (task_dir / "task_config.json").write_text(json.dumps(SAMPLE_TASK_CONFIG), encoding="utf-8")
    (docs_dir / "task.md").write_text(SAMPLE_TASK_MD, encoding="utf-8")

    row = _parse_task_dir(task_dir, "finalpool")
    assert row is not None
    assert row["task_id"] == "train-ticket-plan"
    assert row["instruction"] == SAMPLE_TASK_MD
    assert row["needed_mcp_servers"] == ["filesystem", "terminal"]
    assert row["needed_local_tools"] == ["web_search", "claim_done"]
    assert row["primary_mcp"] == "filesystem"
    assert row["mcp_server_count"] == 2
    assert row["local_tool_count"] == 2


def test_load_toolathlon_uses_cached_archive(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    extracted = tmp_path / toolathlon_module.EXTRACTED_DIR_NAME
    task_dir = extracted / toolathlon_module.TASKS_ROOT / "demo-task"
    docs_dir = task_dir / "docs"
    docs_dir.mkdir(parents=True)
    (task_dir / "task_config.json").write_text(json.dumps(SAMPLE_TASK_CONFIG), encoding="utf-8")
    (docs_dir / "task.md").write_text(SAMPLE_TASK_MD, encoding="utf-8")
    (tmp_path / ".extracted").write_text("ok", encoding="utf-8")

    monkeypatch.setattr(toolathlon_module, "cache_dir", lambda _key: tmp_path)
    load_toolathlon.clear()

    df = load_toolathlon()
    assert len(df) == 1
    assert df.loc[0, "task_name"] == "demo-task"
    assert df.loc[0, "question"] == SAMPLE_TASK_MD
