import { useQuery } from "@tanstack/react-query"

import { getCapabilities } from "@/features/capabilities/api"

export const capabilitiesQueryKey = [
  "toolfence",
  "capabilities",
] as const

export function useCapabilities() {
  return useQuery({
    queryKey: capabilitiesQueryKey,
    queryFn: ({ signal }) =>
      getCapabilities(signal),
  })
}
