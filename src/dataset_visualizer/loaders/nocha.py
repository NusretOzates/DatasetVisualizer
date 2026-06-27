"""NoCha long-context book QA loader (marzenakrp/nocha on GitHub)."""

from __future__ import annotations

import io
import json
import pickle
import zipfile
from pathlib import Path
from typing import Any
from urllib.error import HTTPError
from urllib.request import urlopen

import pandas as pd

from dataset_visualizer.loaders.base import cache_dir
from dataset_visualizer.loaders.cache import loader_cache

NOCHA_GITHUB_REPO = "marzenakrp/nocha"
NOCHA_BRANCH = "main"
NOCHA_ZIP_URL = (
    f"https://github.com/{NOCHA_GITHUB_REPO}/archive/refs/heads/{NOCHA_BRANCH}.zip"
)
EXTRACTED_DIR_NAME = f"nocha-{NOCHA_BRANCH}"
DATA_SAMPLE_JSON = "data_sample/data_sample.json"
CLASSIC_BOOKS_PKL = "data_sample/classic_books.pkl"


def _normalize_claim_type(value: object) -> str:
    if isinstance(value, bool):
        return "True" if value else "False"
    text = str(value).strip()
    lowered = text.lower()
    if lowered == "true":
        return "True"
    if lowered == "false":
        return "False"
    return text


def _parse_model_responses(raw: dict[str, Any]) -> list[dict[str, str]]:
    responses: list[dict[str, str]] = []
    for key, value in raw.items():
        if not key.startswith("response-"):
            continue
        model = key.removeprefix("response-")
        text = str(value).strip()
        responses.append(
            {
                "model": model,
                "response": text,
                "skipped": text.upper() == "SKIPPED" or not text,
            }
        )
    responses.sort(key=lambda item: item["model"])
    return responses


def _normalize_row(raw: dict[str, Any]) -> dict[str, Any]:
    book_title = str(raw.get("book_title", "")).strip()
    pair_index = int(raw["index"])
    claim_type = _normalize_claim_type(raw.get("type"))
    claim = str(raw.get("claim", "")).strip()
    false_explanation = str(
        raw.get("false-claim-explanation") or raw.get("false_claim_explanation") or ""
    ).strip()
    length_group = str(raw.get("length_group") or raw.get("length_bucket") or "").strip()

    return {
        "sample_id": f"{book_title}::{pair_index}::{claim_type}",
        "book_title": book_title,
        "claim": claim,
        "claim_preview": claim[:120],
        "claim_type": claim_type,
        "pair_index": pair_index,
        "false_claim_explanation": false_explanation,
        "length": int(raw.get("length") or 0),
        "length_group": length_group,
        "genre": str(raw.get("genre") or "").strip(),
        "publication_year": str(raw.get("publication_year") or "").strip(),
        "model_responses": _parse_model_responses(raw),
    }


def _attach_paired_claims(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_pair: dict[tuple[str, int], dict[str, str]] = {}
    for row in rows:
        key = (row["book_title"], row["pair_index"])
        by_pair.setdefault(key, {})[row["claim_type"]] = row["claim"]

    for row in rows:
        pair = by_pair.get((row["book_title"], row["pair_index"]), {})
        other_type = "False" if row["claim_type"] == "True" else "True"
        row["paired_claim"] = pair.get(other_type, "")
        row["paired_claim_type"] = other_type
    return rows


def _extracted_root(cache_root: Path) -> Path:
    return cache_root / EXTRACTED_DIR_NAME


def _download_sample_archive(cache_root: Path) -> Path:
    """Download and extract the upstream NoCha repository archive."""
    extracted = _extracted_root(cache_root)
    marker = cache_root / ".extracted"
    json_path = extracted / DATA_SAMPLE_JSON
    if marker.is_file() and json_path.is_file():
        return extracted

    cache_root.mkdir(parents=True, exist_ok=True)
    try:
        with urlopen(NOCHA_ZIP_URL, timeout=180) as response:
            archive_bytes = response.read()
    except HTTPError as exc:
        msg = f"Failed to download NoCha archive: HTTP {exc.code}"
        raise RuntimeError(msg) from exc

    with zipfile.ZipFile(io.BytesIO(archive_bytes)) as archive:
        archive.extractall(cache_root)

    if not json_path.is_file():
        msg = f"NoCha archive missing sample JSON at {json_path}"
        raise RuntimeError(msg)

    marker.write_text("ok", encoding="utf-8")
    return extracted


def _load_sample_rows(extracted: Path) -> list[dict[str, Any]]:
    json_path = extracted / DATA_SAMPLE_JSON
    raw_rows = json.loads(json_path.read_text(encoding="utf-8"))
    if not isinstance(raw_rows, list):
        msg = f"Expected a JSON array in {json_path}"
        raise RuntimeError(msg)
    rows = [_normalize_row(item) for item in raw_rows if isinstance(item, dict)]
    return _attach_paired_claims(rows)


def _load_classic_books(extracted: Path) -> dict[str, str]:
    pkl_path = extracted / CLASSIC_BOOKS_PKL
    if not pkl_path.is_file():
        return {}
    with pkl_path.open("rb") as handle:
        books = pickle.load(handle)
    if not isinstance(books, dict):
        msg = f"Expected mapping in {pkl_path}"
        raise RuntimeError(msg)
    return {str(key): str(value) for key, value in books.items()}


def _normalize_nocha_frame(df: pd.DataFrame) -> pd.DataFrame:
    normalized = df.copy()
    if "pair_index" in normalized.columns:
        normalized["pair_index"] = normalized["pair_index"].astype(int)
    if "length" in normalized.columns:
        normalized["length"] = normalized["length"].fillna(0).astype(int)
    return normalized


@loader_cache(show_spinner="Downloading NoCha sample data from GitHub …")
def load_nocha() -> tuple[pd.DataFrame, dict[str, Any]]:
    """Load the public NoCha sample claims and classic book texts.

    Returns:
        Tuple of normalized claim rows and loader extras with ``books`` text mapping.
    """
    cache_root = cache_dir("nocha")
    extracted = _download_sample_archive(cache_root)
    rows = _load_sample_rows(extracted)
    if not rows:
        msg = "No NoCha sample claims found in the downloaded archive"
        raise RuntimeError(msg)
    books = _load_classic_books(extracted)
    return _normalize_nocha_frame(pd.DataFrame(rows)), {"books": books}
