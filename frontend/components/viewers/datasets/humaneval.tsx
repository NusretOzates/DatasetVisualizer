import { CodeEvalViewer as ViewerPrimitive } from "../CodeEvalViewer";
import type { SampleViewerProps } from "../types";

export function HumanevalViewer({ row }: SampleViewerProps) {
  return <ViewerPrimitive row={row} />;
}
