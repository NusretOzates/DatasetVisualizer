import { McqViewer } from "../McqViewer";
import type { SampleViewerProps } from "../types";

export function PiqaViewer({ row }: SampleViewerProps) {
  return <McqViewer row={row} />;
}
