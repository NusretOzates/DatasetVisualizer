# LiveCodeBench v6

**Source:** [`livecodebench/code_generation_lite`](https://huggingface.co/datasets/livecodebench/code_generation_lite) — `test6.jsonl` (release v6, 175 problems)  
**Archetype:** Code generation with embedded test harnesses  
**Status:** Implemented (Wave 2, Track B)  
**Loader:** `dataset_visualizer.loaders.livecodebench.load_livecodebench`

## Schema

| Column | Type (normalized) | Notes |
|--------|-------------------|-------|
| `question_title` | string | Short problem title |
| `question_content` | string | Full statement (markdown/LaTeX) |
| `starter_code` | string | Optional Python scaffold (may be empty) |
| `platform` | string | `leetcode`, `atcoder`, or `codeforces` |
| `question_id` | string | Stable problem identifier |
| `contest_id` | string | Source contest id |
| `contest_date` | datetime | Parsed from ISO string |
| `difficulty` | string | `easy`, `medium`, or `hard` |
| `public_test_cases` | `list[dict]` | Parsed JSON; each case has `input`, `output`, `testtype` |
| `private_test_cases` | string (raw) | Lazy-decoded on sample view (JSON or base64+zlib+pickle) |
| `metadata` | dict | Parsed JSON; `func_name` present for functional tests |
| `public_test_count` | int | Derived: `len(public_test_cases)` |

### Test case shape

```json
{"input": "...", "output": "...", "testtype": "stdin"}
```

`testtype` is either `stdin` (run as script with stdin/stdout) or `functional` (call `metadata["func_name"]` with parsed args).

### Private test decoding

Official LiveCodeBench stores private cases as a base64-encoded, zlib-compressed pickle of a JSON string. The loader keeps the raw string; `decode_private_test_cases()` tries `json.loads` first, then falls back to the compressed path (see `lcb_runner/benchmarks/code_generation.py`).

## Loading

```python
from huggingface_hub import hf_hub_download
from datasets import load_dataset

path = hf_hub_download("livecodebench/code_generation_lite", "test6.jsonl", repo_type="dataset")
ds = load_dataset("json", data_files=path, split="train")
```

Do **not** use `load_dataset("livecodebench/code_generation_lite", ...)` — the dataset script is incompatible with `datasets>=5`.

## Visualization rationale

- **Difficulty × platform stacked bar:** Shows benchmark composition across sources and hardness levels.
- **Contest date timeline:** Highlights the temporal evaluation window (contamination control).
- **Public test table:** Core inspectability — inputs, outputs, and harness type per case.
- **Private tests expander:** Decoded on demand with a row cap to avoid UI freezes on large case sets.
- **Functional metadata:** Surfaces `func_name` when tests are not stdin-based.

## Cache

Downloaded JSONL is cached by Hugging Face Hub; loader metadata uses `data/cache/livecodebench/`.
