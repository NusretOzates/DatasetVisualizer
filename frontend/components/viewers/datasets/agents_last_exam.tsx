import { StructuredViewer } from "../StructuredViewer";
import type { SampleViewerProps } from "../types";

const CONFIG = {
  "heroFields": [
    "task_prompt",
    "summary"
  ],
  "badgeFields": [
    "task_id",
    "category",
    "subdomain",
    "task_split"
  ],
  "hideFields": []
} as const;

export function AgentsLastExamViewer({ row }: SampleViewerProps) {
  return <StructuredViewer row={row} config={CONFIG} />;
}
