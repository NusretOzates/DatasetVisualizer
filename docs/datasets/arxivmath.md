# ArXiv Math 0526

**Sources:**

- Problems: [`MathArena/arxivmath-0526`](https://huggingface.co/datasets/MathArena/arxivmath-0526) (40 rows, `train` split)
- Model outputs: [`MathArena/arxivmath-0526_outputs`](https://huggingface.co/datasets/MathArena/arxivmath-0526_outputs) (960 rows, `train` split)

**Archetype:** Math competition with model runs  
**Status:** Implemented (Wave 2, Track C)  
**Loader:** `dataset_visualizer.loaders.arxivmath` (`load_problems`, `load_outputs`)

## Problems schema

| Column | Type | Description |
|---|---|---|
| `problem_idx` | `int64` → `str` | Problem index; cast to string before joins |
| `title` | `string` | Source arXiv paper title |
| `problem` | `string` | Problem statement (LaTeX/markdown) |
| `answer` | `string` | Gold final answer |
| `source` | `string` | arXiv identifier (e.g. `2605.01234`) |
| `authors` | `string` | Comma-separated author list |

## Outputs schema

| Column | Type | Description |
|---|---|---|
| `problem_idx` | `string` | Join key (cast to string in loader) |
| `model_name` | `string` | Display name in MathArena results |
| `model_config` | `string` | Path to model configuration |
| `idx_answer` | `int64` | Attempt index for model/problem pair |
| `correct` | `bool` | Whether parsed answer matched gold |
| `parsed_answer` | `string` | Extracted answer from model response |
| `gold_answer` | `string` | Gold answer used for scoring |
| `answer` | `string` | Full model response |
| `user_message` | `string` | Prompt sent to the model |
| `all_messages` | `string` | JSON-serialized full conversation (parsed lazily in UI) |
| `input_tokens` | `int64` | Input token count |
| `output_tokens` | `int64` | Output token count |
| `cost` | `float64` | Estimated API cost (USD) |
| `input_cost_per_tokens` | `float64` | Input price per million tokens |
| `output_cost_per_tokens` | `float64` | Output price per million tokens |
| `source` | `string` | arXiv identifier for source paper |

## Join gotcha

Problems store `problem_idx` as `int64`; outputs store it as `string`. Both loaders cast to `str` so merges on `problem_idx` work reliably.

## Cache

- Problems: `data/cache/arxivmath/`
- Model outputs: `data/cache/arxivmath_outputs/`

## Visualization rationale

- **Overview table** — only 40 problems; a full listing with title, arXiv id, and author count is the fastest way to orient.
- **Model accuracy bar chart** — aggregates `correct` by `model_name` from outputs to compare models at a glance.
- **Token scatter** — `input_tokens` vs `output_tokens` colored by `correct` surfaces cost/length patterns vs success.
- **Sample inspector** — two-column layout: problem + revealable gold answer on the left; paper metadata and per-problem model runs on the right.
- **Model runs sub-panel** — filter by `model_name`, tabular summary, parsed vs gold diff, expanders for full response and user prompt.
