import { apiGet } from "@/api/client"
import { API_ENDPOINTS } from "@/api/endpoints"
import type { Policy } from "@/features/policy/types"

export function getPolicy(
  signal?: AbortSignal,
): Promise<Policy> {
  return apiGet<Policy>(
    API_ENDPOINTS.policy,
    signal,
  )
}
