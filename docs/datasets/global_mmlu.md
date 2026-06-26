# Global-MMLU

**Source:** [`CohereLabs/Global-MMLU`](https://huggingface.co/datasets/CohereLabs/Global-MMLU)  
**Archetype:** MCQ multilingual (42 language configs)  
**Splits:** `dev` (default in app) and `test`

## Schema (normalized)

| Column | Type | Notes |
|--------|------|-------|
| `sample_id` | str | Unique question id |
| `subject` | str | Academic subject |
| `subject_category` | str | STEM / Humanities / etc. |
| `question` | str | Translated MMLU question |
| `choices` | list[str] | `[option_a, option_b, option_c, option_d]` |
| `answer_letter` | str | A–D |
| `language` | str | Loaded language config |
| `split` | str | `dev` or `test` |
| `cultural_sensitivity_label` | str | CS (culturally sensitive) or CA (agnostic) |
| `required_knowledge` | list[str] | Parsed annotation votes |
| `culture`, `region`, `country` | list[str] | Parsed annotation lists |

## UI notes

- **Overview** — row count, subject count, language, split.
- **Controls** — language and split selects load one config at a time (defaults to `en` + `dev`).
- **Sample inspector** — shared MCQ viewer.

## Loader

`load_dataset("CohereLabs/Global-MMLU", language, split=split)` — page sidebar selects language and split before load.

## Cache

`data/cache/global_mmlu/`
