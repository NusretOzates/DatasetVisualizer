"use client";

import { useState } from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { ExternalLink } from "lucide-react";
import { ProblemCard } from "./ProblemCard";

type ArxivMathViewerProps = {
  row: Record<string, unknown>;
  extras: Record<string, unknown>;
};

export function ArxivMathViewer({ row, extras }: ArxivMathViewerProps) {
  const [attemptIndex, setAttemptIndex] = useState("0");
  const modelRuns = Array.isArray(extras.model_runs)
    ? (extras.model_runs as Record<string, unknown>[])
    : [];
  const fullRuns = Array.isArray(extras.full_runs)
    ? (extras.full_runs as Record<string, unknown>[])
    : [];
  const selectedRun = modelRuns[Number(attemptIndex)];
  const fullRun = fullRuns.find(
    (run) =>
      run.model_name === selectedRun?.model_name &&
      run.idx_answer === selectedRun?.idx_answer,
  );

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap gap-2">
        <Badge variant="outline">Problem {String(row.problem_idx ?? "—")}</Badge>
        <Badge variant="outline">arXiv: {String(row.source ?? "—")}</Badge>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <ProblemCard
          problem={String(row.problem ?? "")}
          answer={String(row.answer ?? "")}
        />

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-base">Paper</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 text-sm">
            <p className="font-medium leading-snug">{String(row.title ?? "—")}</p>
            <p className="text-muted-foreground">{String(row.authors ?? "—")}</p>
            {row.source ? (
              <Button asChild variant="outline" size="sm">
                <a
                  href={`https://arxiv.org/abs/${String(row.source)}`}
                  target="_blank"
                  rel="noreferrer"
                >
                  View on arXiv
                  <ExternalLink className="size-3.5" />
                </a>
              </Button>
            ) : null}
          </CardContent>
        </Card>
      </div>

      {modelRuns.length ? (
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-base">Model runs</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="overflow-hidden rounded-lg border">
              <Table>
                <TableHeader>
                  <TableRow>
                    {Object.keys(modelRuns[0]).map((column) => (
                      <TableHead key={column}>{column}</TableHead>
                    ))}
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {modelRuns.map((run, index) => (
                    <TableRow key={index}>
                      {Object.keys(modelRuns[0]).map((column) => (
                        <TableCell key={column} className="text-xs">
                          {String(run[column] ?? "")}
                        </TableCell>
                      ))}
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>

            <div className="space-y-2">
              <Label>Inspect attempt</Label>
              <Select value={attemptIndex} onValueChange={setAttemptIndex}>
                <SelectTrigger className="w-full max-w-md">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {modelRuns.map((run, index) => (
                    <SelectItem key={index} value={String(index)}>
                      {String(run.model_name)} · attempt {String(run.idx_answer)}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {selectedRun ? (
              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-2">
                  <p className="text-xs font-medium text-muted-foreground">Parsed answer</p>
                  <pre className="code-block">{String(selectedRun.parsed_answer ?? "")}</pre>
                </div>
                <div className="space-y-2">
                  <p className="text-xs font-medium text-muted-foreground">Gold answer</p>
                  <pre className="code-block">{String(selectedRun.gold_answer ?? "")}</pre>
                </div>
              </div>
            ) : null}

            {fullRun ? (
              <Accordion type="multiple" className="space-y-2">
                <AccordionItem value="response">
                  <AccordionTrigger>Full model response</AccordionTrigger>
                  <AccordionContent>
                    <pre className="code-block">{String(fullRun.answer ?? "")}</pre>
                  </AccordionContent>
                </AccordionItem>
                <AccordionItem value="message">
                  <AccordionTrigger>User message</AccordionTrigger>
                  <AccordionContent>
                    <pre className="code-block">{String(fullRun.user_message ?? "")}</pre>
                  </AccordionContent>
                </AccordionItem>
              </Accordion>
            ) : null}
          </CardContent>
        </Card>
      ) : (
        <Card>
          <CardContent className="py-6 text-sm text-muted-foreground">
            No model runs for this problem.
          </CardContent>
        </Card>
      )}
    </div>
  );
}
