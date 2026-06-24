import { McqViewer } from "../McqViewer";
import type { SampleViewerProps } from "../types";

export function GpqaDiamondViewer({ row }: SampleViewerProps) {
  return <McqViewer row={row} />;
}
