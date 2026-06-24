import { CodeEvalViewer as ViewerPrimitive } from "../CodeEvalViewer";
import type { SampleViewerProps } from "../types";

export function AppsViewer({ row }: SampleViewerProps) {
  return <ViewerPrimitive row={row} />;
}
