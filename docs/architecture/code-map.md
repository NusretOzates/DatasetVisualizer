# Code map

Use this map to locate the right files before searching the whole repository.

| Capability / Concern | Entry point | Key files | Tests |
|------------------------|------------------------------|-------------------------------|-----------------------------|
| Dataset catalog and metadata | `dataset_visualizer.api.service:get_catalog` | `config/datasets.yaml`, `src/dataset_visualizer/config.py`, `src/dataset_visualizer/api/service.py` | `tests/test_api_service.py`, `tests/test_home.py` |
| Dataset registration | `dataset_visualizer.api.dataset_registry:get_descriptor` | `src/dataset_visualizer/api/dataset_registry.py`, `config/datasets.yaml` | `tests/test_registry.py`, `tests/test_benchmark_registry.py` |
| Hugging Face benchmark loading | `dataset_visualizer.loaders.hf_benchmark:load_hf_benchmark_entry` | `src/dataset_visualizer/loaders/hf_benchmark.py`, `src/dataset_visualizer/loaders/benchmark_normalize.py` | `tests/test_loaders_hf_benchmark.py`, `tests/test_benchmark_normalize.py` |
| Overview payloads | `dataset_visualizer.api.service:get_overview` | `src/dataset_visualizer/api/overview.py`, `src/dataset_visualizer/api/generic_overview.py`, `src/dataset_visualizer/api/chart_data.py` | `tests/test_api_service.py`, `tests/test_generic_overview.py` |
| Filter options and filtering | `dataset_visualizer.api.service:get_filter_options` | `src/dataset_visualizer/api/filters.py`, `src/dataset_visualizer/api/dataset_registry.py` | `tests/test_filters.py`, `tests/test_api_service.py` |
| Sample lookup and inspection | `dataset_visualizer.api.service:get_sample` | `src/dataset_visualizer/api/service.py`, `frontend/components/SampleInspector.tsx`, `frontend/lib/api.ts` | `tests/test_api_service.py` |
| React overview charts | `frontend/components/OverviewTab.tsx:OverviewTab` | `frontend/components/ChartPanel.tsx`, `frontend/lib/types.ts` | Frontend type/lint checks |
| React sample viewers | `frontend/components/viewers/registry.tsx:renderSample` | `frontend/components/viewers/*Viewer.tsx`, `frontend/components/viewers/MarkdownMath.tsx` | Frontend type/lint checks |
| ARC-AGI grid visualization | `frontend/components/viewers/ArcGridViewer.tsx:ArcGridViewer` | `config/datasets.yaml`, `frontend/components/viewers/registry.tsx` | `tests/test_benchmark_registry.py`, frontend type/lint checks |
| Static frontend routes | `frontend/app/dataset/[id]/page.tsx:generateStaticParams` | `frontend/lib/api.ts`, `src/dataset_visualizer/server.py` | Frontend build |
