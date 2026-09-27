import { apiGet } from "@/api/client"
import { API_ENDPOINTS } from "@/api/endpoints"
import type { Capabilities } from "@/features/capabilities/types"

export function getCapabilities(
  signal?: AbortSignal,
): Promise<Capabilities> {
  return apiGet<Capabilities>(
    API_ENDPOINTS.capabilities,
    signal,
  )
}
