import { StructuredViewer } from "../StructuredViewer";
import type { SampleViewerProps } from "../types";

const CONFIG = {
  "heroFields": [
    "task",
    "description",
    "question",
    "reference_answer"
  ],
  "badgeFields": [
    "task_id",
    "occupation",
    "sector"
  ]
} as const;

export function GdpvalViewer({ row }: SampleViewerProps) {
  return <StructuredViewer row={row} config={CONFIG} />;
}
