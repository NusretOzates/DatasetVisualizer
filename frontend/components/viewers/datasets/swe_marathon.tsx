import { StructuredViewer } from "../StructuredViewer";
import type { SampleViewerProps } from "../types";

const CONFIG = {
  "heroFields": [
    "instruction",
    "description"
  ],
  "badgeFields": [
    "task_id",
    "category",
    "difficulty"
  ],
  "hideFields": [
    "files"
  ]
} as const;

export function SweMarathonViewer({ row }: SampleViewerProps) {
  return <StructuredViewer row={row} config={CONFIG} />;
}
