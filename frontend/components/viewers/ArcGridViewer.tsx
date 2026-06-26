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

function parsePuzzle(row: Record<string, unknown>): ArcPuzzle | ArcPair[] | null {
  const raw = row.puzzle_json ?? row.question;
  if (typeof raw === "object" && raw !== null) return raw as ArcPuzzle | ArcPair[];
  if (typeof raw !== "string" || !raw.trim()) return null;
  try {
    return JSON.parse(raw) as ArcPuzzle | ArcPair[];
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

function parseGrid(value: unknown): ArcGrid | null {
  if (isGrid(value)) return value;
  if (typeof value !== "string") return null;
  const trimmed = value.trim();
  if (!trimmed) return null;
  for (const candidate of [trimmed, `[${trimmed}]`]) {
    try {
      const parsed: unknown = JSON.parse(candidate);
      if (isGrid(parsed)) return parsed;
    } catch {
      continue;
    }
  }
  return null;
}

function parsePair(pair: ArcPair | Record<string, unknown>): ArcPair {
  return {
    input: parseGrid(pair.input) ?? undefined,
    output: parseGrid(pair.output) ?? undefined,
  };
}

function parseFewshots(value: unknown): ArcPair[] {
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
  return parsed
    .filter((item): item is Record<string, unknown> => Boolean(item) && typeof item === "object")
    .map((item) => parsePair(item))
    .filter((pair) => pair.input || pair.output);
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
  const normalized = parsePair(pair);
  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-base">{title}</CardTitle>
      </CardHeader>
      <CardContent className="grid gap-4 md:grid-cols-2">
        {isGrid(normalized.input) ? <GridView grid={normalized.input} title="Input" /> : null}
        {isGrid(normalized.output) ? <GridView grid={normalized.output} title="Output" /> : null}
      </CardContent>
    </Card>
  );
}

export function ArcGridViewer({ row }: { row: Record<string, unknown> }) {
  const puzzle = parsePuzzle(row);
  const fewshotPairs = parseFewshots(row.fewshots);
  const topLevelPairs = Array.isArray(puzzle) ? puzzle.map((pair) => parsePair(pair)) : [];
  const trainPairs =
    !Array.isArray(puzzle) && Array.isArray(puzzle?.train)
      ? puzzle.train.map((pair) => parsePair(pair))
      : [];
  const testPairs =
    !Array.isArray(puzzle) && Array.isArray(puzzle?.test)
      ? puzzle.test.map((pair) => parsePair(pair))
      : [];
  const inlinePair =
    !Array.isArray(puzzle) && (puzzle?.input || puzzle?.output)
      ? [parsePair({ input: puzzle.input, output: puzzle.output })]
      : [];
  const puzzlePairs = [...trainPairs, ...inlinePair, ...topLevelPairs, ...testPairs].filter(
    (pair) => pair.input || pair.output,
  );

  if (!puzzle && !fewshotPairs.length) {
    return <pre className="code-block">{String(row.puzzle_json ?? row.question ?? "")}</pre>;
  }

  return (
    <div className="flex flex-col gap-4">
      <div className="flex flex-wrap gap-2">
        <Badge variant="outline">ID: {String(row.sample_id ?? row.id ?? "—")}</Badge>
        <Badge variant="secondary">
          {fewshotPairs.length.toLocaleString()} few-shot · {puzzlePairs.length.toLocaleString()}{" "}
          puzzle
        </Badge>
      </div>

      {fewshotPairs.map((pair, index) => (
        <PairView key={`fewshot-${index}`} pair={pair} title={`Few-shot example ${index + 1}`} />
      ))}

      {puzzlePairs.map((pair, index) => (
        <PairView key={`puzzle-${index}`} pair={pair} title={`Test puzzle ${index + 1}`} />
      ))}
    </div>
  );
}
