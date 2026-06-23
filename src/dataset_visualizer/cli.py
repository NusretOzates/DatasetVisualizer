"""CLI entry point for launching the Dataset Visualizer."""

from __future__ import annotations

from dataset_visualizer.server import main as launch_server


def main() -> None:
    """Launch the Gradio Server backend."""
    launch_server()


if __name__ == "__main__":
    main()
