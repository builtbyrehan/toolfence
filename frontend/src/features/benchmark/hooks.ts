import { useQuery } from "@tanstack/react-query"

import { getBenchmark } from "@/features/benchmark/api"

export const benchmarkQueryKey = [
  "toolfence",
  "benchmark",
] as const

export function useBenchmark() {
  return useQuery({
    queryKey: benchmarkQueryKey,
    queryFn: ({ signal }) =>
      getBenchmark(signal),
  })
}
