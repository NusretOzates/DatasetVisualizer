import { StructuredViewer } from "../StructuredViewer";
import type { SampleViewerProps } from "../types";

const CONFIG = {
  "heroFields": [
    "question_content",
    "canonical_solution"
  ],
  "badgeFields": [
    "stem",
    "family",
    "difficulty"
  ],
  "hideFields": [
    "code"
  ]
} as const;

export function BenchcadViewer({ row }: SampleViewerProps) {
  return <StructuredViewer row={row} config={CONFIG} />;
}
