# Dataset Visualizer Docs

Internal developer documentation for the Dataset Visualizer project.

## Before exploring code

Read [architecture/code-map.md](architecture/code-map.md) first to locate relevant files.  
Prefer [how-to/](how-to/) recipes over full-codebase search for common tasks.

## Start here

- **Changing how a visualizer feature works?** → [Architecture overview](architecture/overview.md) → [Code map](architecture/code-map.md) → [Frontend](frontend.md) or [Backend](backend.md)
- **Adding or modifying a dataset?** → [How to add a dataset](how-to/add-dataset.md) (YAML-only benchmarks: [add-hf-benchmark.md](how-to/add-hf-benchmark.md))
- **[Dataset system reference](dataset-system.md)** — architecture, touchpoint checklist, loader/API contracts, archetype table, templates, pitfalls
- **[Glossary](glossary.md)** — domain terms (`id`, `profile`, `viewer`, `hf_benchmark`, …)
- [Backend (Gradio Server)](backend.md) — API endpoints, caching, static frontend mount
- [Frontend (Next.js)](frontend.md) — React app structure, dev workflow, viewers

Legacy link: [adding-a-dataset.md](adding-a-dataset.md) redirects to the how-to playbooks.

## Datasets

The catalog has **51 datasets** (13 manual loaders + 38 `hf_benchmark` auto-registered entries) across 10 categories in [`config/datasets.yaml`](../config/datasets.yaml).

Per-dataset schema and visualization notes (hand-written loaders and special cases):

- [MMLU](datasets/mmlu.md)
- [MMLU-Pro](datasets/mmlu_pro.md)
- [GPQA Diamond](datasets/gpqa_diamond.md)
- [Global-MMLU](datasets/global_mmlu.md)
- [MMMLU](datasets/mmmlu.md)
- [AIME 2026](datasets/aime_2026.md)
- [Humanity's Last Exam](datasets/hle.md)
- [LiveCodeBench v6](datasets/livecodebench.md)
- [SWE-Bench](datasets/swe_bench.md)
- [τ³-Bench](datasets/tau3_bench.md)
- [ArXiv Math 0526](datasets/arxivmath.md)
- [ARC-AGI 2](datasets/arc_agi_2.md)

`hf_benchmark` entries do not need individual docs unless schema or visualization is non-obvious — use the inspect CLI and [add-hf-benchmark.md](how-to/add-hf-benchmark.md).

## Architecture (summary)

```
config/datasets.yaml  →  config.py (Pydantic)
                      →  api/dataset_registry.py (DATASET_REGISTRY)
                      →  loaders/<module>.py or loaders/hf_benchmark.py (@loader_cache)
                      →  loaders/benchmark_normalize.py (profile normalizers)
                      →  api/service.py (orchestration)
                      →  api/filters.py, api/overview.py, api/generic_overview.py
                      →  server.py (gradio.Server API)
                      →  frontend/ (Next.js + @gradio/client)
```

Details, naming rules, and the full touchpoint list: [dataset-system.md](dataset-system.md). Public capability entry points: [architecture/code-map.md](architecture/code-map.md).

## Shared modules

| Module | Purpose |
|--------|---------|
| `server.py` | `gradio.Server` entry point, CORS, `@app.api` routes, static frontend mount |
| `api/dataset_registry.py` | Single registration point: `DatasetDescriptor` per config `id` |
| `api/service.py` | Catalog, meta, filter options, overview, and sample handlers |
| `api/filters.py` | Schema-driven `apply_filters()` and `build_filter_options()` |
| `api/overview.py` | Per-dataset overview builders (manual loaders) |
| `api/generic_overview.py` | Reusable overview for `hf_benchmark` entries |
| `api/chart_data.py` | Chart JSON builders for the React frontend |
| `api/serializers.py` | DataFrame/row JSON serialization |
| `loaders/hf_benchmark.py` | Config-driven Hub download + normalization |
| `loaders/benchmark_normalize.py` | Profile-specific column normalization |
| `loaders/cache.py` | `@loader_cache` in-process memoization |
| `utils/mcq.py` | MCQ helper functions (letter resolution, option formatting) |

Column contracts per archetype: [dataset-system.md § Column contracts](dataset-system.md#column-contracts-python-helpers).

## Inspect CLI

```bash
uv run python scripts/inspect_dataset.py <dataset_id>
```

`<dataset_id>` is the config `id` (e.g. `mmlu`, `humaneval`, `arc_agi_2`). The CLI calls `get_descriptor(id).loader({})` — loaders must define safe defaults for an empty params dict. Cache path uses `descriptor.cache_key` or config `loader`. See [dataset-system.md § Loader contract](dataset-system.md#loader-contract).

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

**Always update docs when you change setup, architecture, or developer workflows.** At minimum touch `docs/index.md`, the relevant topic file (`backend.md`, `frontend.md`, `dataset-system.md`, `how-to/`), and `README.md` when user-facing behavior changes.
