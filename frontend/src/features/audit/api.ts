import { apiGet } from "@/api/client"
import { API_ENDPOINTS } from "@/api/endpoints"
import type { AuditLog } from "@/features/audit/types"

export function getAuditLog(
  signal?: AbortSignal,
): Promise<AuditLog> {
  return apiGet<AuditLog>(
    API_ENDPOINTS.audit,
    signal,
  )
}
