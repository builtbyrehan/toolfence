import { useQuery } from "@tanstack/react-query"

import { getTask } from "@/features/task/api"

export const taskQueryKey = [
  "toolfence",
  "task",
] as const

export function useTask() {
  return useQuery({
    queryKey: taskQueryKey,
    queryFn: ({ signal }) =>
      getTask(signal),
  })
}
