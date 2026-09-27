import { apiGet } from "@/api/client"
import { API_ENDPOINTS } from "@/api/endpoints"
import type { Benchmark } from "@/features/benchmark/types"

export function getBenchmark(
  signal?: AbortSignal,
): Promise<Benchmark> {
  return apiGet<Benchmark>(
    API_ENDPOINTS.benchmark,
    signal,
  )
}
