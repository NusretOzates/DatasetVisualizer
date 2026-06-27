"""BrowseComp loader (OpenAI simple-evals encrypted CSV)."""

from __future__ import annotations

import base64
import hashlib
from pathlib import Path
from typing import Any
from urllib.error import HTTPError
from urllib.request import urlopen

import pandas as pd

from dataset_visualizer.loaders.base import cache_dir
from dataset_visualizer.loaders.cache import loader_cache

BROWSECOMP_CSV_URL = (
    "https://openaipublic.blob.core.windows.net/simple-evals/browse_comp_test_set.csv"
)
BROWSECOMP_GITHUB_REPO = "openai/simple-evals"
BROWSECOMP_SPLIT = "test"
BROWSECOMP_EXPECTED_ROWS = 1266


def _derive_key(password: str, length: int) -> bytes:
    """Derive a fixed-length XOR key from the row canary string."""
    hasher = hashlib.sha256()
    hasher.update(password.encode())
    key = hasher.digest()
    return key * (length // len(key)) + key[: length % len(key)]


def decrypt_browsecomp_field(ciphertext_b64: str, password: str) -> str:
    """Decrypt a base64-encoded BrowseComp field using the row canary."""
    encrypted = base64.b64decode(ciphertext_b64)
    key = _derive_key(password, len(encrypted))
    decrypted = bytes(left ^ right for left, right in zip(encrypted, key, strict=True))
    return decrypted.decode()


def _cached_csv_row_count(csv_path: Path) -> int:
    """Return data row count in a cached BrowseComp CSV (excluding header)."""
    with csv_path.open(encoding="utf-8") as handle:
        return max(sum(1 for _ in handle) - 1, 0)


def _download_csv(cache_root: Path) -> Path:
    csv_path = cache_root / "browse_comp_test_set.csv"
    if csv_path.is_file():
        if _cached_csv_row_count(csv_path) >= BROWSECOMP_EXPECTED_ROWS:
            return csv_path
        csv_path.unlink()

    cache_root.mkdir(parents=True, exist_ok=True)
    try:
        with urlopen(BROWSECOMP_CSV_URL, timeout=180) as response:
            csv_path.write_bytes(response.read())
    except HTTPError as exc:
        msg = f"Failed to download BrowseComp CSV: HTTP {exc.code}"
        raise RuntimeError(msg) from exc
    return csv_path


def _normalize_browsecomp_frame(df: pd.DataFrame) -> pd.DataFrame:
    normalized = df.copy()
    if "question_preview" not in normalized.columns:
        preview = normalized.get("question", pd.Series(dtype=str)).astype(str)
        normalized["question_preview"] = preview.str.slice(0, 120)
    normalized["split"] = BROWSECOMP_SPLIT
    return normalized


def _load_rows(csv_path: Path) -> list[dict[str, Any]]:
    raw = pd.read_csv(csv_path)
    rows: list[dict[str, Any]] = []
    for index, record in raw.iterrows():
        canary = str(record.get("canary", ""))
        question = decrypt_browsecomp_field(str(record["problem"]), canary)
        answer = decrypt_browsecomp_field(str(record["answer"]), canary)
        rows.append(
            {
                "sample_id": f"browsecomp_{index}",
                "question": question,
                "answer": answer,
                "question_preview": question[:120],
                "problem_topic": str(record.get("problem_topic", "")).strip(),
                "canary": canary,
                "split": BROWSECOMP_SPLIT,
            }
        )
    return rows


@loader_cache(show_spinner="Downloading BrowseComp from OpenAI simple-evals …")
def load_browsecomp() -> pd.DataFrame:
    """Load and decrypt the BrowseComp browsing-agent benchmark.

    Returns:
        Normalized DataFrame with decrypted questions and short reference answers.
    """
    cache_root = cache_dir("browsecomp")
    csv_path = _download_csv(cache_root)
    rows = _load_rows(csv_path)
    if not rows:
        msg = "No BrowseComp rows found in the downloaded CSV"
        raise RuntimeError(msg)
    return _normalize_browsecomp_frame(pd.DataFrame(rows))
