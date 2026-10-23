import { StructuredViewer } from "../StructuredViewer";
import type { SampleViewerProps } from "../types";

const CONFIG = {
  "heroFields": [
    "question",
    "answer"
  ],
  "badgeFields": [
    "id",
    "question_type",
    "media_count"
  ],
  "hideFields": [
    "messages"
  ]
} as const;

export function ZerobenchMainViewer({ row }: SampleViewerProps) {
  return <StructuredViewer row={row} config={CONFIG} />;
}
