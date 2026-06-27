"""Tests for the NoCha GitHub loader."""

from __future__ import annotations

import json
import pickle
import shutil
from pathlib import Path

import pandas as pd
import pytest

from dataset_visualizer.loaders import nocha as nocha_module
from dataset_visualizer.loaders.nocha import (
    _attach_paired_claims,
    _normalize_claim_type,
    _normalize_nocha_frame,
    _normalize_row,
    load_nocha,
)

SAMPLE_ROWS = [
    {
        "book_title": "little_women_louisa_may_alcott",
        "claim": "Laurie and Amy celebrate their marriage quietly due to Beth's death.",
        "type": True,
        "index": 148,
        "false-claim-explanation": "They still marry, they just keep the wedding modest.",
        "length": 235118,
        "genre": "historical",
        "publication_year": "classics",
        "length_group": "above 180k",
        "response-gemini": "FALSE",
    },
    {
        "book_title": "little_women_louisa_may_alcott",
        "claim": "Laurie and Amy hold a large public wedding after Beth recovers.",
        "type": False,
        "index": 148,
        "false-claim-explanation": "The wedding is quiet, not public.",
        "length": 235118,
        "genre": "historical",
        "publication_year": "classics",
        "length_group": "above 180k",
        "response-gemini": "SKIPPED",
    },
]


def test_normalize_claim_type_accepts_bool_and_strings() -> None:
    assert _normalize_claim_type(True) == "True"
    assert _normalize_claim_type("false") == "False"


def test_normalize_row_builds_sample_id_and_responses() -> None:
    row = _normalize_row(SAMPLE_ROWS[0])
    assert row["sample_id"] == "little_women_louisa_may_alcott::148::True"
    assert row["claim_type"] == "True"
    assert row["model_responses"][0]["model"] == "gemini"
    assert row["model_responses"][0]["response"] == "FALSE"


def test_attach_paired_claims_links_true_and_false_rows() -> None:
    rows = _attach_paired_claims([_normalize_row(item) for item in SAMPLE_ROWS])
    true_row = next(row for row in rows if row["claim_type"] == "True")
    false_row = next(row for row in rows if row["claim_type"] == "False")
    assert true_row["paired_claim"] == false_row["claim"]
    assert false_row["paired_claim"] == true_row["claim"]


def test_normalize_nocha_frame_casts_int_columns() -> None:
    raw = pd.DataFrame([{"pair_index": "3", "length": None}])
    df = _normalize_nocha_frame(raw)
    assert df.loc[0, "pair_index"] == 3
    assert df.loc[0, "length"] == 0


def test_load_nocha_uses_cached_archive(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    extracted = tmp_path / nocha_module.EXTRACTED_DIR_NAME
    data_dir = extracted / "data_sample"
    data_dir.mkdir(parents=True)
    (data_dir / "data_sample.json").write_text(json.dumps(SAMPLE_ROWS), encoding="utf-8")
    books = {"little_women_louisa_may_alcott": "Once upon a time in Concord..."}
    (data_dir / "classic_books.pkl").write_bytes(pickle.dumps(books))

    def _mock_download(cache_root: Path) -> Path:
        target = cache_root / nocha_module.EXTRACTED_DIR_NAME
        shutil.copytree(extracted, target, dirs_exist_ok=True)
        (cache_root / ".extracted").write_text("ok", encoding="utf-8")
        return target

    monkeypatch.setattr(nocha_module, "_download_sample_archive", _mock_download)
    load_nocha.clear()

    df, extras = load_nocha()
    assert len(df) == 2
    assert extras["books"]["little_women_louisa_may_alcott"].startswith("Once upon")
