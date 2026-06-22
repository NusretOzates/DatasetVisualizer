import { DatasetPageClient } from "@/components/DatasetPageClient";

const DATASET_IDS = [
  "mmlu",
  "mmlu_pro",
  "gpqa_diamond",
  "global_mmlu",
  "mmmlu",
  "aime_2026",
  "hle",
  "livecodebench_v6",
  "swe_bench_verified",
  "swe_bench_multilingual",
  "swe_bench_pro",
  "arxivmath_0526",
];

export function generateStaticParams() {
  return DATASET_IDS.map((id) => ({ id }));
}

type PageProps = {
  params: Promise<{ id: string }>;
};

export default async function DatasetPage({ params }: PageProps) {
  const { id } = await params;
  return <DatasetPageClient datasetId={id} />;
}
