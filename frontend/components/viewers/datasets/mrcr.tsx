import { StructuredViewer } from "../StructuredViewer";
import type { SampleViewerProps } from "../types";

const CONFIG = {
  "heroFields": [
    "prompt",
    "answer",
    "context"
  ],
  "badgeFields": [
    "task_id",
    "sample_id"
  ]
} as const;

export function MrcrViewer({ row }: SampleViewerProps) {
  return <StructuredViewer row={row} config={CONFIG} />;
}
