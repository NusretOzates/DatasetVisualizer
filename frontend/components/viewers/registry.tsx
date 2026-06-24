"use client";

import type { ComponentType, ReactNode } from "react";
import type { DatasetMeta } from "@/lib/types";
import { GenericViewer } from "./GenericViewer";
import type { SampleViewerProps } from "./types";
import { Aime2026Viewer } from "./datasets/aime_2026";
import { AppsViewer } from "./datasets/apps";
import { ArcAgi2Viewer } from "./datasets/arc_agi_2";
import { ArcChallengeViewer } from "./datasets/arc_challenge";
import { Arxivmath0526Viewer } from "./datasets/arxivmath_0526";
import { CoconotViewer } from "./datasets/coconot";
import { CommonsenseqaViewer } from "./datasets/commonsenseqa";
import { DabstepViewer } from "./datasets/dabstep";
import { EvoevalDifficultViewer } from "./datasets/evoeval_difficult";
import { FuturebenchViewer } from "./datasets/futurebench";
import { FuturexViewer } from "./datasets/futurex";
import { GaiaViewer } from "./datasets/gaia";
import { Gaia2Viewer } from "./datasets/gaia2";
import { GdpvalViewer } from "./datasets/gdpval";
import { GlobalMmluViewer } from "./datasets/global_mmlu";
import { GpqaDiamondViewer } from "./datasets/gpqa_diamond";
import { Gsm1kViewer } from "./datasets/gsm1k";
import { Gsm8kViewer } from "./datasets/gsm8k";
import { GsmPlusViewer } from "./datasets/gsm_plus";
import { GsmSymbolicViewer } from "./datasets/gsm_symbolic";
import { HellaswagViewer } from "./datasets/hellaswag";
import { HleViewer } from "./datasets/hle";
import { HumanevalViewer } from "./datasets/humaneval";
import { HumanevalPlusViewer } from "./datasets/humaneval_plus";
import { IfbenchViewer } from "./datasets/ifbench";
import { IfevalViewer } from "./datasets/ifeval";
import { LivecodebenchV6Viewer } from "./datasets/livecodebench_v6";
import { LivemcpbenchViewer } from "./datasets/livemcpbench";
import { MathViewer } from "./datasets/math";
import { Math500Viewer } from "./datasets/math_500";
import { MathArenaViewer } from "./datasets/math_arena";
import { MathHardViewer } from "./datasets/math_hard";
import { MbppViewer } from "./datasets/mbpp";
import { MbppPlusViewer } from "./datasets/mbpp_plus";
import { MmluViewer } from "./datasets/mmlu";
import { MmluProViewer } from "./datasets/mmlu_pro";
import { MmluReduxViewer } from "./datasets/mmlu_redux";
import { MmmluViewer } from "./datasets/mmmlu";
import { MrcrViewer } from "./datasets/mrcr";
import { MtobViewer } from "./datasets/mtob";
import { OpenbookqaViewer } from "./datasets/openbookqa";
import { PaperbenchViewer } from "./datasets/paperbench";
import { PiqaViewer } from "./datasets/piqa";
import { RulerViewer } from "./datasets/ruler";
import { ScicodeViewer } from "./datasets/scicode";
import { SweBenchMultilingualViewer } from "./datasets/swe_bench_multilingual";
import { SweBenchProViewer } from "./datasets/swe_bench_pro";
import { SweBenchVerifiedViewer } from "./datasets/swe_bench_verified";
import { Tau3BenchViewer } from "./datasets/tau3_bench";
import { WinograndeViewer } from "./datasets/winogrande";
import { ZebraLogicViewer } from "./datasets/zebra_logic";

const DATASET_VIEWERS: Record<string, ComponentType<SampleViewerProps>> = {
  aime_2026: Aime2026Viewer,
  apps: AppsViewer,
  arc_agi_2: ArcAgi2Viewer,
  arc_challenge: ArcChallengeViewer,
  arxivmath_0526: Arxivmath0526Viewer,
  coconot: CoconotViewer,
  commonsenseqa: CommonsenseqaViewer,
  dabstep: DabstepViewer,
  evoeval_difficult: EvoevalDifficultViewer,
  futurebench: FuturebenchViewer,
  futurex: FuturexViewer,
  gaia: GaiaViewer,
  gaia2: Gaia2Viewer,
  gdpval: GdpvalViewer,
  global_mmlu: GlobalMmluViewer,
  gpqa_diamond: GpqaDiamondViewer,
  gsm1k: Gsm1kViewer,
  gsm8k: Gsm8kViewer,
  gsm_plus: GsmPlusViewer,
  gsm_symbolic: GsmSymbolicViewer,
  hellaswag: HellaswagViewer,
  hle: HleViewer,
  humaneval: HumanevalViewer,
  humaneval_plus: HumanevalPlusViewer,
  ifbench: IfbenchViewer,
  ifeval: IfevalViewer,
  livecodebench_v6: LivecodebenchV6Viewer,
  livemcpbench: LivemcpbenchViewer,
  math: MathViewer,
  math_500: Math500Viewer,
  math_arena: MathArenaViewer,
  math_hard: MathHardViewer,
  mbpp: MbppViewer,
  mbpp_plus: MbppPlusViewer,
  mmlu: MmluViewer,
  mmlu_pro: MmluProViewer,
  mmlu_redux: MmluReduxViewer,
  mmmlu: MmmluViewer,
  mrcr: MrcrViewer,
  mtob: MtobViewer,
  openbookqa: OpenbookqaViewer,
  paperbench: PaperbenchViewer,
  piqa: PiqaViewer,
  ruler: RulerViewer,
  scicode: ScicodeViewer,
  swe_bench_multilingual: SweBenchMultilingualViewer,
  swe_bench_pro: SweBenchProViewer,
  swe_bench_verified: SweBenchVerifiedViewer,
  tau3_bench: Tau3BenchViewer,
  winogrande: WinograndeViewer,
  zebra_logic: ZebraLogicViewer,
};

export function renderSample(
  meta: DatasetMeta,
  payload: { row: Record<string, unknown> | null; extras: Record<string, unknown> },
  privateTests: Record<string, unknown>[] | null,
  privateTestsLoading = false,
): ReactNode {
  if (!payload.row) {
    return <p className="text-sm text-muted-foreground">No sample available.</p>;
  }

  const Viewer = DATASET_VIEWERS[meta.id];
  if (!Viewer) {
    if (process.env.NODE_ENV === "development") {
      return <GenericViewer row={payload.row} />;
    }
    return <pre className="code-block">{JSON.stringify(payload.row, null, 2)}</pre>;
  }

  return (
    <Viewer
      row={payload.row}
      extras={payload.extras}
      privateTests={privateTests}
      privateTestsLoading={privateTestsLoading}
    />
  );
}
