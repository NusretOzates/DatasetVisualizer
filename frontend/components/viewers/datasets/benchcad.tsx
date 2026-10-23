import { StructuredViewer } from "../StructuredViewer";
import type { SampleViewerProps } from "../types";

const CONFIG = {
  "heroFields": [
    "canonical_solution"
  ],
  "badgeFields": [
    "stem",
    "family",
    "variant",
    "difficulty",
    "base_plane",
    "standard"
  ],
  "hideFields": [
    "code"
  ]
} as const;

export function BenchcadViewer({ row }: SampleViewerProps) {
  return <StructuredViewer row={row} config={CONFIG} />;
}
