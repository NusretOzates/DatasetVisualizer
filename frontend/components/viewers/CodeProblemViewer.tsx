type CodeProblemViewerProps = {
  row: Record<string, unknown>;
};

function formatTestValue(raw: string, testtype: string): string {
  const stripped = raw.trim();
  if (testtype === "functional") return stripped;
  try {
    return JSON.stringify(JSON.parse(stripped), null, 2);
  } catch {
    return raw;
  }
}

function TestCases({
  cases,
  title,
  limit,
}: {
  cases: Record<string, unknown>[];
  title: string;
  limit?: number;
}) {
  if (!cases.length) {
    return <p className="muted">No {title.toLowerCase()}.</p>;
  }
  const visible = limit ? cases.slice(0, limit) : cases;
  return (
    <div>
      <h4>
        {title} ({cases.length.toLocaleString()} total)
      </h4>
      {visible.map((testCase, index) => {
        const testtype = String(testCase.testtype ?? "stdin");
        const input = formatTestValue(String(testCase.input ?? ""), testtype);
        const output = formatTestValue(String(testCase.output ?? ""), testtype);
        return (
          <details key={index} open={index === 0}>
            <summary>
              Test {index + 1} · {testtype}
            </summary>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem" }}>
              <div>
                <strong>Input</strong>
                <pre className="code-block">{input}</pre>
              </div>
              <div>
                <strong>Expected output</strong>
                <pre className="code-block">{output}</pre>
              </div>
            </div>
          </details>
        );
      })}
      {limit && cases.length > limit ? (
        <p className="muted">
          Showing first {limit} of {cases.length.toLocaleString()} cases.
        </p>
      ) : null}
    </div>
  );
}

export function CodeProblemViewer({ row }: CodeProblemViewerProps) {
  const publicTests = Array.isArray(row.public_test_cases)
    ? (row.public_test_cases as Record<string, unknown>[])
    : [];

  return (
    <div>
      <p className="muted">
        ID: {String(row.question_id ?? "—")} · Platform: {String(row.platform ?? "—")} ·
        Difficulty: {String(row.difficulty ?? "—")}
      </p>
      {row.question_title ? <h3>{String(row.question_title)}</h3> : null}
      <h4>Problem</h4>
      <p>{String(row.question_content ?? "")}</p>
      {row.starter_code ? (
        <>
          <h4>Starter code</h4>
          <pre className="code-block">{String(row.starter_code)}</pre>
        </>
      ) : null}
      <TestCases cases={publicTests} title="Public test cases" />
    </div>
  );
}
