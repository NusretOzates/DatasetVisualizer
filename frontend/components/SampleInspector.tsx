"use client";

import { useEffect, useState } from "react";
import type { DatasetMeta, SamplePayload } from "@/lib/types";
import { decodePrivateTests, fetchSample, findSample } from "@/lib/api";
import { McqViewer } from "./viewers/McqViewer";
import { CodeProblemViewer } from "./viewers/CodeProblemViewer";
import { IssueViewer } from "./viewers/IssueViewer";
import { ArxivMathViewer, HleViewer, MathViewer } from "./viewers/SpecialViewers";
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
import { AlertCircle, ChevronDown, ChevronLeft, ChevronRight, Search } from "lucide-react";

type SampleInspectorProps = {
  datasetId: string;
  meta: DatasetMeta;
  params: Record<string, unknown>;
  filters: Record<string, unknown>;
};

function renderSample(
  datasetId: string,
  meta: DatasetMeta,
  payload: SamplePayload,
  privateTests: Record<string, unknown>[] | null,
) {
  if (!payload.row) {
    return <p className="text-sm text-muted-foreground">No sample available.</p>;
  }

  const row = payload.row;
  const archetype = meta.archetype ?? "";

  if (datasetId === "arxivmath_0526") {
    return <ArxivMathViewer row={row} extras={payload.extras} />;
  }
  if (datasetId === "aime_2026") {
    return <MathViewer row={row} solution={String(payload.extras.solution ?? "")} />;
  }
  if (datasetId === "hle") {
    return <HleViewer row={row} />;
  }
  if (archetype === "code_problem") {
    return (
      <div className="space-y-4">
        <CodeProblemViewer row={row} />
        {privateTests ? (
          <Collapsible>
            <CollapsibleTrigger>
              <ChevronDown className="size-4" />
              Private test cases
            </CollapsibleTrigger>
            <CollapsibleContent className="pt-3">
              <CodeProblemViewer row={{ public_test_cases: privateTests }} />
            </CollapsibleContent>
          </Collapsible>
        ) : null}
      </div>
    );
  }
  if (archetype === "issue_resolution") {
    return <IssueViewer row={row} />;
  }
  if (archetype === "mcq_cot") {
    return (
      <div className="space-y-4">
        <McqViewer row={row} choicesCol="options" answerCol="answer" />
        {row.cot_content ? (
          <Collapsible>
            <CollapsibleTrigger>
              <ChevronDown className="size-4" />
              Chain-of-thought
            </CollapsibleTrigger>
            <CollapsibleContent className="pt-3">
              <pre className="code-block">{String(row.cot_content)}</pre>
            </CollapsibleContent>
          </Collapsible>
        ) : null}
      </div>
    );
  }
  if (archetype?.startsWith("mcq")) {
    return <McqViewer row={row} />;
  }
  if (archetype === "math_competition") {
    return <MathViewer row={row} />;
  }

  return <pre className="code-block">{JSON.stringify(row, null, 2)}</pre>;
}

export function SampleInspector({ datasetId, meta, params, filters }: SampleInspectorProps) {
  const [index, setIndex] = useState(0);
  const [idSearch, setIdSearch] = useState("");
  const [payload, setPayload] = useState<SamplePayload | null>(null);
  const [privateTests, setPrivateTests] = useState<Record<string, unknown>[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);
    fetchSample(datasetId, index, params, filters)
      .then(async (result) => {
        if (cancelled) return;
        setPayload(result);
        if (
          datasetId === "livecodebench_v6" &&
          result.row?.private_test_cases &&
          String(result.row.private_test_cases).trim()
        ) {
          const decoded = await decodePrivateTests(String(result.row.private_test_cases));
          if (!cancelled) setPrivateTests(decoded.cases);
        } else if (!cancelled) {
          setPrivateTests(null);
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
  }, [datasetId, index, params, filters]);

  const total = payload?.total ?? 0;

  async function handleSearch() {
    if (!idSearch.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const result = await findSample(datasetId, idSearch.trim(), params, filters);
      setPayload(result);
      if (result.index >= 0) setIndex(result.index);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Search failed");
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

          <div className="flex flex-col gap-2 sm:flex-row sm:items-end">
            <div className="flex-1 space-y-2">
              <Label htmlFor="id-search">Find by {meta.id_column}</Label>
              <Input
                id="id-search"
                value={idSearch}
                placeholder={`Search ${meta.id_column}`}
                onChange={(event) => setIdSearch(event.target.value)}
                onKeyDown={(event) => {
                  if (event.key === "Enter") void handleSearch();
                }}
              />
            </div>
            <Button onClick={() => void handleSearch()} disabled={loading}>
              <Search className="size-4" />
              Search
            </Button>
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

      {loading && !payload ? <Skeleton className="h-64 w-full" /> : null}

      {payload ? (
        <Card>
          <CardContent className="pt-6">
            {renderSample(datasetId, meta, payload, privateTests)}
          </CardContent>
        </Card>
      ) : null}

      {payload?.row ? (
        <Collapsible>
          <CollapsibleTrigger>
            <ChevronDown className="size-4" />
            Raw JSON
          </CollapsibleTrigger>
          <CollapsibleContent className="pt-3">
            <pre className="code-block">{JSON.stringify(payload.row, null, 2)}</pre>
          </CollapsibleContent>
        </Collapsible>
      ) : null}
    </div>
  );
}
