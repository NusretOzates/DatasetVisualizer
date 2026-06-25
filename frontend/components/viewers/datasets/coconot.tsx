import { StructuredViewer } from "../StructuredViewer";
import type { SampleViewerProps } from "../types";

const CONFIG = {
  "heroFields": [
    "prompt",
    "response",
    "question"
  ],
  "badgeFields": [
    "id",
    "category",
    "label"
  ]
} as const;

export function CoconotViewer({ row }: SampleViewerProps) {
  return <StructuredViewer row={row} config={CONFIG} />;
}
