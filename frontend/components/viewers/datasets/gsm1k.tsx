import { MathViewer as ViewerPrimitive } from "../MathViewer";
import type { SampleViewerProps } from "../types";

export function Gsm1kViewer({ row, extras }: SampleViewerProps) {
  const solution = String(extras.solution ?? row.solution ?? "");
  return <ViewerPrimitive row={row} solution={solution || undefined} />;
}
