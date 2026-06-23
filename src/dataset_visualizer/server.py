"""Gradio Server backend for the Dataset Visualizer."""

from __future__ import annotations

import os
from pathlib import Path

from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from gradio import Server

from dataset_visualizer.api.service import (
    decode_private_tests_api,
    find_sample,
    get_catalog,
    get_dataset_meta,
    get_filter_options,
    get_overview,
    get_sample,
    parse_json_param,
)
from dataset_visualizer.compat import apply_warning_filters

FRONTEND_DIST = Path(__file__).resolve().parents[2] / "frontend" / "out"
DEFAULT_PORT = int(os.environ.get("PORT", "7860"))
CORS_ORIGINS = [
    origin.strip()
    for origin in os.environ.get("CORS_ORIGINS", "http://localhost:3000").split(",")
    if origin.strip()
]

app = Server(title="Dataset Visualizer")
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.api(name="get_catalog")
def api_get_catalog() -> dict:
    """Return navigation metadata and home-page rows."""
    return get_catalog()


@app.api(name="get_dataset_meta")
def api_get_dataset_meta(dataset_id: str) -> dict:
    """Return dataset metadata, controls, and filter schema."""
    return get_dataset_meta(dataset_id)


@app.api(name="get_filter_options")
def api_get_filter_options(dataset_id: str, params_json: str = "") -> dict:
    """Return available filter values for a dataset."""
    return get_filter_options(dataset_id, parse_json_param(params_json))


@app.api(name="get_overview")
def api_get_overview(
    dataset_id: str,
    params_json: str = "",
    filters_json: str = "",
) -> dict:
    """Return overview metrics, charts, and tables."""
    return get_overview(
        dataset_id,
        parse_json_param(params_json),
        parse_json_param(filters_json),
    )


@app.api(name="get_sample")
def api_get_sample(
    dataset_id: str,
    index: int,
    params_json: str = "",
    filters_json: str = "",
) -> dict:
    """Return a sample row at the given index."""
    return get_sample(
        dataset_id,
        index,
        parse_json_param(params_json),
        parse_json_param(filters_json),
    )


@app.api(name="find_sample")
def api_find_sample(
    dataset_id: str,
    id_value: str,
    params_json: str = "",
    filters_json: str = "",
) -> dict:
    """Find a sample by its id column value."""
    return find_sample(
        dataset_id,
        id_value,
        parse_json_param(params_json),
        parse_json_param(filters_json),
    )


@app.api(name="decode_private_tests")
def api_decode_private_tests(raw: str) -> dict:
    """Decode LiveCodeBench private test cases."""
    return decode_private_tests_api(raw)


if FRONTEND_DIST.is_dir():
    assets_dir = FRONTEND_DIST / "_next"
    if assets_dir.is_dir():
        app.mount("/_next", StaticFiles(directory=assets_dir), name="next-assets")

    @app.get("/")
    async def homepage() -> FileResponse:
        return FileResponse(FRONTEND_DIST / "index.html")

    @app.get("/dataset/{dataset_id}")
    @app.get("/dataset/{dataset_id}/")
    async def dataset_page(dataset_id: str) -> FileResponse:
        page = FRONTEND_DIST / "dataset" / dataset_id / "index.html"
        if page.is_file():
            return FileResponse(page)
        not_found = FRONTEND_DIST / "404.html"
        if not_found.is_file():
            return FileResponse(not_found)
        return FileResponse(FRONTEND_DIST / "index.html")


apply_warning_filters()


def main() -> None:
    """Launch the Gradio Server with CORS enabled for local Next.js dev."""
    app.launch(server_name="0.0.0.0", server_port=DEFAULT_PORT, show_error=True)


if __name__ == "__main__":
    main()
