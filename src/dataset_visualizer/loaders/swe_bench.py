"""SWE-bench Verified, Multilingual, and PRO dataset loaders."""

from __future__ import annotations

import json
from typing import Literal

import pandas as pd
import streamlit as st
from datasets import load_dataset

from dataset_visualizer.loaders.base import cache_dir

SWEBenchVariant = Literal["verified", "multilingual", "pro"]

VARIANT_HF_IDS: dict[SWEBenchVariant, str] = {
    "verified": "SWE-bench/SWE-bench_Verified",
    "multilingual": "SWE-bench/SWE-bench_Multilingual",
    "pro": "Contextbench/SWE-bench_Pro",
}


def _parse_test_list(raw: object) -> list[str]:
    """Parse FAIL_TO_PASS / fail_to_pass JSON string columns into string lists."""
    if raw is None or (isinstance(raw, float) and pd.isna(raw)):
        return []
    if isinstance(raw, list):
        return [str(item) for item in raw]
    if not isinstance(raw, str):
        return [str(raw)]

    text = raw.strip()
    if not text:
        return []
    try:
        value = json.loads(text)
    except json.JSONDecodeError:
        return [text]
    if isinstance(value, list):
        return [str(item) for item in value]
    return [str(value)]


def _normalize_swe_bench_frame(df: pd.DataFrame, variant: SWEBenchVariant) -> pd.DataFrame:
    """Normalize SWE-bench rows with parsed test lists and metadata."""
    normalized = df.copy()

    if variant == "pro":
        fail_col, pass_col = "fail_to_pass", "pass_to_pass"
    else:
        fail_col, pass_col = "FAIL_TO_PASS", "PASS_TO_PASS"

    normalized["fail_to_pass"] = normalized[fail_col].map(_parse_test_list)
    normalized["pass_to_pass"] = normalized[pass_col].map(_parse_test_list)
    normalized["fail_to_pass_count"] = normalized["fail_to_pass"].map(len)
    normalized["pass_to_pass_count"] = normalized["pass_to_pass"].map(len)
    normalized["variant"] = variant

    if "created_at" in normalized.columns:
        normalized["created_at"] = pd.to_datetime(normalized["created_at"], errors="coerce")

    if "issue_categories" in normalized.columns:
        normalized["issue_categories"] = normalized["issue_categories"].map(_parse_test_list)

    return normalized


def _load_swe_bench(variant: SWEBenchVariant, split: str = "test") -> pd.DataFrame:
    """Load and normalize a SWE-bench variant from Hugging Face."""
    cache_dir("swe_bench")
    hf_id = VARIANT_HF_IDS[variant]
    dataset = load_dataset(hf_id, split=split)
    return _normalize_swe_bench_frame(dataset.to_pandas(), variant=variant)


@st.cache_data(show_spinner="Downloading SWE-Bench Verified …")
def load_swe_bench_verified(split: str = "test") -> pd.DataFrame:
    """Load SWE-Bench Verified (500 human-validated Python issues)."""
    return _load_swe_bench("verified", split=split)


@st.cache_data(show_spinner="Downloading SWE-Bench Multilingual …")
def load_swe_bench_multilingual(split: str = "test") -> pd.DataFrame:
    """Load SWE-Bench Multilingual (300 issues across 9 languages)."""
    return _load_swe_bench("multilingual", split=split)


@st.cache_data(show_spinner="Downloading SWE-Bench PRO …")
def load_swe_bench_pro(split: str = "test") -> pd.DataFrame:
    """Load SWE-Bench PRO (731 enterprise-scale issue resolution tasks)."""
    return _load_swe_bench("pro", split=split)
