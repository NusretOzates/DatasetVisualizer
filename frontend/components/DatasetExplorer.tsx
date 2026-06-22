"use client";

import { useEffect, useMemo, useState } from "react";
import type { Catalog, DatasetMeta, OverviewPayload } from "@/lib/types";
import {
  fetchDatasetMeta,
  fetchFilterOptions,
  fetchOverview,
} from "@/lib/api";
import { Sidebar } from "@/components/Sidebar";
import { OverviewTab } from "@/components/OverviewTab";
import { SampleInspector } from "@/components/SampleInspector";
import { ControlPanel, FilterPanel } from "@/components/FilterPanel";

type DatasetExplorerProps = {
  catalog: Catalog;
  datasetId: string;
};

function defaultControlValues(meta: DatasetMeta): Record<string, unknown> {
  const values: Record<string, unknown> = {};
  for (const control of meta.controls) {
    if (control.type === "select") {
      values[control.name] = control.default;
    }
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

export function DatasetExplorer({ catalog, datasetId }: DatasetExplorerProps) {
  const [meta, setMeta] = useState<DatasetMeta | null>(null);
  const [params, setParams] = useState<Record<string, unknown>>({});
  const [filters, setFilters] = useState<Record<string, unknown>>({});
  const [filterOptions, setFilterOptions] = useState<Record<string, unknown>>({});
  const [overview, setOverview] = useState<OverviewPayload | null>(null);
  const [activeTab, setActiveTab] = useState<"overview" | "sample">("overview");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);
    fetchDatasetMeta(datasetId)
      .then((datasetMeta) => {
        if (cancelled) return;
        setMeta(datasetMeta);
        setParams(defaultControlValues(datasetMeta));
        setFilters(defaultFilterValues(datasetMeta));
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
  }, [datasetId]);

  useEffect(() => {
    if (!meta) return;
    let cancelled = false;
    fetchFilterOptions(datasetId, params)
      .then((options) => {
        if (cancelled) return;
        setFilterOptions(options);
        setFilters((current) => {
          const next = { ...current };
          for (const filter of meta.filters) {
            if (filter.type === "multiselect" && Array.isArray(options[filter.name])) {
              if (!Array.isArray(next[filter.name])) {
                next[filter.name] = options[filter.name];
              }
            }
            if (filter.type === "date_range" && options[filter.name]) {
              const range = options[filter.name] as { min?: string; max?: string };
              if (!next[filter.name]) {
                next[filter.name] = { start: range.min, end: range.max };
              }
            }
          }
          return next;
        });
      })
      .catch((err: Error) => {
        if (!cancelled) setError(err.message);
      });
    return () => {
      cancelled = true;
    };
  }, [datasetId, meta, params]);

  useEffect(() => {
    if (!meta) return;
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

  const title = useMemo(() => meta?.label ?? datasetId, [meta, datasetId]);

  return (
    <div className="app-shell">
      <Sidebar catalog={catalog} />
      <main className="main">
        <h2>{title}</h2>
        {meta ? <p className="muted">{meta.description}</p> : null}
        {error ? <div className="error">{error}</div> : null}
        {meta ? (
          <>
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
            <div className="tabs">
              <button
                type="button"
                className={`tab${activeTab === "overview" ? " active" : ""}`}
                onClick={() => setActiveTab("overview")}
              >
                Overview
              </button>
              <button
                type="button"
                className={`tab${activeTab === "sample" ? " active" : ""}`}
                onClick={() => setActiveTab("sample")}
              >
                Sample Inspector
              </button>
            </div>
            {loading && !overview ? <p className="muted">Loading dataset…</p> : null}
            {activeTab === "overview" && overview ? <OverviewTab overview={overview} /> : null}
            {activeTab === "sample" && meta ? (
              <SampleInspector
                datasetId={datasetId}
                meta={meta}
                params={params}
                filters={filters}
              />
            ) : null}
          </>
        ) : null}
      </main>
    </div>
  );
}
