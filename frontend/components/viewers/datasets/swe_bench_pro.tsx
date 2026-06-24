import { IssueViewer as ViewerPrimitive } from "../IssueViewer";
import type { SampleViewerProps } from "../types";

export function SweBenchProViewer({ row }: SampleViewerProps) {
  return <ViewerPrimitive row={row} />;
}
