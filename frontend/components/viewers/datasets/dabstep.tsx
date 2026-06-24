import { StructuredViewer } from "../StructuredViewer";
import type { SampleViewerProps } from "../types";

const CONFIG = {
  "heroFields": [
    "question",
    "task",
    "instruction",
    "ground_truth"
  ],
  "badgeFields": [
    "task_id",
    "category"
  ]
} as const;

export function DabstepViewer({ row }: SampleViewerProps) {
  return <StructuredViewer row={row} config={CONFIG} />;
}
