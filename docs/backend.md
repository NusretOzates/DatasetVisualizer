# Backend (Gradio Server)

The API layer uses [`gradio.Server`](https://huggingface.co/blog/introducing-gradio-server) — a FastAPI app with Gradio queuing and `gradio_client` compatibility.

## Entry points

| Command | Module | Port |
|---------|--------|------|
| `uv run dataset-viz` | `cli.py` → `server.py` | 7860 (default) |
| `uv run python src/dataset_visualizer/server.py` | `server.py` | 7860 |
| `uv run python src/dataset_visualizer/app.py` | `app.py` → `server.py` | 7860 |

Override port with the `PORT` environment variable.

## Module layout

```
src/dataset_visualizer/
├── server.py           # gradio.Server, @app.api routes, static frontend mount
├── api/
│   ├── service.py      # Dataset handlers (load, filter, overview, samples)
│   ├── chart_data.py   # Chart JSON builders
│   └── serializers.py  # DataFrame/row → JSON
├── loaders/            # HF download + normalization + @loader_cache
├── registry.py         # LOADER_REGISTRY (inspect CLI, home row counts)
└── config.py           # Pydantic models for datasets.yaml
```

## API endpoints

All endpoints are registered with `@app.api(name="…")` in `server.py` and callable via `@gradio/client` or `gradio_client`:

| API name | Parameters | Returns |
|----------|------------|---------|
| `get_catalog` | — | Categories, dataset list, home table rows |
| `get_dataset_meta` | `dataset_id` | Description, archetype, controls, filters, `id_column` |
| `get_filter_options` | `dataset_id`, `params_json` | Unique filter values after load |
| `get_overview` | `dataset_id`, `params_json`, `filters_json` | Metrics, charts, tables |
| `get_sample` | `dataset_id`, `index`, `params_json`, `filters_json` | Row + extras at index |
| `find_sample` | `dataset_id`, `id_value`, `params_json`, `filters_json` | Row + extras by id column |
| `decode_private_tests` | `raw` | Decoded LiveCodeBench private test cases |

`params_json` and `filters_json` are JSON strings (or dicts) matching the control/filter names defined in `api/service.py`.

## Caching

- **Loaders:** `@loader_cache` in `loaders/cache.py` — in-process memoization for the server lifetime. Call `load_<name>.clear()` in tests.
- **On-disk:** `data/cache/<key>/` via `cache_dir()` — created on first load, shown by inspect CLI.
- **Hugging Face:** standard HF hub cache for downloaded datasets.

## Static frontend

When `frontend/out/` exists (after `npm run build`), `server.py` mounts:

- `/_next/*` — Next.js static assets
- `/` and `/dataset/{id}` — `index.html` (client-side routing)

CORS is enabled for local Next.js dev on port 3000.

## Adding a new API endpoint

Only needed for genuinely new capabilities (not per-dataset). Pattern:

```python
@app.api(name="my_endpoint")
def api_my_endpoint(arg: str) -> dict:
    return {"result": arg}
```

Register the handler in `api/service.py` and add a wrapper in `frontend/lib/api.ts`.
