"use client";

import { useEffect, useRef, useState } from "react";
import type { Catalog, DatasetMeta, FilterOptions, OverviewPayload } from "@/lib/types";
import { fetchDatasetMeta, fetchFilterOptions, fetchOverview } from "@/lib/api";
import { AppShell } from "@/components/Sidebar";
import { OverviewTab } from "@/components/OverviewTab";
import { SampleInspector } from "@/components/SampleInspector";
import { ControlPanel, FilterPanel } from "@/components/FilterPanel";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { AlertCircle } from "lucide-react";

type DatasetExplorerProps = {
  catalog: Catalog;
  datasetId: string;
};

function defaultControlValues(meta: DatasetMeta): Record<string, unknown> {
  const values: Record<string, unknown> = {};
  for (const control of meta.controls) {
    values[control.name] = control.default;
  }
  return values;
}

function defaultFilterValues(meta: DatasetMeta): Record<string, unknown> {
  const values: Record<string, unknown> = {};
  for (const filter of meta.filters) {
    if (filter.type === "radio") {
      values[filter.name] = filter.default ?? "All";
    }
    if (filter.type === "text") {
      values[filter.name] = "";
    }
  }
  return values;
}

function mergeFilterDefaults(
  meta: DatasetMeta,
  options: FilterOptions,
  base: Record<string, unknown>,
): Record<string, unknown> {
  const next = { ...base };
  for (const filter of meta.filters) {
    if (filter.type === "multiselect" && Array.isArray(options[filter.name])) {
      if (!Array.isArray(next[filter.name])) {
        next[filter.name] = options[filter.name];
      }
    }
    if (filter.type === "date_range" && options[filter.name]) {
      const range = options[filter.name];
      if (range && typeof range === "object" && "min" in range && !next[filter.name]) {
        next[filter.name] = { start: range.min, end: range.max };
      }
    }
  }
  return next;
}

function buildInitialFilters(meta: DatasetMeta, options: FilterOptions): Record<string, unknown> {
  return mergeFilterDefaults(meta, options, defaultFilterValues(meta));
}

export function DatasetExplorer({ catalog, datasetId }: DatasetExplorerProps) {
  const [meta, setMeta] = useState<DatasetMeta | null>(null);
  const [params, setParams] = useState<Record<string, unknown>>({});
  const [filters, setFilters] = useState<Record<string, unknown>>({});
  const [filterOptions, setFilterOptions] = useState<FilterOptions>({});
  const [overview, setOverview] = useState<OverviewPayload | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const initializedRef = useRef(false);
  const prevParamsRef = useRef<string | null>(null);
  const prevQueryRef = useRef<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    initializedRef.current = false;
    prevParamsRef.current = null;
    prevQueryRef.current = null;

    async function initialize() {
      setLoading(true);
      setError(null);
      setOverview(null);
      try {
        const datasetMeta = await fetchDatasetMeta(datasetId);
        const initialParams = defaultControlValues(datasetMeta);
        const options = await fetchFilterOptions(datasetId, initialParams);
        if (cancelled) return;

        const initialFilters = buildInitialFilters(datasetMeta, options);
        setMeta(datasetMeta);
        setParams(initialParams);
        setFilters(initialFilters);
        setFilterOptions(options);

        const overviewResult = await fetchOverview(datasetId, initialParams, initialFilters);
        if (cancelled) return;
        setOverview(overviewResult);
        initializedRef.current = true;
        prevParamsRef.current = JSON.stringify(initialParams);
        prevQueryRef.current = JSON.stringify({ params: initialParams, filters: initialFilters });
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "Failed to load dataset");
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    void initialize();
    return () => {
      cancelled = true;
    };
  }, [datasetId]);

  useEffect(() => {
    if (!meta || !initializedRef.current) return;
    const paramsKey = JSON.stringify(params);
    if (prevParamsRef.current === paramsKey) return;
    prevParamsRef.current = paramsKey;

    let cancelled = false;
    setLoading(true);
    fetchFilterOptions(datasetId, params)
      .then((options) => {
        if (cancelled) return;
        setFilterOptions(options);
        setFilters(buildInitialFilters(meta, options));
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
  }, [datasetId, meta, params]);

  useEffect(() => {
    if (!meta || !initializedRef.current) return;
    const queryKey = JSON.stringify({ params, filters });
    if (prevQueryRef.current === queryKey) return;
    prevQueryRef.current = queryKey;

    let cancelled = false;
    setLoading(true);
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
  }, [datasetId, meta, params, filters]);

  const title = meta?.label ?? datasetId;

  return (
    <AppShell catalog={catalog}>
      <div className="space-y-6">
        <div className="space-y-3">
          <div className="flex flex-wrap items-center gap-2">
            <h2 className="text-3xl font-semibold tracking-tight">{title}</h2>
            {meta?.archetype ? <Badge variant="secondary">{meta.archetype}</Badge> : null}
          </div>
          {meta ? <p className="max-w-4xl text-muted-foreground">{meta.description}</p> : null}
        </div>

        {error ? (
          <Alert variant="destructive">
            <AlertCircle className="size-4" />
            <AlertTitle>Something went wrong</AlertTitle>
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        ) : null}

        {!meta && loading ? (
          <div className="space-y-4">
            <Skeleton className="h-28 w-full" />
            <Skeleton className="h-28 w-full" />
            <Skeleton className="h-64 w-full" />
          </div>
        ) : null}

        {meta ? (
          <div className="space-y-4">
            <ControlPanel
              controls={meta.controls}
              values={params}
              onChange={(name, value) => setParams((current) => ({ ...current, [name]: value }))}
            />
            <FilterPanel
              filters={meta.filters}
              options={filterOptions}
              values={filters}
              onChange={(name, value) => setFilters((current) => ({ ...current, [name]: value }))}
            />

            <Tabs defaultValue="overview" className="space-y-4">
              <TabsList>
                <TabsTrigger value="overview">Overview</TabsTrigger>
                <TabsTrigger value="sample">Sample Inspector</TabsTrigger>
              </TabsList>

              <TabsContent value="overview" className="space-y-4">
                {loading && !overview ? (
                  <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
                    {Array.from({ length: 4 }).map((_, index) => (
                      <Skeleton key={index} className="h-24 w-full" />
                    ))}
                  </div>
                ) : null}
                {overview ? <OverviewTab overview={overview} /> : null}
              </TabsContent>

              <TabsContent value="sample">
                <SampleInspector
                  datasetId={datasetId}
                  meta={meta}
                  params={params}
                  filters={filters}
                />
              </TabsContent>
            </Tabs>
          </div>
        ) : null}
      </div>
    </AppShell>
  );
}
