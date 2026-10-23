# Gated benchmarks — access notes

Some catalog benchmarks live in gated Hugging Face repos. They register like
any other dataset, but loading fails until the account in `HF_TOKEN` has
accepted the upstream terms. This page records what is known, what was
verified without access, and what to check on first successful load. Do not
fill gaps with invented content: if a field is not listed here as verified,
treat it as unconfirmed.

## OfficeQA Pro v2 (`officeqa_pro_v2`)

- **Repo:** `databricks/officeqa-pro-v2` (gated, auto-approval form).
- **Status:** the project token had not accepted the terms as of 2026-10-23;
  live loads return the Hub gating error (same pattern as GAIA / GPQA).
- **Schema (from the official dataset card, not a live load):** config
  `officeqa_pro_v2`, split `train`, 90 rows, columns `uid`, `question`,
  `answer`, `source_docs`, `source_files`. The catalog uses `uid` as
  `id_column`.
- **Verify on first access:** run `uv run python scripts/inspect_dataset.py officeqa_pro_v2`;
  confirm the columns above, the row count, and that the generic overview
  and filters behave; then update this note and the catalog entry if the
  card and the live schema disagree.

## ChartoGraphy (`chartography`)

- **Repo:** `surgeai/chartography` (access-restricted; the Hub API returns
  404 for accounts without access).
- **Status:** not loaded live as of 2026-10-23.
- **Schema (from the official dataset card):** split `test`, 100 rows,
  columns `task_id`, `prompt`, `golden_answer`, `chart_path`,
  `domain_combined`, `source_type`, `source_url`. Chart images are stored
  as files in the repo, referenced by `chart_path`.
- **Verify on first access:** run `uv run python scripts/inspect_dataset.py chartography`;
  confirm columns and row count. Only then add chart rendering to the
  viewer (for example by resolving `chart_path` against the repo), using
  the pattern from the ZeroBench viewer — do not construct image URLs
  before the path layout is confirmed live.

## OSWorld V2.1 (`osworld_v21`)

- **Repo:** task classes in `xlangai/osworld_v2_tasks` (gated by design, to
  reduce benchmark leakage); release pinned by
  `benchmark_releases/osworld-v2.1.json` in `xlang-ai/OSWorld-V2`.
- **Status:** catalog rows intentionally contain only public release
  manifest data (task file, SHA-256, size, source revision). Task
  instructions are inside the gated `task_*.py` files and are not mirrored.
- **Verify on first access:** if access is granted, evaluate parsing the
  task classes for instruction text before changing the loader. Do not
  invent task descriptions from filenames in the meantime.
