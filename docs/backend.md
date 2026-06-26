# Backend (Gradio Server)

The API layer uses [`gradio.Server`](https://huggingface.co/blog/introducing-gradio-server) — a FastAPI app with Gradio queuing and `gradio_client` compatibility.

## Entry points

| Command | Module | Port |
|---------|--------|------|
| `uv run dataset-viz` | `cli.py` → `server.py` | 7860 (default) |
| `uv run python src/dataset_visualizer/server.py` | `server.py` | 7860 |

Override port with the `PORT` environment variable.

## Module layout

```
src/dataset_visualizer/
├── server.py              # gradio.Server, CORS, @app.api routes, static frontend mount
├── api/
│   ├── dataset_registry.py  # DATASET_REGISTRY — manual + auto hf_benchmark
│   ├── service.py           # Catalog, meta, filters, overview, samples (orchestration)
│   ├── filters.py           # Schema-driven apply_filters() + build_filter_options()
│   ├── overview.py          # Per-dataset overview builders (manual loaders)
│   ├── generic_overview.py  # Reusable overview for hf_benchmark entries
│   └── serializers.py       # DataFrame/row → JSON
├── loaders/                 # HF download + normalization + @loader_cache
│   ├── hf_benchmark.py      # Config-driven generic Hub loader
│   └── benchmark_normalize.py  # Profile-specific column normalization
├── row_count.py             # Home-page row counts via DATASET_REGISTRY
└── config.py                # Pydantic models for datasets.yaml
```

## Dataset registration (`api/dataset_registry.py`)

Each config `id` has one `DatasetDescriptor`:

| Field | Purpose |
|-------|---------|
| `id_column` | Sample ID search column for `find_sample` |
| `viewer` | Frontend viewer key (`mcq`, `code_problem`, …) |
| `loader` | `Callable[[dict], tuple[DataFrame, dict]]` — params from UI controls |
| `overview` | `Callable[[DataFrame, dict], dict]` — metrics/tables |
| `controls` | Zero-arg callable returning pre-load select controls |
| `filters` | Filter schema (multiselect, text, radio, date_range) |
| `sample_extras` | Optional per-row extras (model runs, solutions, …) |
| `supports_private_tests` | Enables LiveCodeBench private-test decoding in the UI |
| `cache_key` | On-disk cache dir for inspect CLI (`descriptor.cache_key` or config `loader`) |

Row counts on the catalog use `entry.row_count` from YAML when set; otherwise the loader runs once per dataset. `get_catalog()` formats each count once and reuses it for sidebar and home table rows.

Row counts (`row_count.py`), the inspect CLI (`scripts/inspect_dataset.py`), and API handlers all use `get_descriptor(dataset_id)` — there is no separate loader registry.

`loader: hf_benchmark` entries are auto-registered with `overview_generic()` plus reusable filter candidates for common benchmark columns (`subject`, `category`, `domain`, `difficulty`, `level`, etc.). The frontend hides generated filters whose columns are absent in the loaded frame.

## API endpoints

All endpoints are registered with `@app.api(name="…")` in `server.py` and callable via `@gradio/client` or `gradio_client`:

| API name | Parameters | Returns |
|----------|------------|---------|
| `get_catalog` | — | Categories, dataset list, home table rows |
| `get_dataset_meta` | `dataset_id` | Description, archetype, `viewer`, controls, filters, `id_column`, Hub `readme` |
| `get_filter_options` | `dataset_id`, `params_json` | Column names and unique filter values after load |
| `get_overview` | `dataset_id`, `params_json`, `filters_json` | Metrics and tables |
| `get_sample` | `dataset_id`, `index`, `params_json`, `filters_json` | Row + extras at index |
| `find_sample` | `dataset_id`, `id_value`, `params_json`, `filters_json` | Row + extras by id column |
| `decode_private_tests` | `raw` | Decoded LiveCodeBench private test cases |

`params_json` and `filters_json` are JSON strings (or dicts) matching control/filter names from `get_dataset_meta`.

Filter application and option discovery are schema-driven in `api/filters.py` and `api/service.py` — no per-dataset `if dataset_id == …` branches for standard filter types. `find_sample` is available via the API for programmatic lookup by `id_column`; the Sample Inspector browses by index only.

## Caching

- **Loaders:** `@loader_cache` in `loaders/cache.py` — in-process memoization for the server lifetime. Call `load_<name>.clear()` in tests.
- **On-disk:** `data/cache/<key>/` via `cache_dir()` — created on first load, shown by inspect CLI.
- **Hugging Face:** standard HF hub cache for downloaded datasets.

## CORS and static frontend

CORS middleware is registered at module level in `server.py`. Allowed origins default to `http://localhost:3000`; override with comma-separated `CORS_ORIGINS`.

When `frontend/out/` exists (after `npm run build`), `server.py` mounts:

- `/_next/*` — Next.js static assets
- `/` and `/dataset/{id}` — `index.html` (client-side routing)

## Adding a new API endpoint

Only needed for genuinely new capabilities (not per-dataset). Pattern:

```python
@app.api(name="my_endpoint")
def api_my_endpoint(arg: str) -> dict:
    return {"result": arg}
```

Register the handler in `api/service.py` and add a wrapper in `frontend/lib/api.ts`.

## Adding a new dataset

Register a `DatasetDescriptor` in `api/dataset_registry.py`, or add a `loader: hf_benchmark` YAML entry for auto-registration. See [dataset-system.md](dataset-system.md) and [how-to/add-dataset.md](how-to/add-dataset.md). `server.py` does not need changes for standard datasets.
