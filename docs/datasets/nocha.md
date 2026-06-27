# NoCha

**Source:** [marzenakrp/nocha](https://github.com/marzenakrp/nocha) on GitHub  
**Archetype:** Long-context QA (book-length claims)  
**Loader:** `dataset_visualizer.loaders.nocha` (`load_nocha`)

NoCha evaluates whether models can verify true/false claims about entire novels presented as context. The upstream project releases only a **sample subset** built from four classic books; the full copyrighted benchmark is evaluated privately by the authors.

## Normalized columns

| Column | Description |
|--------|-------------|
| `sample_id` | Stable id: `{book_title}::{pair_index}::{claim_type}` |
| `book_title` | Book slug (title + author) |
| `claim` | Claim text shown to the model |
| `claim_preview` | Truncated claim for overview tables |
| `claim_type` | `True` or `False` |
| `pair_index` | Shared id linking the true/false minimal pair |
| `paired_claim` | The other claim in the pair |
| `paired_claim_type` | `True` or `False` for the paired claim |
| `false_claim_explanation` | Annotator note on why the false claim is incorrect |
| `length` | Book length in tokens (`cl100k_base`) |
| `length_group` | Token bucket (`below 75k`, `127k_180k`, `above 180k`, …) |
| `genre` | `historical`, `contemporary`, or `speculative` |
| `publication_year` | Publication era (`classics` in the public sample) |
| `model_responses` | List of `{model, response, skipped}` from upstream JSON |

## Sample extras

| Key | Description |
|-----|-------------|
| `book_text_preview` | First 12k characters of the classic novel text |
| `book_char_count` | Full decoded book length |
| `book_text_omitted_chars` | Characters not sent in the API payload |

## UI notes

- **Overview** — claim count, pair count, books, length buckets, claims-by-book summary.
- **Filters** — book, claim type, genre, length bucket.
- **Sample inspector** — claim pair, false-claim explanation, scrollable book preview, published model responses.

## Cache

Downloaded GitHub archive lives under `data/cache/nocha/`.

## Links

- [NoCha paper](https://arxiv.org/abs/2406.16264)
- [Leaderboard](https://novelchallenge.github.io/index.html)
