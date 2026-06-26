import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { MarkdownMath } from "../MarkdownMath";
import type { SampleViewerProps } from "../types";

type ModelPrediction = {
  algorithm_name?: string;
  actual_prediction?: string;
  prediction_created_at?: string;
  source?: string;
};

function parsePredictions(value: unknown): ModelPrediction[] {
  if (value == null) return [];
  let parsed: unknown = value;
  if (typeof value === "string") {
    const trimmed = value.trim();
    if (!trimmed) return [];
    try {
      parsed = JSON.parse(trimmed);
    } catch {
      return [];
    }
  }
  if (!Array.isArray(parsed)) return [];
  return parsed.filter((item): item is ModelPrediction => Boolean(item) && typeof item === "object");
}

export function FuturebenchViewer({ row }: SampleViewerProps) {
  const question = typeof row.question === "string" ? row.question.trim() : "";
  const predictions = parsePredictions(row.predictions);
  const resolvedResult = row.result != null ? String(row.result) : "";

  if (!question && !predictions.length) {
    return <p className="text-sm text-muted-foreground">No fields to display.</p>;
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-2">
        {row.event_id != null ? <Badge variant="outline">event id: {String(row.event_id)}</Badge> : null}
        {row.event_type ? <Badge variant="secondary">{String(row.event_type)}</Badge> : null}
        {resolvedResult ? <Badge variant="outline">resolved: {resolvedResult}</Badge> : null}
        {predictions.length ? (
          <Badge variant="secondary">{predictions.length} model predictions</Badge>
        ) : null}
      </div>

      {question ? (
        <div>
          <h4 className="text-sm font-medium text-muted-foreground">Question</h4>
          <MarkdownMath className="mt-2 text-sm leading-relaxed">{question}</MarkdownMath>
        </div>
      ) : null}

      {row.open_to_bet_until ? (
        <p className="text-sm text-muted-foreground">
          Open to bet until{" "}
          <span className="font-mono text-foreground">{String(row.open_to_bet_until)}</span>
        </p>
      ) : null}

      {predictions.length ? (
        <div>
          <h4 className="text-sm font-medium text-muted-foreground">Model predictions</h4>
          <div className="mt-2 overflow-x-auto rounded-lg border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Algorithm</TableHead>
                  <TableHead>Prediction</TableHead>
                  <TableHead>Created at</TableHead>
                  <TableHead>Source</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {predictions.map((prediction, index) => {
                  const algorithm = prediction.algorithm_name ?? "—";
                  const actual = prediction.actual_prediction ?? "—";
                  const matchesResult =
                    resolvedResult &&
                    actual.toLowerCase() === resolvedResult.toLowerCase();
                  return (
                    <TableRow key={`${algorithm}-${index}`}>
                      <TableCell className="font-mono text-xs">{algorithm}</TableCell>
                      <TableCell>
                        <span className={matchesResult ? "font-medium text-green-700 dark:text-green-400" : undefined}>
                          {actual}
                        </span>
                      </TableCell>
                      <TableCell className="text-xs text-muted-foreground">
                        {prediction.prediction_created_at ?? "—"}
                      </TableCell>
                      <TableCell className="text-xs text-muted-foreground">
                        {prediction.source ?? "—"}
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          </div>
        </div>
      ) : null}
    </div>
  );
}
