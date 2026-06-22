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
                      →  registry.py (LOADER_REGISTRY)
                      →  loaders/<module>.py (@loader_cache)
                      →  api/service.py (handlers + JSON payloads)
                      →  server.py (gradio.Server API)
                      →  frontend/ (Next.js + @gradio/client)
```

Details, naming rules, and the full touchpoint list: [dataset-system.md](dataset-system.md).

## Shared modules

| Module | Purpose |
|--------|---------|
| `server.py` | `gradio.Server` entry point and `@app.api` routes |
| `api/service.py` | Dataset loading, filters, overview payloads, sample API |
| `api/chart_data.py` | Chart JSON builders for the React frontend |
| `api/serializers.py` | DataFrame/row JSON serialization |
| `loaders/cache.py` | `@loader_cache` decorator (replaces Streamlit cache) |
| `components/mcq_viewer.py` | MCQ helper functions (letter resolution, option formatting) |

Column contracts per archetype: [dataset-system.md § Column contracts](dataset-system.md#column-contracts-python-helpers).

## Inspect CLI

```bash
uv run python scripts/inspect_dataset.py <dataset_id>
```

`<dataset_id>` is the config `id` (e.g. `mmlu`, `swe_bench_verified`). The CLI calls `loader()` with no arguments — loaders must define safe defaults. See [dataset-system.md § Loader contract](dataset-system.md#loader-contract).

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

```bash
cd frontend && npm install && npm run build && cd ..
uv run dataset-viz
```

Open http://localhost:7860 — the Gradio server serves the built React app and API on the same origin.
