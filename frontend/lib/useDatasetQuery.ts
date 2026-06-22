import { useCallback, useEffect, useRef, useState } from "react";
import type { DatasetMeta, FilterOptions, OverviewPayload } from "@/lib/types";
import { fetchDatasetMeta, fetchFilterOptions, fetchOverview } from "@/lib/api";
import {
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
  const requestIdRef = useRef(0);

  useEffect(() => {
    let cancelled = false;
    setInitialized(false);
    setLoading(true);
    setError(null);
    setOverview(null);
    setMeta(null);
    paramsKeyRef.current = null;

    async function initialize() {
      try {
        const datasetMeta = await fetchDatasetMeta(datasetId);
        if (cancelled) return;
        setMeta(datasetMeta);
        setParams(defaultControlValues(datasetMeta));
        setFilters({});
        setFilterOptions({});
        paramsKeyRef.current = null;
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

    const datasetMeta = meta;
    const requestId = ++requestIdRef.current;
    let cancelled = false;

    async function refresh() {
      setLoading(true);
      setError(null);
      setOverview(null);

      try {
        const paramsKey = JSON.stringify(params);
        let activeFilters = filters;

        if (paramsKeyRef.current !== paramsKey) {
          paramsKeyRef.current = paramsKey;
          const options = await fetchFilterOptions(datasetId, params);
          if (cancelled || requestId !== requestIdRef.current) return;
          activeFilters = reconcileFilters(datasetMeta, options, filters);
          setFilterOptions(options);
          setFilters(activeFilters);
        }

        const result = await fetchOverview(datasetId, params, activeFilters);
        if (cancelled || requestId !== requestIdRef.current) return;
        setOverview(result);
      } catch (err) {
        if (!cancelled && requestId === requestIdRef.current) {
          setError(err instanceof Error ? err.message : "Failed to load dataset");
        }
      } finally {
        if (!cancelled && requestId === requestIdRef.current) {
          setLoading(false);
        }
      }
    }

    void refresh();
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
