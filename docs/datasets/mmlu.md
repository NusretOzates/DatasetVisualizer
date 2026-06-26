# MMLU

**Source:** [`cais/mmlu`](https://huggingface.co/datasets/cais/mmlu)  
**Archetype:** MCQ (4 options)  
**Status:** Implemented (Wave 1)

## Schema (normalized)

| Column | Type | Notes |
|--------|------|-------|
| `question` | str | Question text |
| `choices` | list[str] | Four answer options |
| `answer` | int | ClassLabel 0–3 |
| `answer_letter` | str | Normalized A–D |
| `subject` | str | Academic subject |
| `split` | str | Loaded split name |

## UI notes

- **Overview** — row count, subject count, active split.
- **Sample inspector** — shared MCQ viewer with highlighted correct answer.

## Loader

`load_dataset("cais/mmlu", "all", split="test")` by default. Page sidebar allows `test`, `validation`, or `dev`.

## Cache

`data/cache/mmlu/`
