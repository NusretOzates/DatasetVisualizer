"""Tests for MTOB decryption helpers."""

from __future__ import annotations

import pandas as pd
import pytest

from dataset_visualizer.loaders.benchmark_normalize import normalize_mtob
from dataset_visualizer.loaders.mtob_crypto import decrypt_mtob_text


def test_decrypt_mtob_sample_row() -> None:
    source = decrypt_mtob_text("PEcguWjEksM=", "v0I+xheXU/H1ZEB3+v0=")
    target = decrypt_mtob_text("BJaJecFlRi4=", "aL7Q0x/kNIFClfqauo+bDKgu")
    assert source == "Who asked you?"
    assert target == "Namana kat gerket?"


def test_normalize_mtob_adds_readable_text_columns() -> None:
    df = pd.DataFrame(
        {
            "original_ciphertext": ["v0I+xheXU/H1ZEB3+v0="],
            "original_nonce": ["PEcguWjEksM="],
            "ground_truth_ciphertext": ["aL7Q0x/kNIFClfqauo+bDKgu"],
            "ground_truth_nonce": ["BJaJecFlRi4="],
            "original_id": [8],
            "subtask": ["English_to_Kalamang"],
        }
    )
    normalized = normalize_mtob(df, "sample_id")
    assert normalized["source_text"].iloc[0] == "Who asked you?"
    assert normalized["target_text"].iloc[0] == "Namana kat gerket?"
    assert normalized["sample_id"].iloc[0] == "0"


def test_normalize_mtob_requires_encryption_columns() -> None:
    df = pd.DataFrame({"subtask": ["English_to_Kalamang"]})
    with pytest.raises(ValueError, match="missing encryption columns"):
        normalize_mtob(df, "sample_id")
