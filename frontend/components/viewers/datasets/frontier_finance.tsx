import { StructuredViewer } from "../StructuredViewer";
import type { SampleViewerProps } from "../types";

const CONFIG = {
  "heroFields": [
    "prompt"
  ],
  "badgeFields": [
    "sample_id",
    "eval_type"
  ],
  "hideFields": [
    "attachments"
  ]
} as const;

export function FrontierFinanceViewer({ row }: SampleViewerProps) {
  return <StructuredViewer row={row} config={CONFIG} />;
}
