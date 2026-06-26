# Dataset Visualizer

Interactive explorer for Hugging Face benchmark datasets. A **Gradio Server** backend ([`gradio.Server`](https://huggingface.co/blog/introducing-gradio-server)) plus a **Next.js** frontend: catalog browsing, summary overviews, schema-driven filters, Markdown/LaTeX rendering, and per-sample inspection.

Developer docs: [`docs/index.md`](docs/index.md)

## Setup

```bash
uv sync
cp .env.example .env
cd frontend && npm install
```

Set `HF_TOKEN` in `.env` to your [Hugging Face access token](https://huggingface.co/settings/tokens). The app loads `.env` at startup; `huggingface_hub` uses `HF_TOKEN` for faster downloads and higher rate limits. Without a token, downloads still work but may be slower. Gated datasets (GPQA Diamond, GAIA, HLE, …) require a token with accepted Hub terms.

## Run (development)

Backend (Gradio API on port 7860):

```bash
uv run dataset-viz
```

Frontend (Next.js on port 3000):

```bash
cd frontend
NEXT_PUBLIC_API_URL=http://localhost:7860 npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

### Pre-download (optional)

Warm the Hugging Face cache before starting the backend:

```bash
uv run pre-download --fast              # small smoke-test subset
uv run pre-download --id mmlu           # one dataset
uv run pre-download --category reasoning
uv run pre-download                     # full catalog (large)
uv run pre-download --skip-gated        # skip gated datasets
uv run pre-download --workers 8         # parallel downloads (default: 4)
```

Gated datasets print a warning when access fails — set `HF_TOKEN` and accept dataset terms on the Hub.

## Production build

Start the backend first so the build can fetch the catalog for static routes:

```bash
uv run dataset-viz   # terminal 1
cd frontend
NEXT_PUBLIC_API_URL=http://localhost:7860 npm run build
cd ..
```

The backend serves `frontend/out/` at `/` when the build exists.

## Datasets

[`config/datasets.yaml`](config/datasets.yaml) lists **51 benchmarks** in eight categories: reasoning, code, long context, instruction following, assistant tasks, games, forecasters, and math.

| Path | Count | Registration |
|------|------:|--------------|
| Manual loaders | 13 | Custom Python in `loaders/` + `DatasetDescriptor` |
| `hf_benchmark` | 38 | YAML-only; auto-registered |

Add a dataset:

- Standard Hub benchmark → [`docs/how-to/add-hf-benchmark.md`](docs/how-to/add-hf-benchmark.md)
- Custom loader logic → [`docs/how-to/add-dataset.md`](docs/how-to/add-dataset.md)

Full reference: [`docs/dataset-system.md`](docs/dataset-system.md)

### Visual audit

Every catalog dataset has a dedicated Sample Inspector viewer. Audit matrix: [`docs/audit/dataset-audit-matrix.md`](docs/audit/dataset-audit-matrix.md)

```bash
uv run python scripts/audit_datasets.py
```

Optional local screenshots: `uv run python scripts/capture_audit_screenshots.py` (writes to `docs/images/audit/`, gitignored).

Per-dataset schema notes: [`docs/index.md`](docs/index.md#datasets)

## Cache

Per-dataset cache directories live under `data/cache/<key>/` (gitignored). Keys are typically the config `id` for `hf_benchmark` entries, or `cache_key` / `loader` for manual loaders (e.g. three SWE-bench variants share `swe_bench`). Hugging Face hub cache is used for downloads. First load can be slow; subsequent requests reuse `@loader_cache` and on-disk caches.

## Inspect CLI

```bash
uv run python scripts/inspect_dataset.py <dataset_id>
```

`<dataset_id>` is the config `id` (e.g. `mmlu`, `humaneval`, `arc_agi_2`). Prints columns, dtypes, row count, one truncated sample row, and the cache path.

## Development

```bash
uv run pytest
uv run ruff check src tests scripts
uv run ruff format src tests scripts
cd frontend && npm run lint && npm run typecheck
```

## Screenshots

**Home** — browse benchmarks by category, archetype, and row count.

![Dataset catalog home page](docs/images/homepage.jpg)

**Overview** — metric cards and the Hub dataset README ([MMLU](https://huggingface.co/datasets/cais/mmlu), dev split).

![MMLU overview with metrics and README](docs/images/mmlu_homepage.jpg)

**Filters** — multiselect and radio filters ([HLE](https://huggingface.co/datasets/cais/hle)).

![HLE category, subject, and modality filters](docs/images/hle_filter_card.jpg)

**Sample Inspector** — archetype-specific viewers with Markdown/LaTeX, highlighted answers, and raw JSON.

MCQ ([MMLU](https://huggingface.co/datasets/cais/mmlu)):

![MMLU sample with highlighted correct answer](docs/images/mmlu_sample.jpg)

Multimodal academic QA ([HLE](https://huggingface.co/datasets/cais/hle)):

![HLE multimodal sample with chess board and exact answer](docs/images/hle_sample.jpg)

Math + model runs ([ArXiv Math 0526](https://huggingface.co/datasets/ArtificialAnalysis/arxivmath_0526)):

![ArXiv Math sample with LaTeX gold answer and model run table](docs/images/arxivmath_sample.jpg)

Issue resolution ([SWE-Bench PRO](https://huggingface.co/datasets/ScaleAI/SWE-bench_Pro)):

![SWE-Bench PRO sample with problem statement and patch sections](docs/images/swe_bench_pro_sample.jpg)
