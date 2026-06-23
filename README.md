# Dataset Visualizer

Interactive explorer for Hugging Face benchmark datasets. The app uses a **Gradio Server** backend ([`gradio.Server`](https://huggingface.co/blog/introducing-gradio-server)) and a **Next.js** React frontend.

## Setup

```bash
uv sync
cp .env.example .env
cd frontend && npm install
```

Set `HF_TOKEN` in `.env` to your [Hugging Face access token](https://huggingface.co/settings/tokens). The app loads `.env` at startup; `huggingface_hub` uses `HF_TOKEN` automatically for faster downloads and higher rate limits. Without a token, downloads still work but may be slower.

## Run (development)

Start the Gradio API backend:

```bash
uv run dataset-viz
```

In a second terminal, start the Next.js frontend (proxies API calls to port 7860):

```bash
cd frontend
NEXT_PUBLIC_API_URL=http://localhost:7860 npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

Optional direct backend launch:

```bash
uv run python src/dataset_visualizer/server.py
```

## Production build

Build the static Next.js export and serve it from the Gradio server. Start the backend first so the build can fetch the catalog for static routes:

```bash
uv run dataset-viz   # terminal 1 — keep running
cd frontend
NEXT_PUBLIC_API_URL=http://localhost:7860 npm run build
cd ..
```

The backend serves `frontend/out/` at `/` when the build exists.

## Datasets

| Category | Dataset | Source |
|----------|---------|--------|
| Reasoning | MMLU | `cais/mmlu` |
| Reasoning | MMLU-Pro | `TIGER-Lab/MMLU-Pro` |
| Reasoning | GPQA Diamond | `Idavidrein/gpqa` (`gpqa_diamond`) |
| Reasoning | Global-MMLU | `CohereLabs/Global-MMLU` |
| Reasoning | MMMLU | `openai/MMMLU` |
| Reasoning | Humanity's Last Exam | `cais/hle` |
| Code | LiveCodeBench v6 | `livecodebench/code_generation_lite` (`test6.jsonl`) |
| Code | SWE-Bench Verified | `SWE-bench/SWE-bench_Verified` |
| Code | SWE-Bench Multilingual | `SWE-bench/SWE-bench_Multilingual` |
| Code | SWE-Bench PRO | `Contextbench/SWE-bench_Pro` |
| Math | AIME 2026 | `MathArena/aime_2026` |
| Math | ArXiv Math 0526 | `MathArena/arxivmath-0526` + `MathArena/arxivmath-0526_outputs` |

Configuration lives in [`config/datasets.yaml`](config/datasets.yaml). To add a dataset, follow [`docs/adding-a-dataset.md`](docs/adding-a-dataset.md) and the full reference in [`docs/dataset-system.md`](docs/dataset-system.md). **Update docs and this README when you change setup or architecture.**

Per-dataset schema notes: [`docs/index.md`](docs/index.md).

## Cache

Per-dataset cache directories are created under `data/cache/<loader_key>/` (gitignored) and shown by the inspect CLI. Hugging Face dataset downloads are cached in the standard Hugging Face cache (location varies by environment). Loader keys: `mmlu`, `mmlu_pro`, `gpqa`, `global_mmlu`, `mmmlu`, `aime_2026`, `hle`, `livecodebench`, `swe_bench`, `arxivmath`, `arxivmath_outputs`. First load may take a while; subsequent runs reuse in-process loader caching and the Hugging Face cache.

## Inspect CLI

Inspect schema and a sample row without opening the app:

```bash
uv run python scripts/inspect_dataset.py mmlu
uv run python scripts/inspect_dataset.py mmlu_pro
uv run python scripts/inspect_dataset.py gpqa_diamond
uv run python scripts/inspect_dataset.py global_mmlu
uv run python scripts/inspect_dataset.py mmmlu
uv run python scripts/inspect_dataset.py aime_2026
uv run python scripts/inspect_dataset.py hle
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
cd frontend && npm run lint
```

See [`docs/index.md`](docs/index.md) for architecture and per-dataset notes.
