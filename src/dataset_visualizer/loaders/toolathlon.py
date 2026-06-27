"""Toolathlon loader (hkust-nlp/Toolathlon on GitHub)."""

from __future__ import annotations

import io
import json
import zipfile
from pathlib import Path
from typing import Any
from urllib.error import HTTPError
from urllib.request import urlopen

import pandas as pd

from dataset_visualizer.loaders.base import cache_dir
from dataset_visualizer.loaders.cache import loader_cache

TOOLATHLON_GITHUB_REPO = "hkust-nlp/Toolathlon"
TOOLATHLON_TRAJECTORIES_HF_ID = "hkust-nlp/Toolathlon-Trajectories"
TOOLATHLON_BRANCH = "main"
TOOLATHLON_ZIP_URL = (
    f"https://github.com/{TOOLATHLON_GITHUB_REPO}/archive/refs/heads/{TOOLATHLON_BRANCH}.zip"
)
EXTRACTED_DIR_NAME = f"Toolathlon-{TOOLATHLON_BRANCH}"
TASKS_ROOT = "tasks/finalpool"
TASK_CONFIG_NAME = "task_config.json"
TASK_DOC_CANDIDATES = ("docs/task.md", "docs/task_cn.md")


def _read_task_instruction(task_dir: Path) -> str:
    """Return the natural-language task prompt from docs/task.md when present."""
    for relative in TASK_DOC_CANDIDATES:
        doc_path = task_dir / relative
        if doc_path.is_file():
            return doc_path.read_text(encoding="utf-8").strip()
    return ""


def _parse_task_dir(task_dir: Path, pool: str) -> dict[str, Any] | None:
    """Parse one Toolathlon task directory into a normalized row."""
    config_path = task_dir / TASK_CONFIG_NAME
    if not config_path.is_file():
        return None

    raw = json.loads(config_path.read_text(encoding="utf-8"))
    task_name = task_dir.name
    mcp_servers = raw.get("needed_mcp_servers") or []
    local_tools = raw.get("needed_local_tools") or []
    if not isinstance(mcp_servers, list):
        mcp_servers = [str(mcp_servers)]
    if not isinstance(local_tools, list):
        local_tools = [str(local_tools)]

    instruction = _read_task_instruction(task_dir)
    mcp_servers = [str(server).strip() for server in mcp_servers if str(server).strip()]
    local_tools = [str(tool).strip() for tool in local_tools if str(tool).strip()]

    return {
        "task_id": task_name,
        "sample_id": task_name,
        "task_name": task_name,
        "task_pool": pool,
        "question": instruction,
        "instruction": instruction,
        "instruction_preview": instruction[:120],
        "needed_mcp_servers": mcp_servers,
        "needed_local_tools": local_tools,
        "mcp_server_count": len(mcp_servers),
        "local_tool_count": len(local_tools),
        "primary_mcp": mcp_servers[0] if mcp_servers else "",
        "split": pool,
    }


def _extracted_root(cache_root: Path) -> Path:
    return cache_root / EXTRACTED_DIR_NAME


def _download_toolathlon_archive(cache_root: Path) -> Path:
    """Download and extract the upstream Toolathlon repository archive."""
    extracted = _extracted_root(cache_root)
    tasks_root = extracted / TASKS_ROOT
    marker = cache_root / ".extracted"
    if marker.is_file() and tasks_root.is_dir():
        return extracted

    cache_root.mkdir(parents=True, exist_ok=True)
    try:
        with urlopen(TOOLATHLON_ZIP_URL, timeout=180) as response:
            archive_bytes = response.read()
    except HTTPError as exc:
        msg = f"Failed to download Toolathlon archive: HTTP {exc.code}"
        raise RuntimeError(msg) from exc

    with zipfile.ZipFile(io.BytesIO(archive_bytes)) as archive:
        archive.extractall(cache_root)

    if not tasks_root.is_dir():
        msg = f"Toolathlon archive missing tasks root at {tasks_root}"
        raise RuntimeError(msg)

    marker.write_text("ok", encoding="utf-8")
    return extracted


def _load_task_rows(extracted: Path) -> list[dict[str, Any]]:
    tasks_root = extracted / TASKS_ROOT
    pool = tasks_root.name
    rows: list[dict[str, Any]] = []
    for task_dir in sorted(tasks_root.iterdir()):
        if not task_dir.is_dir():
            continue
        row = _parse_task_dir(task_dir, pool)
        if row is not None:
            rows.append(row)
    return rows


@loader_cache(show_spinner="Downloading Toolathlon from GitHub …")
def load_toolathlon() -> pd.DataFrame:
    """Load Toolathlon final-pool agent tasks from the upstream GitHub repository.

    Returns:
        Normalized DataFrame with task prompts and required MCP/local tools.
    """
    cache_root = cache_dir("toolathlon")
    extracted = _download_toolathlon_archive(cache_root)
    rows = _load_task_rows(extracted)
    if not rows:
        msg = "No Toolathlon tasks found in the downloaded archive"
        raise RuntimeError(msg)
    return pd.DataFrame(rows)
