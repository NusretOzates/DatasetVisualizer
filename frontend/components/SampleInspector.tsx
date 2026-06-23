"use client";

import { useEffect, useState, type FormEvent } from "react";
import type { DatasetMeta, SamplePayload } from "@/lib/types";
import { decodePrivateTests, fetchSample, findSample } from "@/lib/api";
import { renderSample } from "./viewers/registry";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Slider } from "@/components/ui/slider";
import { Skeleton } from "@/components/ui/skeleton";
import { AlertCircle, ChevronLeft, ChevronRight, Search } from "lucide-react";

type SampleInspectorProps = {
  datasetId: string;
  meta: DatasetMeta;
  params: Record<string, unknown>;
  filters: Record<string, unknown>;
};

export function SampleInspector({ datasetId, meta, params, filters }: SampleInspectorProps) {
  const [index, setIndex] = useState(0);
  const [payload, setPayload] = useState<SamplePayload | null>(null);
  const [privateTests, setPrivateTests] = useState<Record<string, unknown>[] | null>(null);
  const [privateTestsError, setPrivateTestsError] = useState<string | null>(null);
  const [privateTestsLoading, setPrivateTestsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lookupValue, setLookupValue] = useState("");
  const [lookupError, setLookupError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);
    setPrivateTestsError(null);
    setPrivateTests(null);
    setPrivateTestsLoading(Boolean(meta.supports_private_tests));
    fetchSample(datasetId, index, params, filters)
      .then(async (result) => {
        if (cancelled) return;
        setPayload(result);
        setIndex(result.index);
        const rawPrivateTests = result.row?.private_test_cases;
        if (
          meta.supports_private_tests &&
          rawPrivateTests &&
          String(rawPrivateTests).trim()
        ) {
          try {
            const decoded = await decodePrivateTests(String(rawPrivateTests));
            if (!cancelled) {
              setPrivateTests(decoded.cases);
              setPrivateTestsError(null);
            }
          } catch (decodeErr) {
            if (!cancelled) {
              setPrivateTests(null);
              setPrivateTestsError(
                decodeErr instanceof Error
                  ? decodeErr.message
                  : "Failed to decode private test cases",
              );
            }
          } finally {
            if (!cancelled) setPrivateTestsLoading(false);
          }
        } else if (!cancelled) {
          setPrivateTests(null);
          setPrivateTestsError(null);
          setPrivateTestsLoading(false);
        }
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
  }, [datasetId, index, params, filters, meta.supports_private_tests]);

  const total = payload?.total ?? 0;

  async function handleLookup(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const idValue = lookupValue.trim();
    if (!idValue) return;

    setLoading(true);
    setLookupError(null);
    setError(null);
    try {
      const result = await findSample(datasetId, idValue, params, filters);
      if (!result.row || result.index < 0) {
        setLookupError(`No sample found for ${meta.id_column} = ${idValue}`);
        return;
      }
      setPayload(result);
      setIndex(result.index);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to find sample");
    } finally {
      setLoading(false);
    }
  }

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
              disabled={index <= 0 || loading}
              onClick={() => setIndex(index - 1)}
            >
              <ChevronLeft className="size-4" />
              Previous
            </Button>
            <Button
              variant="outline"
              size="sm"
              disabled={!total || index >= total - 1 || loading}
              onClick={() => setIndex(index + 1)}
            >
              Next
              <ChevronRight className="size-4" />
            </Button>
            <span className="text-sm text-muted-foreground tabular-nums">
              Sample {total ? index + 1 : 0} of {total}
            </span>
          </div>

          <div className="space-y-2">
            <Label>Sample index</Label>
            <Slider
              value={[index]}
              min={0}
              max={Math.max(total - 1, 0)}
              step={1}
              disabled={!total || loading}
              onValueChange={(value) => setIndex(value[0] ?? 0)}
            />
          </div>

          <form onSubmit={handleLookup} className="grid gap-2 md:grid-cols-[1fr_auto]">
            <div className="space-y-2">
              <Label htmlFor="sample-id-lookup">Jump to {meta.id_column}</Label>
              <Input
                id="sample-id-lookup"
                value={lookupValue}
                onChange={(event) => setLookupValue(event.target.value)}
                placeholder={`Enter ${meta.id_column}`}
                disabled={loading}
              />
            </div>
            <Button type="submit" variant="secondary" className="self-end" disabled={loading}>
              <Search data-icon="inline-start" />
              Find sample
            </Button>
          </form>
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

      {lookupError ? (
        <Alert>
          <AlertCircle className="size-4" />
          <AlertTitle>Sample not found</AlertTitle>
          <AlertDescription>{lookupError}</AlertDescription>
        </Alert>
      ) : null}

      {loading && !payload ? <Skeleton className="h-64 w-full" /> : null}

      {payload ? (
        <Card>
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
