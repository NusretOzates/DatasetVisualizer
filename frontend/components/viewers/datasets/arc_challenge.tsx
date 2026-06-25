import { Badge } from "@/components/ui/badge";
import { McqViewer } from "../McqViewer";
import type { SampleViewerProps } from "../types";

export function ArcChallengeViewer({ row }: SampleViewerProps) {
  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-2">
        {row.subject ? <Badge variant="outline">{String(row.subject)}</Badge> : null}
      </div>
      <McqViewer row={row} />
    </div>
  );
}
