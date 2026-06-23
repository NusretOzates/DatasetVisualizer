"""LiveCodeBench v6 dataset loader."""

from __future__ import annotations

import base64
import json
import pickle
import zlib
from typing import Any

import pandas as pd
from datasets import load_dataset
from huggingface_hub import hf_hub_download

from dataset_visualizer.loaders.base import cache_dir
from dataset_visualizer.loaders.cache import loader_cache

LCB_HF_REPO = "livecodebench/code_generation_lite"
LCB_FILE = "test6.jsonl"


def decode_private_test_cases(encoded: str) -> list[dict[str, Any]]:
    """Decode private test cases from plain JSON or compressed pickle payload.

    Args:
        encoded: Raw ``private_test_cases`` field from the dataset row.

    Returns:
        List of test-case dicts with input, output, and testtype keys.
    """
    try:
        parsed = json.loads(encoded)
    except (json.JSONDecodeError, TypeError):
        decoded = base64.b64decode(encoded.encode("utf-8"))
        decompressed = zlib.decompress(decoded)
        parsed = json.loads(pickle.loads(decompressed))
    if isinstance(parsed, list):
        return parsed
    return []


def _parse_public_test_cases(raw: str) -> list[dict[str, Any]]:
    """Parse the JSON-encoded public test cases column."""
    if not raw:
        return []
    return json.loads(raw)


def _parse_metadata(raw: str) -> dict[str, Any]:
    """Parse the JSON-encoded metadata column."""
    if not raw:
        return {}
    return json.loads(raw)


def _parse_contest_date(raw: str) -> pd.Timestamp:
    """Parse ISO contest dates into pandas timestamps."""
    return pd.to_datetime(raw, utc=False)


def _normalize_livecodebench_frame(df: pd.DataFrame) -> pd.DataFrame:
    """Apply column normalization to a raw LiveCodeBench DataFrame."""
    normalized = df.copy()
    normalized["public_test_cases"] = normalized["public_test_cases"].map(_parse_public_test_cases)
    normalized["metadata"] = normalized["metadata"].map(_parse_metadata)
    normalized["contest_date"] = normalized["contest_date"].map(_parse_contest_date)
    normalized["public_test_count"] = normalized["public_test_cases"].map(len)
    return normalized


@loader_cache(show_spinner="Downloading LiveCodeBench v6 …")
def load_livecodebench(file_name: str = LCB_FILE) -> pd.DataFrame:
    """Load and normalize LiveCodeBench code-generation problems.

    Args:
        file_name: JSONL file within the HF dataset repo (default ``test6.jsonl``).

    Returns:
        Normalized DataFrame with parsed public tests, metadata, and contest dates.
    """
    cache_dir("livecodebench")
    path = hf_hub_download(LCB_HF_REPO, file_name, repo_type="dataset")
    dataset = load_dataset("json", data_files=path, split="train")
    return _normalize_livecodebench_frame(dataset.to_pandas())
