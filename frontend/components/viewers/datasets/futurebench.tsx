import { StructuredViewer } from "../StructuredViewer";
import type { SampleViewerProps } from "../types";

const CONFIG = {
  "heroFields": [
    "question",
    "prompt",
    "answer"
  ],
  "badgeFields": [
    "task_id",
    "category"
  ]
} as const;

export function FuturebenchViewer({ row }: SampleViewerProps) {
  return <StructuredViewer row={row} config={CONFIG} />;
}
