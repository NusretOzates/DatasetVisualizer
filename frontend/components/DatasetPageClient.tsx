"use client";

import { DatasetExplorer } from "@/components/DatasetExplorer";
import { AppShell } from "@/components/Sidebar";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Skeleton } from "@/components/ui/skeleton";
import { useCatalog } from "@/lib/useCatalog";
import { AlertCircle } from "lucide-react";

type DatasetPageClientProps = {
  datasetId: string;
};

export function DatasetPageClient({ datasetId }: DatasetPageClientProps) {
  const { catalog, error } = useCatalog();

  if (!catalog) {
    return (
      <AppShell>
        {error ? (
          <Alert variant="destructive">
            <AlertCircle className="size-4" />
            <AlertTitle>Failed to load catalog</AlertTitle>
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        ) : (
          <div className="space-y-4">
            <Skeleton className="h-10 w-64" />
            <Skeleton className="h-64 w-full" />
          </div>
        )}
      </AppShell>
    );
  }

  return <DatasetExplorer catalog={catalog} datasetId={datasetId} />;
}
