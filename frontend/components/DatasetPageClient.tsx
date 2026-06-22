"use client";

import { useEffect, useState } from "react";
import type { Catalog } from "@/lib/types";
import { fetchCatalog } from "@/lib/api";
import { DatasetExplorer } from "@/components/DatasetExplorer";

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
      <main className="main">
        {error ? <div className="error">{error}</div> : <p className="muted">Loading…</p>}
      </main>
    );
  }

  return <DatasetExplorer catalog={catalog} datasetId={datasetId} />;
}
