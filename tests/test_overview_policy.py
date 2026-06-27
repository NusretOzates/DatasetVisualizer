"""Guardrails for dataset overview payloads."""

from __future__ import annotations

import re
from pathlib import Path

OVERVIEW_PATH = Path(__file__).resolve().parents[1] / "src" / "dataset_visualizer" / "api" / "overview.py"
FORBIDDEN_TABLE_TITLE = re.compile(r'"title":\s*"All\s', re.IGNORECASE)


def test_overview_never_uses_all_row_catalog_titles() -> None:
    source = OVERVIEW_PATH.read_text(encoding="utf-8")
    matches = FORBIDDEN_TABLE_TITLE.findall(source)
    assert not matches, f"Overview tables must not catalog every row: {matches}"
