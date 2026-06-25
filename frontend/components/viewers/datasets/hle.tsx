import { HleViewer as ViewerPrimitive } from "../HleViewer";
import type { SampleViewerProps } from "../types";

export function HleViewer({ row }: SampleViewerProps) {
  return <ViewerPrimitive row={row} />;
}
