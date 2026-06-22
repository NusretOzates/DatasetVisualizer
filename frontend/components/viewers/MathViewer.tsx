"use client";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { ProblemCard } from "./ProblemCard";

type MathViewerProps = {
  row: Record<string, unknown>;
  solution?: string;
};

export function MathViewer({ row, solution }: MathViewerProps) {
  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-2">
        <Badge variant="outline">Problem {String(row.problem_idx ?? "—")}</Badge>
      </div>

      <ProblemCard
        problem={String(row.problem ?? "")}
        answer={String(row.answer ?? "")}
      />

      {solution ? (
        <Card>
          <CardContent className="pt-6">
            <Accordion type="single" collapsible>
              <AccordionItem value="solution">
                <AccordionTrigger>Solution / working</AccordionTrigger>
                <AccordionContent className="whitespace-pre-wrap text-sm">
                  {solution}
                </AccordionContent>
              </AccordionItem>
            </Accordion>
          </CardContent>
        </Card>
      ) : null}
    </div>
  );
}
