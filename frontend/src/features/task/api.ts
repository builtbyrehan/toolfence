import { apiGet } from "@/api/client"
import { API_ENDPOINTS } from "@/api/endpoints"
import type { Task } from "@/features/task/types"

export function getTask(
  signal?: AbortSignal,
): Promise<Task> {
  return apiGet<Task>(
    API_ENDPOINTS.task,
    signal,
  )
}
