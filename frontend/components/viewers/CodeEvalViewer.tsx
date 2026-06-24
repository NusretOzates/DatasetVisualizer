"use client";

import { Badge } from "@/components/ui/badge";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { MarkdownMath } from "./MarkdownMath";

type CodeEvalViewerProps = {
  row: Record<string, unknown>;
};

function formatSubSteps(value: unknown): string {
  if (value == null) return "";
  if (typeof value === "string") return value;
  return JSON.stringify(value, null, 2);
}

export function CodeEvalViewer({ row }: CodeEvalViewerProps) {
  const prompt = String(
    row.question_content ??
      row.problem_description_main ??
      row.prompt ??
      row.text ??
      "",
  );
  const solution = String(
    row.canonical_solution ?? row.general_solution ?? row.solution ?? row.code ?? "",
  );
  const tests = String(row.test_code ?? row.general_tests ?? row.test ?? row.tests ?? "");
  const subSteps = formatSubSteps(row.sub_steps);

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-2">
        <Badge variant="outline">
          ID: {String(row.question_id ?? row.problem_id ?? row.task_id ?? "—")}
        </Badge>
        {row.problem_name ? (
          <Badge variant="outline">{String(row.problem_name)}</Badge>
        ) : null}
        {row.difficulty ? <Badge variant="outline">Difficulty: {String(row.difficulty)}</Badge> : null}
      </div>

      <div>
        <h4 className="text-sm font-medium text-muted-foreground">Prompt</h4>
        <MarkdownMath className="mt-2 text-sm">{prompt}</MarkdownMath>
      </div>

      {solution ? (
        <Accordion type="single" collapsible>
          <AccordionItem value="solution">
            <AccordionTrigger className="text-sm">Reference solution</AccordionTrigger>
            <AccordionContent>
              <pre className="code-block whitespace-pre-wrap">{solution}</pre>
            </AccordionContent>
          </AccordionItem>
        </Accordion>
      ) : null}

      {tests ? (
        <Accordion type="single" collapsible>
          <AccordionItem value="tests">
            <AccordionTrigger className="text-sm">Tests</AccordionTrigger>
            <AccordionContent>
              <pre className="code-block whitespace-pre-wrap">{tests}</pre>
            </AccordionContent>
          </AccordionItem>
        </Accordion>
      ) : null}

      {subSteps ? (
        <Accordion type="single" collapsible>
          <AccordionItem value="sub-steps">
            <AccordionTrigger className="text-sm">Sub-steps</AccordionTrigger>
            <AccordionContent>
              <pre className="code-block whitespace-pre-wrap">{subSteps}</pre>
            </AccordionContent>
          </AccordionItem>
        </Accordion>
      ) : null}
    </div>
  );
}
