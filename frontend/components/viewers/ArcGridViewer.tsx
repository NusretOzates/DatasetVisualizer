"use client";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

type ArcGrid = number[][];
type ArcPair = {
  input?: ArcGrid;
  output?: ArcGrid;
};
type ArcPuzzle = {
  train?: ArcPair[];
  test?: ArcPair[];
  input?: ArcGrid;
  output?: ArcGrid;
};

const ARC_COLORS = [
  "#111827",
  "#2563eb",
  "#dc2626",
  "#16a34a",
  "#facc15",
  "#6b7280",
  "#db2777",
  "#f97316",
  "#06b6d4",
  "#7c3aed",
];

function parsePuzzle(row: Record<string, unknown>): ArcPuzzle | null {
  const raw = row.puzzle_json ?? row.question;
  if (typeof raw === "object" && raw !== null) return raw as ArcPuzzle;
  if (typeof raw !== "string" || !raw.trim()) return null;
  try {
    return JSON.parse(raw) as ArcPuzzle;
  } catch {
    return null;
  }
}

function isGrid(value: unknown): value is ArcGrid {
  return (
    Array.isArray(value) &&
    value.length > 0 &&
    value.every(
      (row) => Array.isArray(row) && row.every((cell) => Number.isInteger(Number(cell))),
    )
  );
}

function GridView({ grid, title }: { grid: ArcGrid; title: string }) {
  const width = Math.max(...grid.map((row) => row.length));
  return (
    <div className="flex flex-col gap-2">
      <p className="text-xs font-medium text-muted-foreground">{title}</p>
      <div
        className="inline-grid gap-0.5 rounded-lg border bg-muted p-2"
        style={{ gridTemplateColumns: `repeat(${width}, minmax(0, 1.25rem))` }}
      >
        {grid.flatMap((row, rowIndex) =>
          Array.from({ length: width }).map((_, columnIndex) => {
            const value = Number(row[columnIndex] ?? 0);
            return (
              <div
                key={`${rowIndex}-${columnIndex}`}
                title={String(value)}
                className="aspect-square rounded-[2px] border border-background/50"
                style={{ backgroundColor: ARC_COLORS[value] ?? ARC_COLORS[0] }}
              />
            );
          }),
        )}
      </div>
    </div>
  );
}

function PairView({ pair, title }: { pair: ArcPair; title: string }) {
  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-base">{title}</CardTitle>
      </CardHeader>
      <CardContent className="grid gap-4 md:grid-cols-2">
        {isGrid(pair.input) ? <GridView grid={pair.input} title="Input" /> : null}
        {isGrid(pair.output) ? <GridView grid={pair.output} title="Output" /> : null}
      </CardContent>
    </Card>
  );
}

export function ArcGridViewer({ row }: { row: Record<string, unknown> }) {
  const puzzle = parsePuzzle(row);
  const trainPairs = Array.isArray(puzzle?.train) ? puzzle.train : [];
  const testPairs = Array.isArray(puzzle?.test) ? puzzle.test : [];
  const inlinePair = puzzle?.input || puzzle?.output ? [{ input: puzzle.input, output: puzzle.output }] : [];
  const pairs = [...trainPairs, ...inlinePair];

  if (!puzzle) {
    return <pre className="code-block">{String(row.puzzle_json ?? row.question ?? "")}</pre>;
  }

  return (
    <div className="flex flex-col gap-4">
      <div className="flex flex-wrap gap-2">
        <Badge variant="outline">ID: {String(row.sample_id ?? row.id ?? "—")}</Badge>
        <Badge variant="secondary">
          {trainPairs.length.toLocaleString()} train · {testPairs.length.toLocaleString()} test
        </Badge>
      </div>

      {pairs.map((pair, index) => (
        <PairView key={index} pair={pair} title={`Training pair ${index + 1}`} />
      ))}

      {testPairs.map((pair, index) => (
        <PairView key={index} pair={pair} title={`Test pair ${index + 1}`} />
      ))}
    </div>
  );
}
