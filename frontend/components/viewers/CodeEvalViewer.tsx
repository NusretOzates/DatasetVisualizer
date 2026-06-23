"use client";

import { Badge } from "@/components/ui/badge";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";

type CodeEvalViewerProps = {
  row: Record<string, unknown>;
};

export function CodeEvalViewer({ row }: CodeEvalViewerProps) {
  const prompt = String(row.question_content ?? row.prompt ?? row.text ?? "");
  const solution = String(row.canonical_solution ?? row.solution ?? row.code ?? "");
  const tests = String(row.test_code ?? row.test ?? row.tests ?? "");

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-2">
        <Badge variant="outline">ID: {String(row.question_id ?? row.task_id ?? "—")}</Badge>
        {row.difficulty ? <Badge variant="outline">Difficulty: {String(row.difficulty)}</Badge> : null}
      </div>

      <div>
        <h4 className="text-sm font-medium text-muted-foreground">Prompt</h4>
        <pre className="code-block mt-2 whitespace-pre-wrap">{prompt}</pre>
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
    </div>
  );
}
