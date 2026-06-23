# Dataset Visualizer

Interactive explorer for Hugging Face benchmark datasets. The app uses a **Gradio Server** backend ([`gradio.Server`](https://huggingface.co/blog/introducing-gradio-server)) and a **Next.js** React frontend with benchmark-aware overviews, filters, Markdown/LaTeX rendering, and per-sample inspection.

## Setup

```bash
uv sync
cp .env.example .env
cd frontend && npm install
```

Set `HF_TOKEN` in `.env` to your [Hugging Face access token](https://huggingface.co/settings/tokens). The app loads `.env` at startup; `huggingface_hub` uses `HF_TOKEN` automatically for faster downloads and higher rate limits. Without a token, downloads still work but may be slower. Some datasets (e.g. GPQA Diamond, GAIA) are gated and require a token with accepted terms.

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

The catalog in [`config/datasets.yaml`](config/datasets.yaml) currently lists **51 benchmarks** across reasoning, knowledge, code, long-context, instruction-following, tool-calling, assistant-tasks, games, forecasting, and math.

- **13 manual loaders** — tailored normalization and overviews (MMLU, SWE-bench, LiveCodeBench, …).
- **38 `hf_benchmark` entries** — YAML-only registration; shared loader, profile-based normalization, and generic overviews.

To add a dataset:

- Standard Hub benchmark → [`docs/how-to/add-hf-benchmark.md`](docs/how-to/add-hf-benchmark.md)
- Custom loader logic → [`docs/how-to/add-dataset.md`](docs/how-to/add-dataset.md)

Full reference: [`docs/dataset-system.md`](docs/dataset-system.md). **Update docs and this README when you change setup or architecture.**

Per-dataset schema notes (manual loaders and special cases): [`docs/index.md`](docs/index.md).

## Cache

Per-dataset cache directories are created under `data/cache/<key>/` (gitignored) and shown by the inspect CLI. Keys are typically the config `id` for `hf_benchmark` entries, or the loader/cache_key for manual loaders (e.g. `swe_bench` shared by three SWE variants). Hugging Face dataset downloads are also cached in the standard Hugging Face hub cache. First load may take a while; subsequent runs reuse in-process loader caching and the Hugging Face cache.

## Inspect CLI

Inspect schema and a sample row without opening the app:

```bash
uv run python scripts/inspect_dataset.py <dataset_id>
```

`<dataset_id>` is the config `id` from `config/datasets.yaml` (e.g. `mmlu`, `humaneval`, `arc_agi_2`). On error, the CLI prints all valid ids. Prints columns, dtypes, row count, one truncated sample row, and the on-disk cache path.

Examples:

```bash
uv run python scripts/inspect_dataset.py mmlu
uv run python scripts/inspect_dataset.py humaneval
uv run python scripts/inspect_dataset.py arc_agi_2
uv run python scripts/inspect_dataset.py arxivmath_0526
```

## Development

```bash
uv run pytest
uv run ruff check src tests scripts
uv run ruff format src tests scripts
cd frontend && npm run lint
cd frontend && npm run typecheck
```

See [`docs/index.md`](docs/index.md) for architecture, glossary, and per-dataset notes.
