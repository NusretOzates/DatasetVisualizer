import { Badge } from "@/components/ui/badge";
import { McqViewer } from "../McqViewer";
import type { SampleViewerProps } from "../types";

export function GlobalMmluViewer({ row }: SampleViewerProps) {
  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-2">
        {row.subject ? <Badge variant="outline">{String(row.subject)}</Badge> : null}
        {row.language ? <Badge variant="secondary">{String(row.language)}</Badge> : null}
        {row.locale ? <Badge variant="secondary">{String(row.locale)}</Badge> : null}
      </div>
      <McqViewer row={row} />
    </div>
  );
}
