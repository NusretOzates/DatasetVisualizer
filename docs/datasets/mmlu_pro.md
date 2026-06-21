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

## Visualization rationale

- **Category bar chart** — MMLU-Pro spans 14 disciplines; distribution shows coverage.
- **Option count histogram** — Highlights variable 8–10 option sets after N/A filtering.
- **Source provenance table** — `src` tags show which upstream benchmarks contributed each item.
- **Dynamic MCQ inspector** — Variable option count uses shared `mcq_viewer` with filtered `options`.
- **Chain-of-thought expander** — Long `cot_content` is shown read-only on demand to avoid clutter.

## Loader

`load_dataset("TIGER-Lab/MMLU-Pro", split="test")` by default. Page sidebar allows `test` or `validation`. Options are filtered to match official eval behavior (drop `"N/A"` entries).

## Cache

`data/cache/mmlu_pro/`
