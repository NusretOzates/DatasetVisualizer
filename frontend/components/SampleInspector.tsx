"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import type { DatasetMeta, SamplePayload } from "@/lib/types";
import { decodePrivateTests, fetchSample } from "@/lib/api";
import { renderSample } from "./viewers/registry";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";
import { Label } from "@/components/ui/label";
import { Slider } from "@/components/ui/slider";
import { Skeleton } from "@/components/ui/skeleton";
import { AlertCircle, ChevronLeft, ChevronRight } from "lucide-react";

type SampleInspectorProps = {
  datasetId: string;
  meta: DatasetMeta;
  params: Record<string, unknown>;
  filters: Record<string, unknown>;
};

type SampleCache = {
  key: string;
  samples: Map<number, SamplePayload>;
};

function sampleQueryKey(
  datasetId: string,
  params: Record<string, unknown>,
  filters: Record<string, unknown>,
): string {
  return `${datasetId}:${JSON.stringify(params)}:${JSON.stringify(filters)}`;
}

export function SampleInspector({ datasetId, meta, params, filters }: SampleInspectorProps) {
  const [index, setIndex] = useState(0);
  const [payload, setPayload] = useState<SamplePayload | null>(null);
  const [privateTests, setPrivateTests] = useState<Record<string, unknown>[] | null>(null);
  const [privateTestsError, setPrivateTestsError] = useState<string | null>(null);
  const [privateTestsLoading, setPrivateTestsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [loadToken, setLoadToken] = useState(0);

  const queryKey = useMemo(
    () => sampleQueryKey(datasetId, params, filters),
    [datasetId, params, filters],
  );
  const cacheRef = useRef<SampleCache>({ key: "", samples: new Map() });
  const inflightRef = useRef<Map<number, Promise<SamplePayload>>>(new Map());
  const indexRef = useRef(index);
  indexRef.current = index;

  useEffect(() => {
    cacheRef.current = { key: queryKey, samples: new Map() };
    inflightRef.current.clear();
    setIndex(0);
    setPayload(null);
    setError(null);
    setPrivateTests(null);
    setPrivateTestsError(null);
    setPrivateTestsLoading(false);
    setLoadToken((token) => token + 1);
  }, [queryKey]);

  const loadPrivateTests = useCallback(
    async (row: Record<string, unknown> | null | undefined, cancelled: () => boolean) => {
      const rawPrivateTests = row?.private_test_cases;
      if (meta.supports_private_tests && rawPrivateTests && String(rawPrivateTests).trim()) {
        setPrivateTestsLoading(true);
        try {
          const decoded = await decodePrivateTests(String(rawPrivateTests));
          if (!cancelled()) {
            setPrivateTests(decoded.cases);
            setPrivateTestsError(null);
          }
        } catch (decodeErr) {
          if (!cancelled()) {
            setPrivateTests(null);
            setPrivateTestsError(
              decodeErr instanceof Error
                ? decodeErr.message
                : "Failed to decode private test cases",
            );
          }
        } finally {
          if (!cancelled()) setPrivateTestsLoading(false);
        }
        return;
      }
      if (!cancelled()) {
        setPrivateTests(null);
        setPrivateTestsError(null);
        setPrivateTestsLoading(false);
      }
    },
    [meta.supports_private_tests],
  );

  const requestSample = useCallback(
    (targetIndex: number) => {
      let promise = inflightRef.current.get(targetIndex);
      if (!promise) {
        promise = fetchSample(datasetId, targetIndex, params, filters);
        inflightRef.current.set(targetIndex, promise);
        void promise.finally(() => {
          inflightRef.current.delete(targetIndex);
        });
      }
      return promise;
    },
    [datasetId, params, filters],
  );

  const prefetchNeighbors = useCallback(
    (centerIndex: number, total: number) => {
      for (const neighbor of [centerIndex - 1, centerIndex + 1]) {
        if (neighbor < 0 || neighbor >= total) continue;
        if (cacheRef.current.samples.has(neighbor)) continue;
        if (inflightRef.current.has(neighbor)) continue;
        void requestSample(neighbor).then((result) => {
          cacheRef.current.samples.set(result.index, result);
        });
      }
    },
    [requestSample],
  );

  useEffect(() => {
    let cancelled = false;
    const isCancelled = () => cancelled;

    const cached = cacheRef.current.samples.get(index);
    if (cached) {
      setPayload(cached);
      setIndex(cached.index);
      setLoading(false);
      setError(null);
      void loadPrivateTests(cached.row, isCancelled);
      prefetchNeighbors(cached.index, cached.total);
      return () => {
        cancelled = true;
      };
    }

    setLoading(true);
    setError(null);

    void requestSample(index)
      .then(async (result) => {
        if (cancelled) return;
        cacheRef.current.samples.set(result.index, result);
        if (indexRef.current !== index) return;
        setPayload(result);
        setIndex(result.index);
        await loadPrivateTests(result.row, isCancelled);
        if (!cancelled) prefetchNeighbors(result.index, result.total);
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
  }, [index, loadToken, requestSample, loadPrivateTests, prefetchNeighbors]);

  const total = payload?.total ?? 0;
  const navigating = loading && payload !== null;

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base">Navigate samples</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex flex-wrap items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              disabled={index <= 0 || (loading && !payload)}
              onClick={() => setIndex(index - 1)}
            >
              <ChevronLeft className="size-4" />
              Previous
            </Button>
            <Button
              variant="outline"
              size="sm"
              disabled={!total || index >= total - 1 || (loading && !payload)}
              onClick={() => setIndex(index + 1)}
            >
              Next
              <ChevronRight className="size-4" />
            </Button>
            <span className="text-sm text-muted-foreground tabular-nums">
              Sample {total ? index + 1 : 0} of {total}
              {navigating ? " · loading…" : ""}
            </span>
          </div>

          <div className="space-y-2">
            <Label>Sample index</Label>
            <Slider
              value={[index]}
              min={0}
              max={Math.max(total - 1, 0)}
              step={1}
              disabled={!total || (loading && !payload)}
              onValueChange={(value) => setIndex(value[0] ?? 0)}
            />
          </div>
        </CardContent>
      </Card>

      {error ? (
        <Alert variant="destructive">
          <AlertCircle className="size-4" />
          <AlertTitle>Failed to load sample</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      ) : null}

      {privateTestsError ? (
        <Alert variant="destructive">
          <AlertCircle className="size-4" />
          <AlertTitle>Private test cases unavailable</AlertTitle>
          <AlertDescription>{privateTestsError}</AlertDescription>
        </Alert>
      ) : null}

      {loading && !payload ? <Skeleton className="h-64 w-full" /> : null}

      {payload ? (
        <Card className={navigating ? "opacity-70 transition-opacity" : undefined}>
          <CardContent className="pt-6">
            {renderSample(meta, payload, privateTests, privateTestsLoading)}
          </CardContent>
        </Card>
      ) : null}

      {payload?.row ? (
        <Collapsible>
          <CollapsibleTrigger>Raw JSON</CollapsibleTrigger>
          <CollapsibleContent className="pt-3">
            <pre className="code-block">{JSON.stringify(payload.row, null, 2)}</pre>
          </CollapsibleContent>
        </Collapsible>
      ) : null}
    </div>
  );
}
