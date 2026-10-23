import { StructuredViewer } from "../StructuredViewer";
import type { SampleViewerProps } from "../types";

const CONFIG = {
  "heroFields": [],
  "badgeFields": [
    "task_id",
    "release",
    "source_repo"
  ],
  "hideFields": []
} as const;

export function OsworldV21Viewer({ row }: SampleViewerProps) {
  return <StructuredViewer row={row} config={CONFIG} />;
}
