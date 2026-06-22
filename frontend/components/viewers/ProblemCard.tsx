"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Eye, EyeOff } from "lucide-react";

type ProblemCardProps = {
  problem: string;
  answer: string;
};

export function ProblemCard({ problem, answer }: ProblemCardProps) {
  const [revealed, setRevealed] = useState(false);

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-base">Problem</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <p className="whitespace-pre-wrap text-sm leading-relaxed">{problem}</p>
        <Button variant="outline" size="sm" onClick={() => setRevealed((current) => !current)}>
          {revealed ? <EyeOff className="size-4" /> : <Eye className="size-4" />}
          {revealed ? "Hide gold answer" : "Reveal gold answer"}
        </Button>
        {revealed ? (
          <div className="rounded-lg border border-emerald-300 bg-emerald-50 px-4 py-3 text-sm text-emerald-900">
            <p className="mb-1 text-xs font-medium uppercase tracking-wide text-emerald-700">
              Gold answer
            </p>
            {answer}
          </div>
        ) : null}
      </CardContent>
    </Card>
  );
}
