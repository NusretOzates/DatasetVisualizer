type IssueViewerProps = {
  row: Record<string, unknown>;
};

const TEST_LIST_PREVIEW_LIMIT = 50;

function TestList({ tests, title }: { tests: unknown; title: string }) {
  if (!Array.isArray(tests) || tests.length === 0) {
    return <p className="muted">{title}: none</p>;
  }
  return (
    <div>
      <strong>
        {title} ({tests.length})
      </strong>
      <ul>
        {tests.slice(0, TEST_LIST_PREVIEW_LIMIT).map((test, index) => (
          <li key={index}>
            <code>{String(test)}</code>
          </li>
        ))}
      </ul>
      {tests.length > TEST_LIST_PREVIEW_LIMIT ? (
        <p className="muted">
          … and {tests.length - TEST_LIST_PREVIEW_LIMIT} more
        </p>
      ) : null}
    </div>
  );
}

export function IssueViewer({ row }: IssueViewerProps) {
  return (
    <div>
      <p className="muted">
        <strong>{String(row.instance_id ?? "—")}</strong> ·{" "}
        <code>{String(row.repo ?? "—")}</code> @ <code>{String(row.base_commit ?? "—")}</code>
      </p>
      {row.repo_language ? <p className="muted">Language: {String(row.repo_language)}</p> : null}
      {row.difficulty ? <p className="muted">Difficulty: {String(row.difficulty)}</p> : null}
      <h4>Problem statement</h4>
      <div>{String(row.problem_statement ?? "")}</div>
      {row.hints_text ? (
        <details>
          <summary>Hints (issue comments)</summary>
          <div>{String(row.hints_text)}</div>
        </details>
      ) : null}
      {row.patch ? (
        <details>
          <summary>Gold patch</summary>
          <pre className="code-block">{String(row.patch)}</pre>
        </details>
      ) : null}
      {row.test_patch ? (
        <details>
          <summary>Test patch</summary>
          <pre className="code-block">{String(row.test_patch)}</pre>
        </details>
      ) : null}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem" }}>
        <TestList tests={row.fail_to_pass} title="FAIL_TO_PASS" />
        <TestList tests={row.pass_to_pass} title="PASS_TO_PASS" />
      </div>
      {row.requirements ? (
        <details>
          <summary>Requirements</summary>
          <div>{String(row.requirements)}</div>
        </details>
      ) : null}
      {row.interface ? (
        <details>
          <summary>Interface</summary>
          <pre className="code-block">{String(row.interface)}</pre>
        </details>
      ) : null}
    </div>
  );
}
