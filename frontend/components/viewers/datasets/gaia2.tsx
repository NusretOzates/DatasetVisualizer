import { GaiaViewer as ViewerPrimitive } from "../GaiaViewer";
import type { SampleViewerProps } from "../types";

export function Gaia2Viewer(props: SampleViewerProps) {
  return <ViewerPrimitive {...props} />;
}
