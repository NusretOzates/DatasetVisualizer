"""Tests for the dataset-viz CLI entry point."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from dataset_visualizer.cli import main


def test_main_launches_streamlit_with_app_path() -> None:
    """CLI should delegate to streamlit run on app.py."""
    completed = MagicMock(returncode=0)

    with (
        patch("dataset_visualizer.cli.subprocess.run", return_value=completed) as run,
        patch("dataset_visualizer.cli.sys.argv", ["dataset-viz", "--server.port", "8502"]),
        pytest.raises(SystemExit) as exc,
    ):
        main()

    assert exc.value.code == 0
    cmd = run.call_args[0][0]
    assert cmd[1:4] == ["-m", "streamlit", "run"]
    assert cmd[4].endswith("dataset_visualizer/app.py")
    assert cmd[5:] == ["--server.port", "8502"]
