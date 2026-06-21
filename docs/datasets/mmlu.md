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

## Visualization rationale

- **Subject bar chart** — MMLU spans 57 subjects; distribution shows coverage.
- **Answer letter pie** — Sanity check for class balance.
- **MCQ sample inspector** — Uniform 4-option format suits shared `mcq_viewer`.

## Loader

`load_dataset("cais/mmlu", "all", split="test")` by default. Page sidebar allows `test`, `validation`, or `dev`.

## Cache

`data/cache/mmlu/`
