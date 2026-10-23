import { StructuredViewer } from "../StructuredViewer";
import type { SampleViewerProps } from "../types";

const CONFIG = {
  "heroFields": [
    "prompt"
  ],
  "badgeFields": [
    "task_id",
    "domain"
  ],
  "hideFields": []
} as const;

export function GdpPdfViewer({ row }: SampleViewerProps) {
  return <StructuredViewer row={row} config={CONFIG} />;
}
