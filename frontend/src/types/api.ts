export type PolicyDecision =
  | "ALLOW"
  | "DENY"

export type PolicyLifecycleStatus =
  | "ACTIVE"
  | "COMPLETED"
  | "REVOKED"
  | "EXPIRED"

export type HealthResponse = {
  status: string
  service: string
}

export type TaskResponse = {
  taskId: string
  task: string
}

export type CapabilityGrant = {
  tool: string
  resource: string
}

export type PolicyResponse = {
  taskId: string
  policyId: string
  status: PolicyLifecycleStatus
  grants: CapabilityGrant[]
  grantedCount: number
}

export type CapabilityResponse = {
  tool: string
  granted: boolean
  resource: string | null
}

export type CapabilitiesResponse = {
  total: number
  granted: number
  excluded: number
  privilegeReductionPercent: number
  capabilities: CapabilityResponse[]
}

export type AuditEventResponse = {
  eventId: number
  taskId: string | null
  policyId: string | null
  tool: string
  resource: string
  decision: PolicyDecision
  reasonCode: string
  executionStatus: string
  timestamp: string | null
}

export type AuditResponse = {
  total: number
  events: AuditEventResponse[]
}

export type BenchmarkGroupResult = {
  label: string
  total: number
  correct: number
}

export type BenchmarkResponse = {
  totalCases: number
  matchedCases: number
  groundTruthMatchPercent: number
  forbiddenActionBlockingPercent: number
  falseDenialPercent: number
  boundaryAccuracyPercent: number
  privilegeReductionPercent: number
  meanPolicyEvaluationMs: number
  maxPolicyEvaluationMs: number
  groups?: BenchmarkGroupResult[]
}

export type DashboardResponse = {
  task: TaskResponse
  policy: PolicyResponse
  capabilities: CapabilitiesResponse
  audit: AuditResponse
  benchmark: BenchmarkResponse
}

export type ApiErrorResponse = {
  detail:
    | string
    | {
        message?: string
        code?: string
      }
    | unknown
}
