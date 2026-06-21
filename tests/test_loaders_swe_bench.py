"""Tests for SWE-bench loader normalization."""

from __future__ import annotations

import json

import pandas as pd
import pytest

from dataset_visualizer.loaders.swe_bench import (
    _normalize_swe_bench_frame,
    _parse_test_list,
    load_swe_bench_verified,
)

VERIFIED_ROW = {
    "instance_id": "django__django-12345",
    "repo": "django/django",
    "base_commit": "abc123",
    "problem_statement": "Fix bug",
    "patch": "diff --git a/foo.py",
    "test_patch": "diff --git a/tests.py",
    "hints_text": "Try checking models",
    "created_at": "2024-01-01T00:00:00",
    "version": "4.2",
    "FAIL_TO_PASS": json.dumps(["tests.test_foo.TestFoo::test_bar"]),
    "PASS_TO_PASS": json.dumps(["tests.test_foo.TestFoo::test_baz"]),
    "difficulty": "medium",
}


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        (json.dumps(["a", "b"]), ["a", "b"]),
        (["x"], ["x"]),
        ("", []),
        (None, []),
    ],
)
def test_parse_test_list(raw: object, expected: list[str]) -> None:
    assert _parse_test_list(raw) == expected


def test_normalize_swe_bench_verified_frame() -> None:
    raw = pd.DataFrame([VERIFIED_ROW])
    df = _normalize_swe_bench_frame(raw, variant="verified")

    assert df.loc[0, "fail_to_pass_count"] == 1
    assert df.loc[0, "pass_to_pass_count"] == 1
    assert df.loc[0, "variant"] == "verified"
    assert df.loc[0, "fail_to_pass"][0] == "tests.test_foo.TestFoo::test_bar"


def test_normalize_swe_bench_pro_frame() -> None:
    row = {
        **VERIFIED_ROW,
        "fail_to_pass": json.dumps(["test_a"]),
        "pass_to_pass": json.dumps(["test_b"]),
        "repo_language": "Python",
        "issue_categories": json.dumps(["bug"]),
    }
    del row["FAIL_TO_PASS"]
    del row["PASS_TO_PASS"]
    raw = pd.DataFrame([row])
    df = _normalize_swe_bench_frame(raw, variant="pro")

    assert df.loc[0, "fail_to_pass_count"] == 1
    assert df.loc[0, "issue_categories"] == ["bug"]


def test_load_swe_bench_verified(monkeypatch: pytest.MonkeyPatch) -> None:
    raw = pd.DataFrame([VERIFIED_ROW])

    class FakeDataset:
        def to_pandas(self) -> pd.DataFrame:
            return raw.copy()

    monkeypatch.setattr(
        "dataset_visualizer.loaders.swe_bench.load_dataset",
        lambda *args, **kwargs: FakeDataset(),
    )
    load_swe_bench_verified.clear()

    df = load_swe_bench_verified()
    assert len(df) == 1
    assert df.loc[0, "instance_id"] == "django__django-12345"
