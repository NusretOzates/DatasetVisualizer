"""Tests for the shared dataset page layout."""

from __future__ import annotations

from unittest.mock import MagicMock

import pandas as pd
import pytest

from dataset_visualizer.components import page_layout


def test_render_dataset_page_shows_config_description(monkeypatch: pytest.MonkeyPatch) -> None:
    """Dataset pages should render the YAML description under the title."""
    markdown_calls: list[str] = []

    def _capture_markdown(text: str) -> None:
        markdown_calls.append(text)

    monkeypatch.setattr(page_layout.st, "title", lambda _title: None)
    monkeypatch.setattr(page_layout.st, "markdown", _capture_markdown)

    overview_tab = MagicMock()
    sample_tab = MagicMock()
    overview_tab.__enter__.return_value = None
    overview_tab.__exit__.return_value = False
    sample_tab.__enter__.return_value = None
    sample_tab.__exit__.return_value = False
    monkeypatch.setattr(
        page_layout.st,
        "tabs",
        lambda _labels: (overview_tab, sample_tab),
    )

    sample_row = pd.Series({"subject": "biology"})
    monkeypatch.setattr(
        page_layout,
        "sample_navigator",
        lambda _df, id_column, key_prefix: (sample_row, 0, 1),
    )

    page_layout.render_dataset_page(
        title="MMLU",
        df=pd.DataFrame({"subject": ["biology"]}),
        id_column="subject",
        render_overview=lambda _df: None,
        render_sample=lambda _row: None,
        dataset_id="mmlu",
        key_prefix="mmlu",
    )

    assert markdown_calls
    assert "Massive Multitask Language Understanding" in markdown_calls[0]
