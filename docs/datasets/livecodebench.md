# LiveCodeBench v6

**Source:** [`livecodebench/code_generation_lite`](https://huggingface.co/datasets/livecodebench/code_generation_lite) — `test6.jsonl` only  
**Archetype:** Code generation with test harnesses  
**Status:** Stub (Wave 2)

## Planned schema

| Column | Notes |
|--------|-------|
| `question_content` | Problem statement (markdown) |
| `starter_code` | Optional Python starter |
| `public_test_cases` | Parsed JSON list of I/O cases |
| `private_test_cases` | Lazy-decoded compressed cases |
| `platform` | leetcode / atcoder / codeforces |
| `difficulty` | easy / medium / hard |
| `contest_date` | Parsed datetime |

## Planned visualization

- Difficulty × platform stacked bar, contest date timeline
- Public test table, private tests on expand

## Gotcha

Do **not** use `load_dataset("livecodebench/code_generation_lite", ...)` — use `hf_hub_download` + `load_dataset("json", ...)`.
