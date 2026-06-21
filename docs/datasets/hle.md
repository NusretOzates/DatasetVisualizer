# Humanity's Last Exam (HLE)

**Source:** [`cais/hle`](https://huggingface.co/datasets/cais/hle) (`test` split, 2,500 questions)  
**Archetype:** Academic QA (exact-match and multiple-choice, optional images)  
**Access:** Gated — accept terms on Hugging Face and set `HF_TOKEN` in `.env`.

## Raw HF schema

| Column | Type | Notes |
|--------|------|-------|
| `id` | str | Unique question id |
| `question` | str | Question text (MCQ options are inline in the prompt) |
| `image` | str | Data URI for multimodal questions; empty string when text-only |
| `image_preview` | image | Decoded preview image |
| `answer` | str | Correct exact-match string or MCQ letter |
| `answer_type` | str | `exactMatch` or `multipleChoice` |
| `author_name` | str | Contributor name |
| `rationale` | str | Expert solution explanation |
| `rationale_image` | image | Optional rationale figure |
| `raw_subject` | str | Fine-grained academic subject |
| `category` | str | Top-level subject category |
| `canary` | str | BIG-bench-style canary string |

## Schema (normalized)

| Column | Type | Notes |
|--------|------|-------|
| All raw columns | — | Preserved from Hugging Face |
| `has_image` | bool | True when `image` is non-empty |
| `split` | str | Always `test` |

## Visualization rationale

- **Category / subject bar charts** — show breadth of academic coverage.
- **Answer type pie** — exact-match vs multiple-choice mix.
- **Modality pie** — text-only vs multimodal questions.
- **Sample inspector** — question text, optional image, answer reveal, rationale expander.

## Loader

`load_dataset("cais/hle", split="test")` with `has_image` and `split` metadata.

## Cache

`data/cache/hle/`
