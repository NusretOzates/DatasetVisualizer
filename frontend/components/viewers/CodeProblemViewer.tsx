import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { Badge } from "@/components/ui/badge";

type CodeProblemViewerProps = {
  row: Record<string, unknown>;
  privateTests?: Record<string, unknown>[] | null;
  privateTestsLoading?: boolean;
  privateTestLimit?: number;
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
    return <p className="text-sm text-muted-foreground">No {title.toLowerCase()}.</p>;
  }
  const visible = limit ? cases.slice(0, limit) : cases;
  return (
    <div className="space-y-3">
      <h4 className="text-sm font-medium">
        {title} <Badge variant="secondary">{cases.length.toLocaleString()}</Badge>
      </h4>
      <Accordion type="single" collapsible defaultValue="test-0">
        {visible.map((testCase, index) => {
          const testtype = String(testCase.testtype ?? "stdin");
          const input = formatTestValue(String(testCase.input ?? ""), testtype);
          const output = formatTestValue(String(testCase.output ?? ""), testtype);
          return (
            <AccordionItem key={index} value={`test-${index}`}>
              <AccordionTrigger className="text-sm">
                Test {index + 1} · {testtype}
              </AccordionTrigger>
              <AccordionContent>
                <div className="grid gap-4 md:grid-cols-2">
                  <div>
                    <p className="mb-2 text-xs font-medium text-muted-foreground">Input</p>
                    <pre className="code-block">{input}</pre>
                  </div>
                  <div>
                    <p className="mb-2 text-xs font-medium text-muted-foreground">
                      Expected output
                    </p>
                    <pre className="code-block">{output}</pre>
                  </div>
                </div>
              </AccordionContent>
            </AccordionItem>
          );
        })}
      </Accordion>
      {limit && cases.length > limit ? (
        <p className="text-sm text-muted-foreground">
          Showing first {limit} of {cases.length.toLocaleString()} cases.
        </p>
      ) : null}
    </div>
  );
}

export function CodeProblemViewer({
  row,
  privateTests = null,
  privateTestsLoading = false,
  privateTestLimit = 10,
}: CodeProblemViewerProps) {
  const publicTests = Array.isArray(row.public_test_cases)
    ? (row.public_test_cases as Record<string, unknown>[])
    : [];

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-2">
        <Badge variant="outline">ID: {String(row.question_id ?? "—")}</Badge>
        <Badge variant="outline">Platform: {String(row.platform ?? "—")}</Badge>
        <Badge variant="outline">Difficulty: {String(row.difficulty ?? "—")}</Badge>
      </div>
      {row.question_title ? (
        <h3 className="text-xl font-semibold tracking-tight">{String(row.question_title)}</h3>
      ) : null}
      <div>
        <h4 className="text-sm font-medium text-muted-foreground">Problem</h4>
        <p className="mt-2 whitespace-pre-wrap text-sm leading-relaxed">
          {String(row.question_content ?? "")}
        </p>
      </div>
      {row.starter_code ? (
        <div>
          <h4 className="mb-2 text-sm font-medium text-muted-foreground">Starter code</h4>
          <pre className="code-block">{String(row.starter_code)}</pre>
        </div>
      ) : null}
      <TestCases cases={publicTests} title="Public test cases" />
      {privateTestsLoading ? (
        <p className="text-sm text-muted-foreground">Loading private test cases…</p>
      ) : privateTests ? (
        <TestCases
          cases={privateTests}
          title="Private test cases"
          limit={privateTestLimit}
        />
      ) : null}
    </div>
  );
}
