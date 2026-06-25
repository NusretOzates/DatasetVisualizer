import { CodeEvalViewer as ViewerPrimitive } from "../CodeEvalViewer";
import type { SampleViewerProps } from "../types";

export function MbppViewer({ row }: SampleViewerProps) {
  return <ViewerPrimitive row={row} />;
}
