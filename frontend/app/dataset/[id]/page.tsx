import { DatasetPageClient } from "@/components/DatasetPageClient";
import { fetchCatalog } from "@/lib/api";

export async function generateStaticParams() {
  try {
    const catalog = await fetchCatalog();
    return catalog.categories.flatMap((category) =>
      category.datasets.map((dataset) => ({ id: dataset.id })),
    );
  } catch {
    return [];
  }
}

type PageProps = {
  params: Promise<{ id: string }>;
};

export default async function DatasetPage({ params }: PageProps) {
  const { id } = await params;
  return <DatasetPageClient datasetId={id} />;
}
