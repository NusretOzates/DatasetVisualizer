"use client";

import { useEffect, useState } from "react";
import type { Catalog } from "@/lib/types";
import { fetchCatalog } from "@/lib/api";

export function useCatalog() {
  const [catalog, setCatalog] = useState<Catalog | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    fetchCatalog()
      .then((result) => {
        if (!cancelled) setCatalog(result);
      })
      .catch((err: Error) => {
        if (!cancelled) setError(err.message);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  return { catalog, error };
}
