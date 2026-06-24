import { ArcGridViewer as ViewerPrimitive } from "../ArcGridViewer";
import type { SampleViewerProps } from "../types";

export function ArcAgi2Viewer({ row }: SampleViewerProps) {
  return <ViewerPrimitive row={row} />;
}
