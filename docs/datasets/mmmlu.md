# MMMLU

**Source:** [`openai/MMMLU`](https://huggingface.co/datasets/openai/MMMLU)  
**Archetype:** MCQ multilingual (14 locale configs)  
**Split:** `test` only

## Schema (normalized)

| Column | Type | Notes |
|--------|------|-------|
| `sample_id` | str | `{locale}_{row_index}` |
| `subject` | str | MMLU subject (57 categories) |
| `question` | str | Translated MMLU question |
| `choices` | list[str] | `[A, B, C, D]` option text |
| `answer_letter` | str | A–D |
| `language` | str | Loaded locale config (e.g. `DE_DE`, `JA_JP`) |
| `split` | str | Always `test` |

## Locales

Professional human translations of the MMLU test set into 14 locales:

`AR_XY`, `BN_BD`, `DE_DE`, `ES_LA`, `FR_FR`, `HI_IN`, `ID_ID`, `IT_IT`, `JA_JP`, `KO_KR`, `PT_BR`, `SW_KE`, `YO_NG`, `ZH_CN`

The combined `default` config (~197k rows, all locales) is excluded from the app; load one locale at a time.

## Visualization rationale

- **Subject bar chart** — same 57 subjects as MMLU; shows per-locale coverage.
- **Answer letter pie** — quick sanity check on label distribution.
- **Locale sidebar** — load one of 14 configs at a time (defaults to `DE_DE`).

## Loader

`load_dataset("openai/MMMLU", locale, split="test")` — page sidebar selects locale before load.

## Cache

`data/cache/mmmlu/`
