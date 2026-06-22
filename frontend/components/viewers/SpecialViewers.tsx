"use client";

import { useState } from "react";
import { McqViewer } from "./McqViewer";

type HleViewerProps = {
  row: Record<string, unknown>;
};

export function HleViewer({ row }: HleViewerProps) {
  const hasImage = Boolean(row.has_image);
  const answerType = String(row.answer_type ?? "—");
  const modality = hasImage ? "Multimodal" : "Text only";

  return (
    <div>
      <p className="muted">
        ID: {String(row.id ?? "—")} · Category: {String(row.category ?? "—")} · Subject:{" "}
        {String(row.raw_subject ?? "—")} · Type: {answerType} · Modality: {modality}
      </p>
      <h3>Question</h3>
      <p>{String(row.question ?? "")}</p>
      {hasImage && row.image ? (
        // eslint-disable-next-line @next/next/no-img-element
        <img src={String(row.image)} alt="Question" style={{ maxWidth: "100%" }} />
      ) : null}
      {row.answer ? (
        <div className="mcq-option correct">
          <strong>
            {answerType === "multipleChoice" ? "Correct answer" : "Exact answer"}:
          </strong>{" "}
          {String(row.answer)}
        </div>
      ) : null}
      {row.author_name ? <p className="muted">Contributor: {String(row.author_name)}</p> : null}
      {row.rationale ? (
        <details>
          <summary>Rationale</summary>
          <p>{String(row.rationale)}</p>
          {row.rationale_image ? (
            // eslint-disable-next-line @next/next/no-img-element
            <img src={String(row.rationale_image)} alt="Rationale" style={{ maxWidth: "100%" }} />
          ) : null}
        </details>
      ) : null}
      {answerType === "multipleChoice" ? <McqViewer row={row} answerCol="answer" /> : null}
    </div>
  );
}

type MathViewerProps = {
  row: Record<string, unknown>;
  solution?: string;
};

export function MathViewer({ row, solution }: MathViewerProps) {
  const [revealed, setRevealed] = useState(false);

  return (
    <div>
      <p className="muted">Problem: {String(row.problem_idx ?? "—")}</p>
      <h3>Problem</h3>
      <p>{String(row.problem ?? "")}</p>
      <button type="button" onClick={() => setRevealed(true)}>
        Reveal gold answer
      </button>
      {revealed ? <div className="mcq-option correct">{String(row.answer ?? "")}</div> : null}
      {solution ? (
        <details>
          <summary>Solution / working</summary>
          <p>{solution}</p>
        </details>
      ) : null}
    </div>
  );
}

type ArxivMathViewerProps = {
  row: Record<string, unknown>;
  extras: Record<string, unknown>;
};

export function ArxivMathViewer({ row, extras }: ArxivMathViewerProps) {
  const [revealed, setRevealed] = useState(false);
  const [attemptIndex, setAttemptIndex] = useState(0);
  const modelRuns = Array.isArray(extras.model_runs)
    ? (extras.model_runs as Record<string, unknown>[])
    : [];
  const fullRuns = Array.isArray(extras.full_runs)
    ? (extras.full_runs as Record<string, unknown>[])
    : [];
  const selectedRun = modelRuns[attemptIndex];
  const fullRun = fullRuns.find(
    (run) =>
      run.model_name === selectedRun?.model_name &&
      run.idx_answer === selectedRun?.idx_answer,
  );

  return (
    <div>
      <p className="muted">
        Problem: {String(row.problem_idx ?? "—")} · arXiv: {String(row.source ?? "—")}
      </p>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1.5rem" }}>
        <div>
          <h3>Problem</h3>
          <p>{String(row.problem ?? "")}</p>
          <button type="button" onClick={() => setRevealed(true)}>
            Reveal gold answer
          </button>
          {revealed ? <div className="mcq-option correct">{String(row.answer ?? "")}</div> : null}
        </div>
        <div>
          <h3>Paper</h3>
          <p>
            <strong>{String(row.title ?? "—")}</strong>
          </p>
          <p>{String(row.authors ?? "—")}</p>
          {row.source ? (
            <a href={`https://arxiv.org/abs/${String(row.source)}`} target="_blank" rel="noreferrer">
              View on arXiv
            </a>
          ) : null}
        </div>
      </div>
      {modelRuns.length ? (
        <div className="panel" style={{ marginTop: "1rem" }}>
          <h4>Model runs</h4>
          <div className="table-wrap">
            <table className="data-table">
              <thead>
                <tr>
                  {Object.keys(modelRuns[0]).map((column) => (
                    <th key={column}>{column}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {modelRuns.map((run, index) => (
                  <tr key={index}>
                    {Object.keys(modelRuns[0]).map((column) => (
                      <td key={column}>{String(run[column] ?? "")}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <label>
            Inspect attempt
            <select
              value={attemptIndex}
              onChange={(event) => setAttemptIndex(Number(event.target.value))}
            >
              {modelRuns.map((run, index) => (
                <option key={index} value={index}>
                  {String(run.model_name)} · attempt {String(run.idx_answer)}
                </option>
              ))}
            </select>
          </label>
          {selectedRun ? (
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem" }}>
              <div>
                <strong>Parsed answer</strong>
                <pre className="code-block">{String(selectedRun.parsed_answer ?? "")}</pre>
              </div>
              <div>
                <strong>Gold answer</strong>
                <pre className="code-block">{String(selectedRun.gold_answer ?? "")}</pre>
              </div>
            </div>
          ) : null}
          {fullRun ? (
            <>
              <details>
                <summary>Full model response</summary>
                <pre className="code-block">{String(fullRun.answer ?? "")}</pre>
              </details>
              <details>
                <summary>User message</summary>
                <pre className="code-block">{String(fullRun.user_message ?? "")}</pre>
              </details>
            </>
          ) : null}
        </div>
      ) : (
        <p className="muted">No model runs for this problem.</p>
      )}
    </div>
  );
}
