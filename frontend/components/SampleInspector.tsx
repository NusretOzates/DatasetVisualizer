"use client";

import { useEffect, useState } from "react";
import type { ControlSpec, DatasetMeta, SamplePayload } from "@/lib/types";
import { decodePrivateTests, fetchSample, findSample } from "@/lib/api";
import { McqViewer } from "./viewers/McqViewer";
import { CodeProblemViewer } from "./viewers/CodeProblemViewer";
import { IssueViewer } from "./viewers/IssueViewer";
import { ArxivMathViewer, HleViewer, MathViewer } from "./viewers/SpecialViewers";

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
    return <p className="muted">No sample available.</p>;
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
      <div>
        <CodeProblemViewer row={row} />
        {privateTests ? (
          <details>
            <summary>Private test cases</summary>
            <CodeProblemViewer row={{ public_test_cases: privateTests }} />
          </details>
        ) : null}
      </div>
    );
  }
  if (archetype === "issue_resolution") {
    return <IssueViewer row={row} />;
  }
  if (archetype === "mcq_cot") {
    return (
      <div>
        <McqViewer row={row} choicesCol="options" answerCol="answer" />
        {row.cot_content ? (
          <details>
            <summary>Chain-of-thought</summary>
            <pre className="code-block">{String(row.cot_content)}</pre>
          </details>
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
    <div>
      <div className="navigator panel">
        <button type="button" disabled={index <= 0 || loading} onClick={() => setIndex(index - 1)}>
          Previous
        </button>
        <label>
          Sample {total ? index + 1 : 0} / {total}
          <input
            type="range"
            min={0}
            max={Math.max(total - 1, 0)}
            value={index}
            onChange={(event) => setIndex(Number(event.target.value))}
            disabled={!total || loading}
          />
        </label>
        <button
          type="button"
          disabled={!total || index >= total - 1 || loading}
          onClick={() => setIndex(index + 1)}
        >
          Next
        </button>
        <label>
          Find by {meta.id_column}
          <input
            value={idSearch}
            onChange={(event) => setIdSearch(event.target.value)}
            placeholder={`Search ${meta.id_column}`}
          />
        </label>
        <button type="button" onClick={handleSearch} disabled={loading}>
          Search
        </button>
      </div>
      {error ? <div className="error">{error}</div> : null}
      {loading && !payload ? <p className="muted">Loading sample…</p> : null}
      {payload ? renderSample(datasetId, meta, payload, privateTests) : null}
      {payload?.row ? (
        <details>
          <summary>Raw JSON</summary>
          <pre className="code-block">{JSON.stringify(payload.row, null, 2)}</pre>
        </details>
      ) : null}
    </div>
  );
}
