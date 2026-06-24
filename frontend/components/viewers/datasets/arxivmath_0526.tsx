import { ArxivMathViewer as ViewerPrimitive } from "../ArxivMathViewer";
import type { SampleViewerProps } from "../types";

export function Arxivmath0526Viewer(props: SampleViewerProps) {
  return <ViewerPrimitive row={props.row} extras={props.extras} />;
}
