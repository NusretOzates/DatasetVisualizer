"""Tests for the Gradio server entry point."""

from __future__ import annotations

import ast
from pathlib import Path

from dataset_visualizer import app


def test_app_main_block_calls_main() -> None:
    """app.py __main__ must run the server main function directly."""
    tree = ast.parse(Path(app.__file__).read_text(encoding="utf-8"))
    main_guard = next(
        node
        for node in tree.body
        if isinstance(node, ast.If)
        and isinstance(node.test, ast.Compare)
        and isinstance(node.test.left, ast.Name)
        and node.test.left.id == "__name__"
    )
    assert len(main_guard.body) == 1
    call = main_guard.body[0]
    assert isinstance(call, ast.Expr) and isinstance(call.value, ast.Call)
    func = call.value.func
    assert isinstance(func, ast.Name) and func.id == "main"
