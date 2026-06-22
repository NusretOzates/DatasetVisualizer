"use client";

import type { Catalog } from "@/lib/types";
import { useDatasetQuery } from "@/lib/useDatasetQuery";
import { AppShell } from "@/components/Sidebar";
import { OverviewTab } from "@/components/OverviewTab";
import { SampleInspector } from "@/components/SampleInspector";
import { ControlPanel, FilterPanel } from "@/components/FilterPanel";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";
import { AlertCircle } from "lucide-react";

type DatasetExplorerProps = {
  catalog: Catalog;
  datasetId: string;
};

export function DatasetExplorer({ catalog, datasetId }: DatasetExplorerProps) {
  const {
    meta,
    params,
    filters,
    filterOptions,
    overview,
    loading,
    error,
    setParam,
    setFilter,
  } = useDatasetQuery(datasetId);

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
            <Skeleton className="h-64 w-full" />
          </div>
        ) : null}

        {meta ? (
          <div className="space-y-4">
            <ControlPanel
              controls={meta.controls}
              values={params}
              onChange={setParam}
            />

            <Tabs defaultValue="overview" className="space-y-4">
              <TabsList>
                <TabsTrigger value="overview">Overview</TabsTrigger>
                <TabsTrigger value="sample">Sample Inspector</TabsTrigger>
              </TabsList>

              <TabsContent value="overview" className="space-y-4">
                {loading ? (
                  <div className="space-y-4">
                    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
                      {Array.from({ length: 4 }).map((_, index) => (
                        <Skeleton key={index} className="h-24 w-full" />
                      ))}
                    </div>
                    <Skeleton className="h-80 w-full" />
                  </div>
                ) : null}
                {!loading && overview ? <OverviewTab overview={overview} /> : null}

                {meta.filters.length > 0 ? (
                  <Collapsible>
                    <CollapsibleTrigger>Filter dataset</CollapsibleTrigger>
                    <CollapsibleContent className="pt-3">
                      <FilterPanel
                        filters={meta.filters}
                        options={filterOptions}
                        values={filters}
                        onChange={setFilter}
                      />
                    </CollapsibleContent>
                  </Collapsible>
                ) : null}
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
