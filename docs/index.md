# Dataset Visualizer Docs

Internal developer documentation for the Dataset Visualizer project.

## Start here

- **[Dataset system reference](dataset-system.md)** — architecture, touchpoint checklist, loader/API contracts, archetype table, templates, pitfalls. **Read this before opening source files** when adding or modifying datasets.
- [Adding a dataset](adding-a-dataset.md) — short checklist (links to the system reference)
- [Backend (Gradio Server)](backend.md) — API endpoints, caching, static frontend mount
- [Frontend (Next.js)](frontend.md) — React app structure, dev workflow, viewers

## Datasets

Per-dataset schema and visualization notes:

- [MMLU](datasets/mmlu.md)
- [MMLU-Pro](datasets/mmlu_pro.md)
- [GPQA Diamond](datasets/gpqa_diamond.md)
- [Global-MMLU](datasets/global_mmlu.md)
- [MMMLU](datasets/mmmlu.md)
- [AIME 2026](datasets/aime_2026.md)
- [Humanity's Last Exam](datasets/hle.md)
- [LiveCodeBench v6](datasets/livecodebench.md)
- [SWE-Bench](datasets/swe_bench.md)
- [ArXiv Math 0526](datasets/arxivmath.md)

## Architecture (summary)

```
config/datasets.yaml  →  config.py (Pydantic)
                      →  api/dataset_registry.py (DATASET_REGISTRY)
                      →  loaders/<module>.py (@loader_cache)
                      →  api/service.py (orchestration)
                      →  api/filters.py, api/overview.py, api/serializers.py
                      →  server.py (gradio.Server API)
                      →  frontend/ (Next.js + @gradio/client)
```

Details, naming rules, and the full touchpoint list: [dataset-system.md](dataset-system.md).

## Shared modules

| Module | Purpose |
|--------|---------|
| `server.py` | `gradio.Server` entry point, CORS, `@app.api` routes, static frontend mount |
| `api/dataset_registry.py` | Single registration point: `DatasetDescriptor` per config `id` |
| `api/service.py` | Catalog, meta, filter options, overview, and sample handlers |
| `api/filters.py` | Schema-driven `apply_filters()` |
| `api/overview.py` | Per-dataset overview payload builders |
| `api/chart_data.py` | Chart JSON builders for the React frontend |
| `api/serializers.py` | DataFrame/row JSON serialization |
| `loaders/cache.py` | `@loader_cache` in-process memoization |
| `utils/mcq.py` | MCQ helper functions (letter resolution, option formatting) |

Column contracts per archetype: [dataset-system.md § Column contracts](dataset-system.md#column-contracts-python-helpers).

## Inspect CLI

```bash
uv run python scripts/inspect_dataset.py <dataset_id>
```

`<dataset_id>` is the config `id` (e.g. `mmlu`, `swe_bench_verified`). The CLI calls `get_descriptor(id).loader({})` — loaders must define safe defaults for an empty params dict. See [dataset-system.md § Loader contract](dataset-system.md#loader-contract).

## Run

### Development (hot-reload frontend)

Backend (Gradio API on port 7860):

```bash
uv run dataset-viz
```

Frontend (Next.js on port 3000):

```bash
cd frontend && npm install
NEXT_PUBLIC_API_URL=http://localhost:7860 npm run dev
```

### Production (single server)

Start the backend first so `npm run build` can fetch the catalog for static routes:

```bash
uv run dataset-viz
```

In another terminal:

```bash
cd frontend && npm install
NEXT_PUBLIC_API_URL=http://localhost:7860 npm run build && cd ..
```

Then restart or keep the backend running and open http://localhost:7860 — the Gradio server serves the built React app and API on the same origin.

## Documentation policy

**Always update docs when you change setup, architecture, or developer workflows.** At minimum touch `docs/index.md`, the relevant topic file (`backend.md`, `frontend.md`, `dataset-system.md`, `adding-a-dataset.md`), and `README.md` when user-facing behavior changes.
