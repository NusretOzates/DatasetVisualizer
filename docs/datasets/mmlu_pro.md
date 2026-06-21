# MMLU-Pro

**Source:** [`TIGER-Lab/MMLU-Pro`](https://huggingface.co/datasets/TIGER-Lab/MMLU-Pro)  
**Archetype:** MCQ with chain-of-thought  
**Status:** Stub (Wave 2)

## Planned schema

| Column | Notes |
|--------|-------|
| `question_id` | Unique identifier |
| `question` | Question text |
| `options` | Variable-length options (filter `"N/A"`) |
| `answer` | Correct letter |
| `answer_index` | Numeric index |
| `category` | Discipline |
| `src` | Provenance |
| `cot_content` | Chain-of-thought (long) |

## Planned visualization

- Category bar chart, option-count histogram, src provenance table
- Dynamic MCQ grid with CoT expander
