import { StructuredViewer } from "../StructuredViewer";
import type { SampleViewerProps } from "../types";

const CONFIG = {
  "heroFields": [
    "question",
    "answer"
  ],
  "badgeFields": [
    "uid"
  ],
  "hideFields": []
} as const;

export function OfficeqaProV2Viewer({ row }: SampleViewerProps) {
  return <StructuredViewer row={row} config={CONFIG} />;
}
