import { StructuredViewer } from "../StructuredViewer";
import type { SampleViewerProps } from "../types";

const CONFIG = {
  "heroFields": [
    "source_text",
    "target_text",
    "prompt"
  ],
  "badgeFields": [
    "task_id",
    "language_pair"
  ]
} as const;

export function MtobViewer({ row }: SampleViewerProps) {
  return <StructuredViewer row={row} config={CONFIG} />;
}
