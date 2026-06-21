# Dataset Visualizer Docs

Internal developer documentation for the Dataset Visualizer project.

## Contents

- [Adding a dataset](adding-a-dataset.md) — 4-step checklist for new datasets
- [Datasets](datasets/)
  - [MMLU](datasets/mmlu.md)
  - [MMLU-Pro](datasets/mmlu_pro.md)
  - [GPQA Diamond](datasets/gpqa_diamond.md)
  - [Global-MMLU](datasets/global_mmlu.md)
  - [LiveCodeBench v6](datasets/livecodebench.md)
  - [SWE-Bench](datasets/swe_bench.md)
  - [ArXiv Math 0526](datasets/arxivmath.md)

## Architecture

```
config/datasets.yaml  →  config.py (Pydantic)
                      →  registry.py (loaders + navigation)
                      →  app.py (st.navigation)
pages/<category>/<id>.py  →  loaders/<loader>.py  →  data/cache/<cache_key>/
```

Shared UI building blocks live under `src/dataset_visualizer/components/`:

- `page_layout.py` — Overview + Sample Inspector tabs
- `sample_navigator.py` — index slider, prev/next, ID search
- `charts.py` — Plotly bar, histogram, pie, timeline, scatter
- `mcq_viewer.py` — multiple-choice question rendering
- `code_problem_viewer.py` — code problem statement and test cases

Navigation is **config-driven**: new datasets require a YAML entry, loader, registry line, and page module — not changes to `app.py`.

## Inspect CLI

```bash
uv run python scripts/inspect_dataset.py <dataset_id>
```

Valid ids match `config/datasets.yaml` entries: `mmlu`, `mmlu_pro`, `gpqa_diamond`, `global_mmlu`, `livecodebench_v6`, `swe_bench_verified`, `swe_bench_multilingual`, `swe_bench_pro`, `arxivmath_0526`.

## Run

```bash
uv run streamlit run src/dataset_visualizer/app.py
```
