"use client";

import { useState } from "react";
import { McqViewer } from "./McqViewer";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
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

type HleViewerProps = {
  row: Record<string, unknown>;
};

export function HleViewer({ row }: HleViewerProps) {
  const hasImage = Boolean(row.has_image);
  const answerType = String(row.answer_type ?? "—");
  const modality = hasImage ? "Multimodal" : "Text only";

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-2">
        <Badge variant="outline">ID: {String(row.id ?? "—")}</Badge>
        <Badge variant="outline">{String(row.category ?? "—")}</Badge>
        <Badge variant="outline">{modality}</Badge>
        <Badge variant="secondary">{answerType}</Badge>
      </div>
      <div>
        <h3 className="text-sm font-medium text-muted-foreground">Question</h3>
        <p className="mt-2 text-base leading-relaxed">{String(row.question ?? "")}</p>
      </div>
      {hasImage && row.image ? (
        // eslint-disable-next-line @next/next/no-img-element
        <img
          src={String(row.image)}
          alt="Question"
          className="max-h-96 rounded-lg border object-contain"
        />
      ) : null}
      {row.answer ? (
        <div className="rounded-lg border border-emerald-300 bg-emerald-50 px-4 py-3 text-sm text-emerald-900">
          <strong>
            {answerType === "multipleChoice" ? "Correct answer" : "Exact answer"}:
          </strong>{" "}
          {String(row.answer)}
        </div>
      ) : null}
      {row.author_name ? (
        <p className="text-sm text-muted-foreground">Contributor: {String(row.author_name)}</p>
      ) : null}
      {row.rationale ? (
        <Accordion type="single" collapsible>
          <AccordionItem value="rationale">
            <AccordionTrigger>Rationale</AccordionTrigger>
            <AccordionContent className="space-y-3">
              <p className="text-sm leading-relaxed">{String(row.rationale)}</p>
              {row.rationale_image ? (
                // eslint-disable-next-line @next/next/no-img-element
                <img
                  src={String(row.rationale_image)}
                  alt="Rationale"
                  className="max-h-64 rounded-lg border object-contain"
                />
              ) : null}
            </AccordionContent>
          </AccordionItem>
        </Accordion>
      ) : null}
      {answerType === "multipleChoice" ? <McqViewer row={row} answerCol="answer" /> : null}
    </div>
  );
}

type MathViewerProps = {
  row: Record<string, unknown>;
  solution?: string;
};

export function MathViewer({ row, solution }: MathViewerProps) {
  const [revealed, setRevealed] = useState(false);

  return (
    <div className="space-y-4">
      <Badge variant="outline">Problem {String(row.problem_idx ?? "—")}</Badge>
      <div>
        <h3 className="text-sm font-medium text-muted-foreground">Problem</h3>
        <p className="mt-2 whitespace-pre-wrap text-sm leading-relaxed">
          {String(row.problem ?? "")}
        </p>
      </div>
      <Button variant="secondary" size="sm" onClick={() => setRevealed(true)}>
        Reveal gold answer
      </Button>
      {revealed ? (
        <div className="rounded-lg border border-emerald-300 bg-emerald-50 px-4 py-3 text-sm text-emerald-900">
          {String(row.answer ?? "")}
        </div>
      ) : null}
      {solution ? (
        <Accordion type="single" collapsible>
          <AccordionItem value="solution">
            <AccordionTrigger>Solution / working</AccordionTrigger>
            <AccordionContent className="whitespace-pre-wrap text-sm">{solution}</AccordionContent>
          </AccordionItem>
        </Accordion>
      ) : null}
    </div>
  );
}

type ArxivMathViewerProps = {
  row: Record<string, unknown>;
  extras: Record<string, unknown>;
};

export function ArxivMathViewer({ row, extras }: ArxivMathViewerProps) {
  const [revealed, setRevealed] = useState(false);
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
        <div className="space-y-4">
          <div>
            <h3 className="text-sm font-medium text-muted-foreground">Problem</h3>
            <p className="mt-2 whitespace-pre-wrap text-sm leading-relaxed">
              {String(row.problem ?? "")}
            </p>
          </div>
          <Button variant="secondary" size="sm" onClick={() => setRevealed(true)}>
            Reveal gold answer
          </Button>
          {revealed ? (
            <div className="rounded-lg border border-emerald-300 bg-emerald-50 px-4 py-3 text-sm text-emerald-900">
              {String(row.answer ?? "")}
            </div>
          ) : null}
        </div>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">Paper</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 text-sm">
            <p className="font-medium">{String(row.title ?? "—")}</p>
            <p className="text-muted-foreground">{String(row.authors ?? "—")}</p>
            {row.source ? (
              <a
                href={`https://arxiv.org/abs/${String(row.source)}`}
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center gap-1 text-sm text-primary hover:underline"
              >
                View on arXiv
                <ExternalLink className="size-3.5" />
              </a>
            ) : null}
          </CardContent>
        </Card>
      </div>

      {modelRuns.length ? (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Model runs</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
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

            <div className="space-y-2">
              <p className="text-sm font-medium">Inspect attempt</p>
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
                <div>
                  <p className="mb-2 text-xs font-medium text-muted-foreground">Parsed answer</p>
                  <pre className="code-block">{String(selectedRun.parsed_answer ?? "")}</pre>
                </div>
                <div>
                  <p className="mb-2 text-xs font-medium text-muted-foreground">Gold answer</p>
                  <pre className="code-block">{String(selectedRun.gold_answer ?? "")}</pre>
                </div>
              </div>
            ) : null}

            {fullRun ? (
              <Accordion type="multiple">
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
        <p className="text-sm text-muted-foreground">No model runs for this problem.</p>
      )}
    </div>
  );
}
