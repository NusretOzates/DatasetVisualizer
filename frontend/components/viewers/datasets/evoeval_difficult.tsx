import { CodeEvalViewer as ViewerPrimitive } from "../CodeEvalViewer";
import type { SampleViewerProps } from "../types";

export function EvoevalDifficultViewer({ row }: SampleViewerProps) {
  return <ViewerPrimitive row={row} />;
}
