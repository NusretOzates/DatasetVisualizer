"""Tests for Toolathlon overview payloads."""

from __future__ import annotations

import pandas as pd

from dataset_visualizer.api.overview import overview_toolathlon


def test_overview_toolathlon_summarizes_by_mcp_not_all_tasks() -> None:
    df = pd.DataFrame(
        [
            {
                "primary_mcp": "filesystem",
                "mcp_server_count": 2,
                "local_tool_count": 3,
                "split": "finalpool",
            },
            {
                "primary_mcp": "filesystem",
                "mcp_server_count": 1,
                "local_tool_count": 2,
                "split": "finalpool",
            },
            {
                "primary_mcp": "github",
                "mcp_server_count": 3,
                "local_tool_count": 4,
                "split": "finalpool",
            },
        ]
    )

    overview = overview_toolathlon(df, {})
    assert overview["metrics"][0] == {"label": "Tasks", "value": "3"}
    assert len(overview["tables"]) == 1
    assert overview["tables"][0]["title"] == "Tasks by primary MCP server"
    rows = overview["tables"][0]["rows"]
    assert len(rows) == 2
    assert "task_name" not in overview["tables"][0]["columns"]
