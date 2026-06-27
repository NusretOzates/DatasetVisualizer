"""OSWorld-Verified loader (xlang-ai/OSWorld on GitHub)."""

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

OSWORLD_GITHUB_REPO = "xlang-ai/OSWorld"
OSWORLD_WEBSITE_URL = "https://os-world.github.io/"
OSWORLD_BRANCH = "main"
OSWORLD_ZIP_URL = (
    f"https://github.com/{OSWORLD_GITHUB_REPO}/archive/refs/heads/{OSWORLD_BRANCH}.zip"
)
EXTRACTED_DIR_NAME = f"OSWorld-{OSWORLD_BRANCH}"
VERIFIED_MANIFEST = "evaluation_examples/test_nogdrive.json"
EXAMPLES_ROOT = "evaluation_examples/examples"


def _parse_task_file(task_path: Path, domain: str) -> dict[str, Any] | None:
    """Parse one OSWorld evaluation example JSON into a normalized row."""
    if not task_path.is_file():
        return None

    raw = json.loads(task_path.read_text(encoding="utf-8"))
    task_id = str(raw.get("id", task_path.stem)).strip()
    instruction = str(raw.get("instruction", "")).strip()
    evaluator = raw.get("evaluator")
    evaluator_func = ""
    if isinstance(evaluator, dict):
        evaluator_func = str(evaluator.get("func", "")).strip()

    related_apps = raw.get("related_apps") or []
    if not isinstance(related_apps, list):
        related_apps = [str(related_apps)]

    config = raw.get("config") or []
    config_steps = len(config) if isinstance(config, list) else 0

    return {
        "task_id": task_id,
        "instance_id": task_id,
        "domain": domain,
        "snapshot": str(raw.get("snapshot", "")).strip(),
        "instruction": instruction,
        "instruction_preview": instruction[:120],
        "source": str(raw.get("source", "")).strip(),
        "related_apps": [str(app) for app in related_apps],
        "config": config if isinstance(config, list) else [],
        "config_step_count": config_steps,
        "evaluator": evaluator if isinstance(evaluator, dict) else {},
        "evaluator_func": evaluator_func,
        "trajectory": str(raw.get("trajectory", "")).strip(),
        "proxy": bool(raw.get("proxy", False)),
        "fixed_ip": bool(raw.get("fixed_ip", False)),
        "possibility_of_env_change": str(raw.get("possibility_of_env_change", "")).strip(),
        "split": "verified",
    }


def _extracted_root(cache_root: Path) -> Path:
    return cache_root / EXTRACTED_DIR_NAME


def _download_osworld_archive(cache_root: Path) -> Path:
    """Download and extract the upstream OSWorld repository archive."""
    extracted = _extracted_root(cache_root)
    manifest_path = extracted / VERIFIED_MANIFEST
    marker = cache_root / ".extracted"
    if marker.is_file() and manifest_path.is_file():
        return extracted

    cache_root.mkdir(parents=True, exist_ok=True)
    try:
        with urlopen(OSWORLD_ZIP_URL, timeout=180) as response:
            archive_bytes = response.read()
    except HTTPError as exc:
        msg = f"Failed to download OSWorld archive: HTTP {exc.code}"
        raise RuntimeError(msg) from exc

    with zipfile.ZipFile(io.BytesIO(archive_bytes)) as archive:
        archive.extractall(cache_root)

    if not manifest_path.is_file():
        msg = f"OSWorld archive missing verified manifest at {manifest_path}"
        raise RuntimeError(msg)

    marker.write_text("ok", encoding="utf-8")
    return extracted


def _load_verified_rows(extracted: Path) -> list[dict[str, Any]]:
    manifest_path = extracted / VERIFIED_MANIFEST
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(manifest, dict):
        msg = f"Expected domain mapping in {manifest_path}"
        raise RuntimeError(msg)

    examples_root = extracted / EXAMPLES_ROOT
    rows: list[dict[str, Any]] = []
    for domain, task_ids in manifest.items():
        if not isinstance(task_ids, list):
            continue
        for task_id in task_ids:
            task_path = examples_root / str(domain) / f"{task_id}.json"
            row = _parse_task_file(task_path, str(domain))
            if row is not None:
                rows.append(row)
    return rows


@loader_cache(show_spinner="Downloading OSWorld-Verified from GitHub …")
def load_osworld_verified() -> pd.DataFrame:
    """Load OSWorld-Verified GUI agent tasks from the upstream GitHub repository.

    Returns:
        Normalized task DataFrame for the ``test_nogdrive`` verified suite (361 tasks).
    """
    cache_root = cache_dir("osworld_verified")
    extracted = _download_osworld_archive(cache_root)
    rows = _load_verified_rows(extracted)
    if not rows:
        msg = "No OSWorld-Verified tasks found in the downloaded archive"
        raise RuntimeError(msg)
    return pd.DataFrame(rows)
