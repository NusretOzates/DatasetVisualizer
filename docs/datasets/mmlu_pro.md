# MMLU-Pro

**Source:** [`TIGER-Lab/MMLU-Pro`](https://huggingface.co/datasets/TIGER-Lab/MMLU-Pro)  
**Archetype:** MCQ with chain-of-thought  
**Status:** Implemented (Wave 2, Track A)

## Schema (normalized)

| Column | Type | Notes |
|--------|------|-------|
| `question_id` | str | Unique identifier |
| `question` | str | Question text |
| `options` | list[str] | Up to 10 choices; `"N/A"` placeholders removed in loader |
| `option_count` | int | Count of non-`N/A` options after filtering |
| `answer` | str | Correct answer letter (A–J) |
| `answer_index` | int | Zero-based index into the raw options list |
| `category` | str | Discipline (14 categories) |
| `src` | str | Provenance / upstream source tag |
| `cot_content` | str | Chain-of-thought rationale (often long) |
| `split` | str | Loaded split name (`test` or `validation`) |

## UI notes

- **Overview** — row count, category count, split; source-provenance table (top `src` tags).
- **Sample inspector** — variable option count MCQ; chain-of-thought in a collapsible section.

## Loader

`load_dataset("TIGER-Lab/MMLU-Pro", split="test")` by default. Page sidebar allows `test` or `validation`. Options are filtered to match official eval behavior (drop `"N/A"` entries).

## Cache

`data/cache/mmlu_pro/`
