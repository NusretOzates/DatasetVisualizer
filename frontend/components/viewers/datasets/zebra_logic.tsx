import { Badge } from "@/components/ui/badge";
import { McqViewer } from "../McqViewer";
import type { SampleViewerProps } from "../types";

export function ZebraLogicViewer({ row }: SampleViewerProps) {
  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-2">
        {row.puzzle_type ? <Badge variant="outline">{String(row.puzzle_type)}</Badge> : null}
        {row.difficulty ? <Badge variant="outline">{String(row.difficulty)}</Badge> : null}
      </div>
      <McqViewer row={row} />
    </div>
  );
}
