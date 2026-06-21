# Dataset Visualizer

Interactive Streamlit app for exploring Hugging Face benchmark datasets with overview charts and per-sample inspection.

## Setup

```bash
uv sync
cp .env.example .env
```

Set `HF_TOKEN` in `.env` to your [Hugging Face access token](https://huggingface.co/settings/tokens). The app loads `.env` at startup; `huggingface_hub` uses `HF_TOKEN` automatically for faster downloads and higher rate limits. Without a token, downloads still work but may be slower.

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
| Reasoning | MMLU-Pro | `TIGER-Lab/MMLU-Pro` |
| Reasoning | GPQA Diamond | `Idavidrein/gpqa` (`gpqa_diamond`) |
| Reasoning | Global-MMLU | `CohereLabs/Global-MMLU` |
| Reasoning | AIME 2026 | `MathArena/aime_2026` |
| Code | LiveCodeBench v6 | `livecodebench/code_generation_lite` (`test6.jsonl`) |
| Code | SWE-Bench Verified | `SWE-bench/SWE-bench_Verified` |
| Code | SWE-Bench Multilingual | `SWE-bench/SWE-bench_Multilingual` |
| Code | SWE-Bench PRO | `Contextbench/SWE-bench_Pro` |
| Math | ArXiv Math 0526 | `MathArena/arxivmath-0526` + `MathArena/arxivmath-0526_outputs` |

Configuration lives in [`config/datasets.yaml`](config/datasets.yaml). To add a dataset, follow [`docs/adding-a-dataset.md`](docs/adding-a-dataset.md) and the full reference in [`docs/dataset-system.md`](docs/dataset-system.md).

Per-dataset schema notes: [`docs/index.md`](docs/index.md).

## Cache

Downloaded data is cached under `data/cache/<loader_key>/` (gitignored). Loader keys: `mmlu`, `mmlu_pro`, `gpqa`, `global_mmlu`, `aime_2026`, `livecodebench`, `swe_bench`, `arxivmath`, `arxivmath_outputs`. First load may take a while; subsequent runs reuse the cache via Streamlit `@st.cache_data`.

## Inspect CLI

Inspect schema and a sample row without opening the app:

```bash
uv run python scripts/inspect_dataset.py mmlu
uv run python scripts/inspect_dataset.py mmlu_pro
uv run python scripts/inspect_dataset.py gpqa_diamond
uv run python scripts/inspect_dataset.py global_mmlu
uv run python scripts/inspect_dataset.py aime_2026
uv run python scripts/inspect_dataset.py livecodebench_v6
uv run python scripts/inspect_dataset.py swe_bench_verified
uv run python scripts/inspect_dataset.py swe_bench_multilingual
uv run python scripts/inspect_dataset.py swe_bench_pro
uv run python scripts/inspect_dataset.py arxivmath_0526
```

Prints columns, dtypes, row count, one truncated sample row, and the on-disk cache path.

## Development

```bash
uv run pytest
uv run ruff check src tests scripts
uv run ruff format src tests scripts
```

See [`docs/index.md`](docs/index.md) for architecture and per-dataset notes.
