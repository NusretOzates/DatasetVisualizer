# BrowseComp

**Source:** [openai/simple-evals](https://github.com/openai/simple-evals) (`browsecomp_eval.py`)  
**Paper:** [A Simple Yet Challenging Benchmark for Browsing Agents](https://arxiv.org/abs/2504.12516)  
**Archetype:** Browsing agent task  
**Loader:** `dataset_visualizer.loaders.browsecomp` (`load_browsecomp`)

BrowseComp measures whether agents can persistently search the open web for hard-to-find facts. Each item is a challenging question with a short reference answer. The upstream CSV stores encrypted `problem` and `answer` fields; the loader decrypts them with the per-dataset canary string (same logic as `browsecomp_eval.py`).

## Category

Registered under **Agentic tasks** alongside GAIA and other agent benchmarks — the paper frames BrowseComp as a browsing-agent evaluation, not long-context reading or generic knowledge QA.

## Normalized columns

| Column | Description |
|--------|-------------|
| `sample_id` | Stable id (`browsecomp_{row_index}`) |
| `question` | Decrypted browsing question |
| `answer` | Decrypted short reference answer |
| `question_preview` | Truncated question for overview tables |
| `problem_topic` | Topic label (`Art`, `Sports`, …) |
| `canary` | Upstream canary string used for decryption |
| `split` | `test` |

## UI notes

- **Overview** — question count, topic count, questions-by-topic summary table.
- **Filters** — topic multiselect.
- **Sample inspector** — question markdown and highlighted reference answer.

## Cache

CSV cached at `data/cache/browsecomp/browse_comp_test_set.csv`. Truncated caches (fewer than 1,266 rows) are discarded and re-downloaded automatically — this can happen if the pytest fixture was written to the real cache path before tests isolated `cache_dir`.

## Links

- [OpenAI announcement](https://openai.com/index/browsecomp/)
- [Eval script](https://github.com/openai/simple-evals/blob/main/browsecomp_eval.py)
