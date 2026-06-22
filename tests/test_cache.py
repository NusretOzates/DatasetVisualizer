"""Tests for loader cache."""

from __future__ import annotations

from dataset_visualizer.loaders.cache import loader_cache


def test_loader_cache_reuses_result() -> None:
    calls = {"count": 0}

    @loader_cache()
    def load(value: str) -> str:
        calls["count"] += 1
        return value.upper()

    assert load("a") == "A"
    assert load("a") == "A"
    assert calls["count"] == 1

    load.clear()
    assert load("a") == "A"
    assert calls["count"] == 2
