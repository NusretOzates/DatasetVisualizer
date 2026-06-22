"use client";

import { useEffect, useState } from "react";
import type { Catalog } from "@/lib/types";
import { fetchCatalog } from "@/lib/api";
import { DatasetExplorer } from "@/components/DatasetExplorer";
import { AppShell } from "@/components/Sidebar";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Skeleton } from "@/components/ui/skeleton";
import { AlertCircle } from "lucide-react";

type DatasetPageClientProps = {
  datasetId: string;
};

export function DatasetPageClient({ datasetId }: DatasetPageClientProps) {
  const [catalog, setCatalog] = useState<Catalog | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchCatalog()
      .then(setCatalog)
      .catch((err: Error) => setError(err.message));
  }, []);

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
