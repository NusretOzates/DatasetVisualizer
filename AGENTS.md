# AGENTS.md

## Cursor Cloud specific instructions

This is a Python 3.12 project managed with **uv**. The product is a single Streamlit
web app ("Dataset Visualizer") that loads Hugging Face benchmark datasets and renders
overview charts plus per-sample inspection. There is one service.

The update script runs `uv sync`, so dependencies are already installed at session start.
Standard commands are documented in `README.md` (Setup/Run/Development) and `docs/index.md`;
prefer those instead of duplicating them here.

Non-obvious notes:

- **`HF_TOKEN` is read from the environment, not just `.env`.** `src/dataset_visualizer/loaders/base.py`
  calls `load_dotenv()` with the default `override=False`, so an injected `HF_TOKEN`
  environment variable (e.g. a Cursor secret) takes precedence over the empty value in a
  copied `.env`. You do not need to paste the token into `.env` when it is already set as a secret.
  Some datasets (e.g. GPQA Diamond) are gated on Hugging Face and require a token with accepted terms.
- **Run the app headless** when starting it for testing so it does not block on the
  Streamlit email prompt: `uv run streamlit run src/dataset_visualizer/app.py --server.port 8501 --server.headless true`.
- **First dataset load downloads from Hugging Face** and can be slow; results are cached under
  `data/cache/<loader_key>/` (gitignored) and reused via `@st.cache_data`. For a fast smoke test,
  use the small `arxivmath_0526` dataset (40 rows) via the app or `uv run python scripts/inspect_dataset.py arxivmath_0526`.
- The inspect CLI prints Streamlit `No runtime found` / `missing ScriptRunContext` warnings
  because loaders are decorated with `@st.cache_data`; these are harmless outside the app.
