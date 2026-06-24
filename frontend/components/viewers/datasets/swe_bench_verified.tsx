import { IssueViewer as ViewerPrimitive } from "../IssueViewer";
import type { SampleViewerProps } from "../types";

export function SweBenchVerifiedViewer({ row }: SampleViewerProps) {
  return <ViewerPrimitive row={row} />;
}
