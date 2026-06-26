# Dataset Visualizer Docs

Internal developer documentation.

## Before exploring code

1. [architecture/code-map.md](architecture/code-map.md) — capability → file lookup
2. [how-to/](how-to/) — recipes for common tasks
3. [dataset-system.md](dataset-system.md) — contracts and touchpoints

## Start here

| Goal | Read |
|------|------|
| Change overview, filters, or a viewer | [architecture/overview.md](architecture/overview.md) → [code-map.md](architecture/code-map.md) → [frontend.md](frontend.md) or [backend.md](backend.md) |
| Add a YAML-only Hub benchmark | [how-to/add-hf-benchmark.md](how-to/add-hf-benchmark.md) |
| Add a custom loader | [how-to/add-dataset.md](how-to/add-dataset.md) |
| Understand terms (`profile`, `viewer`, …) | [glossary.md](glossary.md) |
| User setup and commands | [../README.md](../README.md) |

## Datasets

**51 datasets** in [`config/datasets.yaml`](../config/datasets.yaml): 13 manual loaders + 38 `hf_benchmark` entries across eight categories.

Per-dataset notes (manual loaders and special cases):

| Dataset | Doc |
|---------|-----|
| MMLU | [datasets/mmlu.md](datasets/mmlu.md) |
| MMLU-Pro | [datasets/mmlu_pro.md](datasets/mmlu_pro.md) |
| GPQA Diamond | [datasets/gpqa_diamond.md](datasets/gpqa_diamond.md) |
| Global-MMLU | [datasets/global_mmlu.md](datasets/global_mmlu.md) |
| MMMLU | [datasets/mmmlu.md](datasets/mmmlu.md) |
| AIME 2026 | [datasets/aime_2026.md](datasets/aime_2026.md) |
| Humanity's Last Exam | [datasets/hle.md](datasets/hle.md) |
| LiveCodeBench v6 | [datasets/livecodebench.md](datasets/livecodebench.md) |
| SWE-Bench | [datasets/swe_bench.md](datasets/swe_bench.md) |
| τ³-Bench | [datasets/tau3_bench.md](datasets/tau3_bench.md) |
| ArXiv Math 0526 | [datasets/arxivmath.md](datasets/arxivmath.md) |
| ARC-AGI 2 | [datasets/arc_agi_2.md](datasets/arc_agi_2.md) |

`hf_benchmark` entries usually need no per-dataset doc — use the inspect CLI and [add-hf-benchmark.md](how-to/add-hf-benchmark.md).

## Architecture

```
config/datasets.yaml → config.py → dataset_registry.py → loaders/
    → api/service.py → server.py (@app.api) → frontend/ (@gradio/client)
```

Details: [architecture/overview.md](architecture/overview.md), [dataset-system.md](dataset-system.md), [architecture/code-map.md](architecture/code-map.md).

## Key modules

| Module | Role |
|--------|------|
| `server.py` | Gradio Server, CORS, API routes, static frontend mount |
| `api/dataset_registry.py` | `DatasetDescriptor` per config `id` |
| `api/service.py` | Catalog, meta, filters, overview, samples |
| `api/overview.py` / `generic_overview.py` | Overview metrics and tables |
| `api/filters.py` | Schema-driven filtering |
| `dataset_readme.py` | Fetch Hub README for Overview tab |
| `loaders/hf_benchmark.py` | Config-driven Hub loader |
| `loaders/benchmark_normalize.py` | Profile normalizers |

## Run and test

See [README.md](../README.md) for setup. Quick dev:

```bash
uv run dataset-viz
cd frontend && NEXT_PUBLIC_API_URL=http://localhost:7860 npm run dev
```

```bash
uv run pytest
uv run python scripts/inspect_dataset.py <dataset_id>
```

## Documentation policy

Update `docs/`, affected how-to files, and `README.md` when you change architecture, setup, or user-visible behavior.

Legacy redirect: [adding-a-dataset.md](adding-a-dataset.md) → how-to playbooks.
