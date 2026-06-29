"""AA-LCR loader with extracted document previews from the Hub zip archive."""

from __future__ import annotations

import zipfile
from pathlib import Path
from typing import Any

import pandas as pd
from datasets import load_dataset
from huggingface_hub import hf_hub_download

from dataset_visualizer.loaders.base import cache_dir
from dataset_visualizer.loaders.benchmark_normalize import normalize_aa_lcr
from dataset_visualizer.loaders.cache import loader_cache

AA_LCR_HF_REPO = "ArtificialAnalysis/AA-LCR"
AA_LCR_ZIP_HUB_PATH = "extracted_text/AA-LCR_extracted-text.zip"
AA_LCR_SPLIT = "test"
DOCUMENT_PREVIEW_WORDS = 500


def _split_semicolon_field(value: object) -> list[str]:
    """Split semicolon-delimited Hub string fields into trimmed parts."""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return []
    text = str(value).strip()
    if not text:
        return []
    return [part.strip() for part in text.split(";") if part.strip()]


def _first_n_words(text: str, word_count: int) -> tuple[str, int, bool]:
    """Return the first *word_count* words and whether the source was truncated."""
    words = text.split()
    truncated = len(words) > word_count
    preview = " ".join(words[:word_count])
    return preview, len(words), truncated


def _document_path(extract_root: Path, category: str, set_id: str, filename: str) -> Path:
    return extract_root / "lcr" / category / set_id / filename


def _ensure_extracted_text(cache_root: Path) -> Path:
    """Download and extract the AA-LCR document archive once under *cache_root*."""
    extract_root = cache_root / "extracted"
    marker = extract_root / ".extracted"
    if marker.is_file():
        return extract_root

    cache_root.mkdir(parents=True, exist_ok=True)
    zip_path = Path(
        hf_hub_download(AA_LCR_HF_REPO, AA_LCR_ZIP_HUB_PATH, repo_type="dataset")
    )

    extract_root.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path) as archive:
        archive.extractall(extract_root)
    marker.write_text("ok", encoding="utf-8")
    return extract_root


def _read_document_text(path: Path) -> str:
    """Read one extracted document as UTF-8 text."""
    return path.read_text(encoding="utf-8", errors="replace")


def _document_previews(
    extract_root: Path,
    category: str,
    set_id: str,
    filenames: list[str],
    *,
    preview_words: int,
) -> tuple[list[dict[str, Any]], str, int, bool]:
    """Build per-file previews and a combined preview across the document set."""
    previews: list[dict[str, Any]] = []
    combined_parts: list[str] = []

    for filename in filenames:
        path = _document_path(extract_root, category, set_id, filename)
        if not path.is_file():
            previews.append(
                {
                    "filename": filename,
                    "preview": "",
                    "word_count": 0,
                    "truncated": False,
                    "missing": True,
                }
            )
            continue

        text = _read_document_text(path)
        preview, word_count, truncated = _first_n_words(text, preview_words)
        previews.append(
            {
                "filename": filename,
                "preview": preview,
                "word_count": word_count,
                "truncated": truncated,
                "missing": False,
            }
        )
        if text.strip():
            combined_parts.append(text)

    combined_text = "\n\n".join(combined_parts)
    combined_preview, combined_word_count, combined_truncated = _first_n_words(
        combined_text,
        preview_words,
    )
    return previews, combined_preview, combined_word_count, combined_truncated


def _attach_document_previews(df: pd.DataFrame, extract_root: Path) -> pd.DataFrame:
    """Add 500-word document previews to normalized AA-LCR rows."""
    document_previews: list[list[dict[str, Any]]] = []
    combined_previews: list[str] = []
    combined_word_counts: list[int] = []
    combined_truncated: list[bool] = []

    for row in df.itertuples(index=False):
        filenames = _split_semicolon_field(getattr(row, "data_source_filenames", ""))
        previews, combined_preview, word_count, truncated = _document_previews(
            extract_root,
            str(getattr(row, "document_category", "")),
            str(getattr(row, "document_set_id", "")),
            filenames,
            preview_words=DOCUMENT_PREVIEW_WORDS,
        )
        document_previews.append(previews)
        combined_previews.append(combined_preview)
        combined_word_counts.append(word_count)
        combined_truncated.append(truncated)

    enriched = df.copy()
    enriched["document_previews"] = document_previews
    enriched["document_preview"] = combined_previews
    enriched["document_preview_word_count"] = combined_word_counts
    enriched["document_preview_truncated"] = combined_truncated
    return enriched


@loader_cache()
def load_aa_lcr() -> pd.DataFrame:
    """Load AA-LCR questions with 500-word previews of each source document."""
    cache_root = cache_dir("aa_lcr")
    extract_root = _ensure_extracted_text(cache_root)

    raw = load_dataset(AA_LCR_HF_REPO, split=AA_LCR_SPLIT)
    frame = pd.DataFrame(raw)
    normalized = normalize_aa_lcr(frame, "sample_id")
    return _attach_document_previews(normalized, extract_root)
