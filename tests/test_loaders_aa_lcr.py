"""Tests for the AA-LCR loader."""

from __future__ import annotations

import zipfile
from pathlib import Path

import pandas as pd
import pytest

from dataset_visualizer.loaders import aa_lcr as aa_lcr_module
from dataset_visualizer.loaders.aa_lcr import (
    DOCUMENT_PREVIEW_WORDS,
    _attach_document_previews,
    _document_previews,
    _ensure_extracted_text,
    _first_n_words,
    load_aa_lcr,
)


def test_first_n_words_truncates_long_text() -> None:
    preview, word_count, truncated = _first_n_words("one two three four five", 3)

    assert preview == "one two three"
    assert word_count == 5
    assert truncated is True


def test_document_previews_reads_files_in_order(tmp_path: Path) -> None:
    extract_root = tmp_path / "extracted"
    doc_dir = extract_root / "lcr" / "Academia" / "ac_markets"
    doc_dir.mkdir(parents=True)
    (doc_dir / "a.txt").write_text("alpha beta gamma", encoding="utf-8")
    (doc_dir / "b.txt").write_text("delta epsilon zeta eta theta", encoding="utf-8")

    previews, combined, word_count, truncated = _document_previews(
        extract_root,
        "Academia",
        "ac_markets",
        ["a.txt", "b.txt"],
        preview_words=4,
    )

    assert len(previews) == 2
    assert previews[0]["preview"] == "alpha beta gamma"
    assert previews[0]["truncated"] is False
    assert previews[1]["preview"] == "delta epsilon zeta eta"
    assert previews[1]["truncated"] is True
    assert combined == "alpha beta gamma delta"
    assert word_count == 8
    assert truncated is True


def test_attach_document_previews_adds_columns(tmp_path: Path) -> None:
    extract_root = tmp_path / "extracted"
    doc_dir = extract_root / "lcr" / "Legal" / "legal_eu_ai"
    doc_dir.mkdir(parents=True)
    (doc_dir / "doc.txt").write_text(" ".join(f"word{i}" for i in range(600)), encoding="utf-8")

    frame = pd.DataFrame(
        {
            "sample_id": ["legal_eu_ai_1"],
            "document_category": ["Legal"],
            "document_set_id": ["legal_eu_ai"],
            "data_source_filenames": ["doc.txt"],
            "question": ["Does the AI Act apply?"],
            "answer": ["No"],
        }
    )

    enriched = _attach_document_previews(frame, extract_root)

    assert enriched["document_preview_truncated"].iloc[0]
    assert len(enriched["document_preview"].iloc[0].split()) == DOCUMENT_PREVIEW_WORDS
    assert enriched["document_previews"].iloc[0][0]["filename"] == "doc.txt"


def test_ensure_extracted_text_downloads_once(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    cache_root = tmp_path / "aa_lcr"
    zip_path = cache_root / "archive.zip"
    cache_root.mkdir()

    with zipfile.ZipFile(zip_path, "w") as archive:
        archive.writestr(
            "lcr/Academia/ac_markets/sample.txt",
            "context words here",
        )

    monkeypatch.setattr(
        aa_lcr_module,
        "hf_hub_download",
        lambda *_args, **_kwargs: str(zip_path),
    )

    first = _ensure_extracted_text(cache_root)
    second = _ensure_extracted_text(cache_root)

    assert first == second
    assert (first / "lcr" / "Academia" / "ac_markets" / "sample.txt").is_file()


def test_load_aa_lcr_builds_previews(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    extract_root = tmp_path / "extracted"
    doc_dir = extract_root / "lcr" / "Academia" / "ac_markets"
    doc_dir.mkdir(parents=True)
    (doc_dir / "a.txt").write_text("first document words", encoding="utf-8")
    marker = extract_root / ".extracted"
    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.write_text("ok", encoding="utf-8")

    raw = pd.DataFrame(
        {
            "document_category": ["Academia"],
            "document_set_id": ["ac_markets"],
            "question_id": [1],
            "question": ["Summarize the trend."],
            "answer": ["Airline Industry"],
            "data_source_filenames": ["a.txt"],
            "data_source_urls": ["https://example.com/a.txt"],
            "input_tokens": [1000],
        }
    )

    monkeypatch.setattr(aa_lcr_module, "cache_dir", lambda _key: tmp_path)
    monkeypatch.setattr(aa_lcr_module, "_ensure_extracted_text", lambda _root: extract_root)
    monkeypatch.setattr(
        aa_lcr_module,
        "load_dataset",
        lambda *_args, **_kwargs: raw,
    )
    load_aa_lcr.clear()

    frame = load_aa_lcr()

    assert frame.loc[0, "document_preview"].startswith("first document words")
    assert frame.loc[0, "sample_id"] == "ac_markets_1"
