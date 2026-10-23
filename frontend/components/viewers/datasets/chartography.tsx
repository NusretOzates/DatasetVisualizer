import { StructuredViewer } from "../StructuredViewer";
import type { SampleViewerProps } from "../types";

const CONFIG = {
  "heroFields": [
    "prompt",
    "golden_answer"
  ],
  "badgeFields": [
    "task_id",
    "domain_combined",
    "source_type"
  ],
  "hideFields": []
} as const;

export function ChartographyViewer({ row }: SampleViewerProps) {
  return <StructuredViewer row={row} config={CONFIG} />;
}
