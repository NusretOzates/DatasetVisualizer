"""Tests for the dataset-viz CLI entry point."""

from __future__ import annotations

from unittest.mock import patch

from dataset_visualizer.cli import main


def test_main_launches_gradio_server() -> None:
    """CLI should delegate to the Gradio server launcher."""
    with patch("dataset_visualizer.cli.launch_server") as launch_server:
        main()
    launch_server.assert_called_once()
