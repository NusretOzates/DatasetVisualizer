"""Tests for the pre-download CLI."""

from __future__ import annotations

import threading
import time

import pandas as pd
import pytest

from dataset_visualizer.pre_download import (
    FAST_DATASET_IDS,
    _resolve_dataset_ids,
    pre_download_datasets,
)


def test_resolve_dataset_ids_fast() -> None:
    assert _resolve_dataset_ids(dataset_id=None, category=None, fast=True) == list(FAST_DATASET_IDS)


def test_resolve_dataset_ids_unknown_id_raises() -> None:
    with pytest.raises(ValueError, match="Unknown dataset id"):
        _resolve_dataset_ids(dataset_id="not_real", category=None, fast=False)


def test_pre_download_skips_gated_when_requested(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    calls: list[str] = []

    class FakeDescriptor:
        def loader(self, _params: dict[str, object]) -> tuple[pd.DataFrame, dict[str, object]]:
            calls.append("loaded")
            return pd.DataFrame(), {}

    monkeypatch.setattr(
        "dataset_visualizer.pre_download.get_descriptor",
        lambda _dataset_id: FakeDescriptor(),
    )

    code = pre_download_datasets(["gpqa_diamond"], skip_gated=True)
    captured = capsys.readouterr()

    assert code == 0
    assert calls == []
    assert "WARN" in captured.err
    assert "gated" in captured.err.lower()


def test_pre_download_counts_loader_failures(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    class FakeDescriptor:
        def loader(self, _params: dict[str, object]) -> tuple[pd.DataFrame, dict[str, object]]:
            msg = "download failed"
            raise RuntimeError(msg)

    monkeypatch.setattr(
        "dataset_visualizer.pre_download.get_descriptor",
        lambda _dataset_id: FakeDescriptor(),
    )

    code = pre_download_datasets(["mmlu"])
    captured = capsys.readouterr()

    assert code == 1
    assert "FAIL" in captured.err


def test_pre_download_warns_on_gated_runtime_error(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    class FakeDescriptor:
        def loader(self, _params: dict[str, object]) -> tuple[pd.DataFrame, dict[str, object]]:
            msg = "Dataset is a gated dataset on the Hub."
            raise RuntimeError(msg)

    monkeypatch.setattr(
        "dataset_visualizer.pre_download.get_descriptor",
        lambda _dataset_id: FakeDescriptor(),
    )

    code = pre_download_datasets(["mmlu"])
    captured = capsys.readouterr()

    assert code == 1
    assert "WARN" in captured.err
    assert "HF_TOKEN" in captured.err


def test_pre_download_runs_parallel_when_workers_gt_one(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    lock = threading.Lock()
    active = 0
    max_active = 0

    class FakeDescriptor:
        def loader(self, _params: dict[str, object]) -> tuple[pd.DataFrame, dict[str, object]]:
            nonlocal active, max_active
            with lock:
                active += 1
                max_active = max(max_active, active)
            time.sleep(0.05)
            with lock:
                active -= 1
            return pd.DataFrame(), {}

    monkeypatch.setattr(
        "dataset_visualizer.pre_download.get_descriptor",
        lambda _dataset_id: FakeDescriptor(),
    )

    dataset_ids = list(FAST_DATASET_IDS)
    pre_download_datasets(dataset_ids, workers=4)

    assert max_active > 1


def test_pre_download_workers_must_be_positive() -> None:
    with pytest.raises(ValueError, match="workers must be >= 1"):
        pre_download_datasets(["mmlu"], workers=0)
