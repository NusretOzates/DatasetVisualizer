# Dataset Visualizer

Interactive Streamlit app for exploring Hugging Face benchmark datasets with overview charts and per-sample inspection.

## Setup

```bash
uv sync
```

## Run

```bash
uv run streamlit run src/dataset_visualizer/app.py
```

Optional CLI entry point:

```bash
uv run dataset-viz
```

## Datasets

| Category | Dataset | Source |
|----------|---------|--------|
| Reasoning | MMLU | `cais/mmlu` |
| Reasoning | MMLU-Pro | `TIGER-Lab/MMLU-Pro` (coming soon) |
| Code | LiveCodeBench v6 | `livecodebench/code_generation_lite` (coming soon) |
| Math | ArXiv Math 0526 | `MathArena/arxivmath-0526` (coming soon) |

Configuration lives in [`config/datasets.yaml`](config/datasets.yaml). Add datasets by following [`docs/adding-a-dataset.md`](docs/adding-a-dataset.md).

## Cache

Downloaded data is cached under `data/cache/<dataset_id>/` (gitignored). First load may take a while; subsequent runs reuse the cache via Streamlit `@st.cache_data`.

## Development

```bash
uv run pytest
uv run ruff check src tests
uv run ruff format src tests
```

See [`docs/index.md`](docs/index.md) for architecture and per-dataset notes.
