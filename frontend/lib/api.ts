import { Client } from "@gradio/client";
import type {
  Catalog,
  DatasetMeta,
  FilterOptionsResponse,
  OverviewPayload,
  SamplePayload,
} from "./types";

let clientPromise: Promise<Client> | null = null;

function getApiUrl(): string {
  if (process.env.NEXT_PUBLIC_API_URL) {
    return process.env.NEXT_PUBLIC_API_URL;
  }
  if (typeof window !== "undefined") {
    // Next.js dev (port 3000) talks to the Gradio backend on 7860 by default.
    if (window.location.port === "3000") {
      return "http://localhost:7860";
    }
    return window.location.origin;
  }
  return "http://localhost:7860";
}

function formatApiError(error: unknown, context?: string): string {
  if (error instanceof Error && error.message.trim()) {
    return error.message;
  }
  if (typeof error === "object" && error !== null) {
    const message = (error as { message?: unknown }).message;
    if (typeof message === "string" && message.trim()) {
      return message;
    }
  }
  if (context) {
    return `API request failed: ${context}`;
  }
  return "API request failed";
}

async function getClient(): Promise<Client> {
  if (!clientPromise) {
    clientPromise = Client.connect(getApiUrl()).catch((error) => {
      clientPromise = null;
      throw new Error(formatApiError(error, "connect"));
    });
  }
  return clientPromise;
}

async function predict<T>(apiName: string, payload: Record<string, unknown>): Promise<T> {
  const client = await getClient();
  try {
    const result = await client.predict(apiName, payload);
    const data = (result as { data?: unknown[] }).data;
    if (!Array.isArray(data) || data.length === 0) {
      throw new Error(`Unexpected API response from ${apiName}`);
    }
    return data[0] as T;
  } catch (error) {
    throw new Error(formatApiError(error, apiName));
  }
}

export async function fetchCatalog(): Promise<Catalog> {
  return predict<Catalog>("/get_catalog", {});
}

export async function fetchDatasetMeta(datasetId: string): Promise<DatasetMeta> {
  return predict<DatasetMeta>("/get_dataset_meta", { dataset_id: datasetId });
}

export async function fetchFilterOptions(
  datasetId: string,
  params: Record<string, unknown>,
): Promise<FilterOptionsResponse> {
  return predict<FilterOptionsResponse>("/get_filter_options", {
    dataset_id: datasetId,
    params_json: JSON.stringify(params),
  });
}

export async function fetchOverview(
  datasetId: string,
  params: Record<string, unknown>,
  filters: Record<string, unknown>,
): Promise<OverviewPayload> {
  return predict<OverviewPayload>("/get_overview", {
    dataset_id: datasetId,
    params_json: JSON.stringify(params),
    filters_json: JSON.stringify(filters),
  });
}

export async function fetchSample(
  datasetId: string,
  index: number,
  params: Record<string, unknown>,
  filters: Record<string, unknown>,
): Promise<SamplePayload> {
  return predict<SamplePayload>("/get_sample", {
    dataset_id: datasetId,
    index,
    params_json: JSON.stringify(params),
    filters_json: JSON.stringify(filters),
  });
}

export async function decodePrivateTests(raw: string): Promise<{ cases: Record<string, unknown>[] }> {
  return predict<{ cases: Record<string, unknown>[] }>("/decode_private_tests", { raw });
}
