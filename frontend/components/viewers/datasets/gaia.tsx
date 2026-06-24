import { GaiaViewer as ViewerPrimitive } from "../GaiaViewer";
import type { SampleViewerProps } from "../types";

export function GaiaViewer(props: SampleViewerProps) {
  return <ViewerPrimitive {...props} />;
}
