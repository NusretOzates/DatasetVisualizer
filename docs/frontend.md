# Frontend (Next.js)

The Dataset Visualizer UI is a **Next.js 15** React app in [`frontend/`](../frontend/). It talks to the Gradio Server backend via [`@gradio/client`](https://www.npmjs.com/package/@gradio/client).

## Stack

| Piece | Location | Role |
|-------|----------|------|
| App shell | `app/layout.tsx`, `app/globals.css` | Root layout and styles |
| Home page | `app/page.tsx` → `components/HomePage.tsx` | Dataset catalog table |
| Dataset routes | `app/dataset/[id]/page.tsx` | Static export; lists all dataset ids |
| API client | `lib/api.ts` | `@gradio/client` wrappers |
| Types | `lib/types.ts` | Catalog, overview, chart, and control types |
| Explorer | `components/DatasetExplorer.tsx` | Controls, filters, tabs |
| Overview | `components/OverviewTab.tsx`, `ChartPanel.tsx` | Metrics + Plotly charts |
| Samples | `components/SampleInspector.tsx` | Index slider, ID search, viewers |

## Development

Terminal 1 — backend:

```bash
uv run dataset-viz
```

Terminal 2 — frontend with hot reload:

```bash
cd frontend
npm install
NEXT_PUBLIC_API_URL=http://localhost:7860 npm run dev
```

Open http://localhost:3000. The API client uses `NEXT_PUBLIC_API_URL` when set; otherwise it falls back to `window.location.origin` (same-origin production mode).

## Production build

```bash
cd frontend
npm run build   # writes static export to frontend/out/
cd ..
uv run dataset-viz
```

`server.py` serves `frontend/out/` at `/` when the build exists. Rebuild the frontend after UI changes.

## Adding a dataset to the frontend

1. Add the config `id` to `DATASET_IDS` in `app/dataset/[id]/page.tsx` (required for `output: "export"`).
2. Ensure `api/service.py` returns correct `archetype`, controls, filters, and overview payloads.
3. If the archetype is already handled in `SampleInspector.tsx`, no new viewer is needed.

### Archetype → viewer mapping

Defined in `components/SampleInspector.tsx`:

- `mcq`, `mcq_multilingual` → `McqViewer`
- `mcq_cot` → `McqViewer` + chain-of-thought expander
- `code_problem` → `CodeProblemViewer` (+ private tests via `decode_private_tests` API)
- `issue_resolution` → `IssueViewer`
- `academic_qa` → `HleViewer`
- `math_competition` → `MathViewer` (or `ArxivMathViewer` for `arxivmath_0526`)

Custom viewers live in `components/viewers/`.

## Chart payloads

Overview charts are built server-side in `api/chart_data.py` and rendered client-side with `react-plotly.js`. Supported `type` values:

- `bar`, `pie`, `histogram`, `stacked_bar`, `timeline`, `scatter`

See `lib/types.ts` for the full TypeScript shapes.
