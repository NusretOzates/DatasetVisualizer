import { StructuredViewer } from "../StructuredViewer";
import type { SampleViewerProps } from "../types";

const CONFIG = {
  "heroFields": [
    "input",
    "context",
    "question",
    "answer"
  ],
  "badgeFields": [
    "task_id",
    "category",
    "length"
  ]
} as const;

export function RulerViewer({ row }: SampleViewerProps) {
  return <StructuredViewer row={row} config={CONFIG} />;
}
