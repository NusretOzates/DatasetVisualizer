import { Badge } from "@/components/ui/badge";
import { CodeEvalViewer } from "../CodeEvalViewer";
import type { SampleViewerProps } from "../types";

export function CritptViewer({ row }: SampleViewerProps) {
  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-2">
        {row.problem_id ? <Badge variant="outline">{String(row.problem_id)}</Badge> : null}
        {row.problem_type ? <Badge variant="secondary">{String(row.problem_type)}</Badge> : null}
        {row.metadata_tag ? (
          <Badge variant="outline">{String(row.metadata_tag).trim()}</Badge>
        ) : null}
      </div>
      <CodeEvalViewer row={row} />
    </div>
  );
}
