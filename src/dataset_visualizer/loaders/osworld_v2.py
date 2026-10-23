"""OSWorld V2.1 loader (xlang-ai/OSWorld-V2 release manifest on GitHub).

The 108 task implementation classes are distributed through the gated
Hugging Face dataset ``xlangai/osworld_v2_tasks`` to reduce benchmark
leakage, so this loader catalogs the public ``osworld-v2.1`` release
manifest: one row per task file with its pinned SHA-256 and size.
"""

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

OSWORLD_V2_GITHUB_REPO = "xlang-ai/OSWorld-V2"
OSWORLD_V2_RELEASE = "osworld-v2.1"
OSWORLD_V2_ZIP_URL = (
    f"https://github.com/{OSWORLD_V2_GITHUB_REPO}/archive/refs/tags/{OSWORLD_V2_RELEASE}.zip"
)
EXTRACTED_DIR_NAME = f"OSWorld-V2-{OSWORLD_V2_RELEASE}"
RELEASE_MANIFEST = f"benchmark_releases/{OSWORLD_V2_RELEASE}.json"
TASK_HASH_MANIFEST = f"benchmark_releases/{OSWORLD_V2_RELEASE}.task_hashes.json"
TASKS_HF_ID = "xlangai/osworld_v2_tasks"


def _download_release_archive(cache_root: Path) -> Path:
    """Download and extract the public OSWorld-V2 release archive."""
    extracted = cache_root / EXTRACTED_DIR_NAME
    manifest_path = extracted / TASK_HASH_MANIFEST
    marker = cache_root / ".extracted"
    if marker.is_file() and manifest_path.is_file():
        return extracted

    cache_root.mkdir(parents=True, exist_ok=True)
    try:
        with urlopen(OSWORLD_V2_ZIP_URL, timeout=180) as response:
            archive_bytes = response.read()
    except HTTPError as exc:
        msg = f"Failed to download OSWorld V2 archive: HTTP {exc.code}"
        raise RuntimeError(msg) from exc

    with zipfile.ZipFile(io.BytesIO(archive_bytes)) as archive:
        archive.extractall(cache_root)

    if not manifest_path.is_file():
        msg = f"OSWorld V2 archive missing task hash manifest at {manifest_path}"
        raise RuntimeError(msg)

    marker.write_text("ok", encoding="utf-8")
    return extracted


def _load_rows(extracted: Path) -> list[dict[str, Any]]:
    """Build one catalog row per task file in the release hash manifest."""
    release_path = extracted / RELEASE_MANIFEST
    release: dict[str, Any] = {}
    if release_path.is_file():
        parsed = json.loads(release_path.read_text(encoding="utf-8"))
        if isinstance(parsed, dict):
            release = parsed

    tasks_meta = release.get("tasks") or {}
    source_revision = ""
    if isinstance(tasks_meta, dict):
        source_revision = str(tasks_meta.get("commit") or "")

    hashes = json.loads((extracted / TASK_HASH_MANIFEST).read_text(encoding="utf-8"))
    files = hashes.get("files") or {}
    if not isinstance(files, dict):
        msg = f"Expected file mapping in {TASK_HASH_MANIFEST}"
        raise RuntimeError(msg)

    rows: list[dict[str, Any]] = []
    for filename in sorted(files):
        entry = files[filename] or {}
        task_id = Path(filename).stem
        rows.append(
            {
                "task_id": task_id,
                "instance_id": task_id,
                "task_file": filename,
                "sha256": str(entry.get("sha256") or ""),
                "file_size_bytes": entry.get("size"),
                "release": OSWORLD_V2_RELEASE,
                "source_repo": TASKS_HF_ID,
                "source_revision": source_revision,
                "split": OSWORLD_V2_RELEASE,
            }
        )
    return rows


@loader_cache(show_spinner="Downloading OSWorld V2.1 manifest from GitHub …")
def load_osworld_v21() -> pd.DataFrame:
    """Load the OSWorld V2.1 task catalog from the public release manifest.

    Returns:
        DataFrame with one row per gated task class (108 tasks). Task
        implementations themselves stay in the gated Hub dataset and are
        intentionally not mirrored here.
    """
    cache_root = cache_dir("osworld_v21")
    extracted = _download_release_archive(cache_root)
    rows = _load_rows(extracted)
    if not rows:
        msg = "No OSWorld V2.1 tasks found in the release manifest"
        raise RuntimeError(msg)
    return pd.DataFrame(rows)
