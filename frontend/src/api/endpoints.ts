export const API_ENDPOINTS = {
  health: "/api/health",
  task: "/api/task",
  policy: "/api/policy",
  capabilities: "/api/capabilities",
  audit: "/api/audit",
  benchmark: "/api/benchmark",
  demo: "/api/demo",
} as const

export type ApiEndpoint =
  (typeof API_ENDPOINTS)[keyof typeof API_ENDPOINTS]
