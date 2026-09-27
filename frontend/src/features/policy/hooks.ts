import { useQuery } from "@tanstack/react-query"

import { getPolicy } from "@/features/policy/api"

export const policyQueryKey = [
  "toolfence",
  "policy",
] as const

export function usePolicy() {
  return useQuery({
    queryKey: policyQueryKey,
    queryFn: ({ signal }) =>
      getPolicy(signal),
  })
}
