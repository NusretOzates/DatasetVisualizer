"use client";

import { Badge } from "@/components/ui/badge";
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
        solution={solution}
      />
    </div>
  );
}
