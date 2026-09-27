import { useAuditLog } from "@/features/audit/hooks"
import { useBenchmark } from "@/features/benchmark/hooks"
import { useCapabilities } from "@/features/capabilities/hooks"
import { usePolicy } from "@/features/policy/hooks"
import { useTask } from "@/features/task/hooks"


export function useDashboardData() {
  const taskQuery = useTask()
  const policyQuery = usePolicy()
  const capabilitiesQuery = useCapabilities()
  const auditQuery = useAuditLog()
  const benchmarkQuery = useBenchmark()

  const isLoading =
    taskQuery.isLoading ||
    policyQuery.isLoading ||
    capabilitiesQuery.isLoading ||
    auditQuery.isLoading ||
    benchmarkQuery.isLoading

  const isFetching =
    taskQuery.isFetching ||
    policyQuery.isFetching ||
    capabilitiesQuery.isFetching ||
    auditQuery.isFetching ||
    benchmarkQuery.isFetching

  const isError =
    taskQuery.isError ||
    policyQuery.isError ||
    capabilitiesQuery.isError ||
    auditQuery.isError ||
    benchmarkQuery.isError

  const error =
    taskQuery.error ??
    policyQuery.error ??
    capabilitiesQuery.error ??
    auditQuery.error ??
    benchmarkQuery.error ??
    null

  async function refetchAll() {
    await Promise.all([
      taskQuery.refetch(),
      policyQuery.refetch(),
      capabilitiesQuery.refetch(),
      auditQuery.refetch(),
      benchmarkQuery.refetch(),
    ])
  }

  return {
    task: taskQuery.data ?? null,
    policy: policyQuery.data ?? null,
    capabilities: capabilitiesQuery.data ?? null,
    audit: auditQuery.data ?? null,
    benchmark: benchmarkQuery.data ?? null,

    isLoading,
    isFetching,
    isError,
    error,

    refetchAll,
  }
}
