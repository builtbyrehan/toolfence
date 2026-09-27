import { useQuery } from "@tanstack/react-query"

import { getAuditLog } from "@/features/audit/api"

export const auditQueryKey = [
  "toolfence",
  "audit",
] as const

export function useAuditLog() {
  return useQuery({
    queryKey: auditQueryKey,
    queryFn: ({ signal }) =>
      getAuditLog(signal),
    refetchInterval: 3_000,
  })
}
