import { useCallback, useEffect, useRef, useState } from "react";
import type { DatasetMeta, FilterOptions, OverviewPayload } from "@/lib/types";
import { fetchDatasetMeta, fetchFilterOptions, fetchOverview } from "@/lib/api";
import {
  buildInitialFilters,
  defaultControlValues,
  reconcileFilters,
  type FilterValues,
} from "@/lib/filterState";

type DatasetQueryState = {
  meta: DatasetMeta | null;
  params: FilterValues;
  filters: FilterValues;
  filterOptions: FilterOptions;
  overview: OverviewPayload | null;
  loading: boolean;
  error: string | null;
  setParam: (name: string, value: unknown) => void;
  setFilter: (name: string, value: unknown) => void;
};

export function useDatasetQuery(datasetId: string): DatasetQueryState {
  const [meta, setMeta] = useState<DatasetMeta | null>(null);
  const [params, setParams] = useState<FilterValues>({});
  const [filters, setFilters] = useState<FilterValues>({});
  const [filterOptions, setFilterOptions] = useState<FilterOptions>({});
  const [overview, setOverview] = useState<OverviewPayload | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [initialized, setInitialized] = useState(false);
  const paramsKeyRef = useRef<string | null>(null);
  const queryKeyRef = useRef<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setInitialized(false);
    setLoading(true);
    setError(null);
    setOverview(null);
    setMeta(null);
    paramsKeyRef.current = null;
    queryKeyRef.current = null;

    async function initialize() {
      try {
        const datasetMeta = await fetchDatasetMeta(datasetId);
        const initialParams = defaultControlValues(datasetMeta);
        const options = await fetchFilterOptions(datasetId, initialParams);
        if (cancelled) return;

        const initialFilters = buildInitialFilters(datasetMeta, options);
        const initialParamsKey = JSON.stringify(initialParams);

        setMeta(datasetMeta);
        setParams(initialParams);
        setFilterOptions(options);
        setFilters(initialFilters);
        paramsKeyRef.current = initialParamsKey;
        queryKeyRef.current = null;
        setInitialized(true);
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "Failed to load dataset");
          setLoading(false);
        }
      }
    }

    void initialize();
    return () => {
      cancelled = true;
    };
  }, [datasetId]);

  useEffect(() => {
    if (!initialized || !meta) return;

    const paramsKey = JSON.stringify(params);
    if (paramsKeyRef.current === paramsKey) return;
    paramsKeyRef.current = paramsKey;

    let cancelled = false;
    setLoading(true);
    setError(null);

    fetchFilterOptions(datasetId, params)
      .then((options) => {
        if (cancelled) return;
        setFilterOptions(options);
        setFilters((current) => reconcileFilters(meta, options, current));
      })
      .catch((err: Error) => {
        if (!cancelled) setError(err.message);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [datasetId, initialized, meta, params]);

  useEffect(() => {
    if (!initialized || !meta) return;

    const queryKey = JSON.stringify({ params, filters });
    if (queryKeyRef.current === queryKey) return;
    queryKeyRef.current = queryKey;

    let cancelled = false;
    setLoading(true);
    setError(null);

    fetchOverview(datasetId, params, filters)
      .then((result) => {
        if (!cancelled) setOverview(result);
      })
      .catch((err: Error) => {
        if (!cancelled) setError(err.message);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [datasetId, initialized, meta, params, filters]);

  const setParam = useCallback((name: string, value: unknown) => {
    setParams((current) => ({ ...current, [name]: value }));
  }, []);

  const setFilter = useCallback((name: string, value: unknown) => {
    setFilters((current) => ({ ...current, [name]: value }));
  }, []);

  return {
    meta,
    params,
    filters,
    filterOptions,
    overview,
    loading,
    error,
    setParam,
    setFilter,
  };
}
