import { AgentBenchViewer as ViewerPrimitive } from "../AgentBenchViewer";
import type { SampleViewerProps } from "../types";

export function LivemcpbenchViewer(props: SampleViewerProps) {
  return <ViewerPrimitive {...props} />;
}
