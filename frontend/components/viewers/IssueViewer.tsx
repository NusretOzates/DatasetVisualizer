import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { Badge } from "@/components/ui/badge";

type IssueViewerProps = {
  row: Record<string, unknown>;
};

const TEST_LIST_PREVIEW_LIMIT = 50;

function TestList({ tests, title }: { tests: unknown; title: string }) {
  if (!Array.isArray(tests) || tests.length === 0) {
    return <p className="text-sm text-muted-foreground">{title}: none</p>;
  }
  return (
    <div className="space-y-2">
      <p className="text-sm font-medium">
        {title} <Badge variant="secondary">{tests.length}</Badge>
      </p>
      <ul className="space-y-1 text-sm">
        {tests.slice(0, TEST_LIST_PREVIEW_LIMIT).map((test, index) => (
          <li key={index} className="font-mono text-xs text-muted-foreground">
            {String(test)}
          </li>
        ))}
      </ul>
      {tests.length > TEST_LIST_PREVIEW_LIMIT ? (
        <p className="text-xs text-muted-foreground">
          … and {tests.length - TEST_LIST_PREVIEW_LIMIT} more
        </p>
      ) : null}
    </div>
  );
}

export function IssueViewer({ row }: IssueViewerProps) {
  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-2">
        <Badge>{String(row.instance_id ?? "—")}</Badge>
        <Badge variant="outline">{String(row.repo ?? "—")}</Badge>
        <Badge variant="outline" className="font-mono text-xs">
          {String(row.base_commit ?? "—")}
        </Badge>
      </div>
      {row.repo_language ? (
        <p className="text-sm text-muted-foreground">Language: {String(row.repo_language)}</p>
      ) : null}
      {row.difficulty ? (
        <p className="text-sm text-muted-foreground">Difficulty: {String(row.difficulty)}</p>
      ) : null}
      <div>
        <h4 className="text-sm font-medium text-muted-foreground">Problem statement</h4>
        <div className="mt-2 whitespace-pre-wrap text-sm leading-relaxed">
          {String(row.problem_statement ?? "")}
        </div>
      </div>
      <Accordion type="multiple" className="w-full">
        {row.hints_text ? (
          <AccordionItem value="hints">
            <AccordionTrigger>Hints (issue comments)</AccordionTrigger>
            <AccordionContent className="whitespace-pre-wrap text-sm">
              {String(row.hints_text)}
            </AccordionContent>
          </AccordionItem>
        ) : null}
        {row.patch ? (
          <AccordionItem value="patch">
            <AccordionTrigger>Gold patch</AccordionTrigger>
            <AccordionContent>
              <pre className="code-block">{String(row.patch)}</pre>
            </AccordionContent>
          </AccordionItem>
        ) : null}
        {row.test_patch ? (
          <AccordionItem value="test-patch">
            <AccordionTrigger>Test patch</AccordionTrigger>
            <AccordionContent>
              <pre className="code-block">{String(row.test_patch)}</pre>
            </AccordionContent>
          </AccordionItem>
        ) : null}
        {row.requirements ? (
          <AccordionItem value="requirements">
            <AccordionTrigger>Requirements</AccordionTrigger>
            <AccordionContent className="whitespace-pre-wrap text-sm">
              {String(row.requirements)}
            </AccordionContent>
          </AccordionItem>
        ) : null}
        {row.interface ? (
          <AccordionItem value="interface">
            <AccordionTrigger>Interface</AccordionTrigger>
            <AccordionContent>
              <pre className="code-block">{String(row.interface)}</pre>
            </AccordionContent>
          </AccordionItem>
        ) : null}
      </Accordion>
      <div className="grid gap-4 md:grid-cols-2">
        <TestList tests={row.fail_to_pass} title="FAIL_TO_PASS" />
        <TestList tests={row.pass_to_pass} title="PASS_TO_PASS" />
      </div>
    </div>
  );
}
