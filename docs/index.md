# Dataset Visualizer Docs

Internal developer documentation for the Dataset Visualizer project.

## Start here

- **[Dataset system reference](dataset-system.md)** — architecture, touchpoint checklist, loader/page/test contracts, archetype table, templates, pitfalls. **Read this before opening source files** when adding or modifying datasets.
- [Adding a dataset](adding-a-dataset.md) — short checklist (links to the system reference)

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
                      →  api/service.py (dataset handlers + JSON payloads)
                      →  server.py (gradio.Server API)
                      →  frontend/ (Next.js React UI)

loaders/<loader>.py  →  data/cache/<cache_key>/
```

Details, naming rules, and the full touchpoint list: [dataset-system.md](dataset-system.md).

## Shared modules

| Module | Purpose |
|--------|---------|
| `api/service.py` | Dataset loading, filters, overview payloads, sample API |
| `api/chart_data.py` | Chart JSON builders for the React frontend |
| `api/serializers.py` | DataFrame/row JSON serialization |
| `components/mcq_viewer.py` | MCQ helper functions (letter resolution, option formatting) |

Column contracts per archetype: [dataset-system.md § Component column contracts](dataset-system.md#component-column-contracts).

## Inspect CLI

```bash
uv run python scripts/inspect_dataset.py <dataset_id>
```

`<dataset_id>` is the config `id` (e.g. `mmlu`, `swe_bench_verified`). The CLI calls `loader()` with no arguments — loaders must define safe defaults. See [dataset-system.md § Loader contract](dataset-system.md#loader-contract).

## Run

Backend (Gradio API on port 7860):

```bash
uv run dataset-viz
```

Frontend (Next.js on port 3000):

```bash
cd frontend && NEXT_PUBLIC_API_URL=http://localhost:7860 npm run dev
```
