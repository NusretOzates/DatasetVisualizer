import { MathViewer as ViewerPrimitive } from "../MathViewer";
import type { SampleViewerProps } from "../types";

export function Aime2026Viewer({ row, extras }: SampleViewerProps) {
  const solution = String(extras.solution ?? row.solution ?? "");
  return <ViewerPrimitive row={row} solution={solution || undefined} />;
}
