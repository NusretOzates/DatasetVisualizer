# Dataset Visualizer Docs

Internal developer documentation for the Dataset Visualizer project.

## Contents

- [Adding a dataset](adding-a-dataset.md) — 4-step checklist for new datasets
- [Datasets](datasets/)
  - [MMLU](datasets/mmlu.md)
  - [MMLU-Pro](datasets/mmlu_pro.md)
  - [LiveCodeBench v6](datasets/livecodebench.md)
  - [ArXiv Math 0526](datasets/arxivmath.md)

## Architecture

```
config/datasets.yaml  →  config.py (Pydantic)
                      →  registry.py (loaders + navigation)
                      →  app.py (st.navigation)
pages/<category>/<id>.py  →  loaders/<id>.py  →  data/cache/<id>/
```

Shared UI building blocks live under `src/dataset_visualizer/components/`:

- `page_layout.py` — Overview + Sample Inspector tabs
- `sample_navigator.py` — index slider, prev/next, ID search
- `charts.py` — Plotly bar, histogram, pie, timeline
- `mcq_viewer.py` — multiple-choice question rendering

Navigation is **config-driven**: new datasets require a YAML entry, loader, and page module — not changes to `app.py`.

## Run

```bash
uv run streamlit run src/dataset_visualizer/app.py
```
