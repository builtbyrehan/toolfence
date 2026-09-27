import { useOutletContext } from "react-router-dom"

import { AuditTable } from "@/components/dashboard/AuditTable"
import { SectionHeading } from "@/components/shared/SectionHeading"
import type { DashboardContextValue } from "@/pages/dashboard/DashboardLayout"


function toAuditExecutionStatus(
  status: string,
): "EXECUTED" | "NOT_EXECUTED" | "FAILED" {
  if (status === "SUCCEEDED") {
    return "EXECUTED"
  }

  if (status === "FAILED") {
    return "FAILED"
  }

  return "NOT_EXECUTED"
}


export function AuditPage() {
  const {
    task,
    policy,
    audit,
  } = useOutletContext<DashboardContextValue>()

  if (
    !task ||
    !policy ||
    !audit
  ) {
    return null
  }

  const taskEvents =
    audit.events.filter(
      (event) =>
        event.taskId === task.taskId,
    )

  const currentPolicyEvents =
    taskEvents.filter(
      (event) =>
        event.policyId === policy.policyId,
    )

  const auditEvents =
    [...taskEvents]
      .reverse()
      .map((event) => ({
        eventId: event.eventId,
        tool: event.tool,
        resource: event.resource,
        decision: event.decision,
        reasonCode: event.reasonCode,
        executionStatus:
          toAuditExecutionStatus(
            event.executionStatus,
          ),
        policyId:
          event.policyId ?? "—",
      }))

  const allowedCount =
    taskEvents.filter(
      (event) =>
        event.decision === "ALLOW",
    ).length

  const deniedCount =
    taskEvents.filter(
      (event) =>
        event.decision === "DENY",
    ).length

  const currentPolicyCount =
    currentPolicyEvents.length

  return (
    <>
      <SectionHeading
        eyebrow="Authorization evidence"
        title="Audit log"
        description="Append-only authorization evidence for ToolFence-protected requests. ALLOW and DENY decisions remain separate from backend execution status."
      />

      <div
        className="
          mt-5
          grid gap-4
          sm:grid-cols-2
          xl:grid-cols-4
        "
      >
        <AuditMetric
          label="Task events"
          value={String(taskEvents.length)}
          detail={`All evidence for ${task.taskId}`}
        />

        <AuditMetric
          label="Current policy"
          value={String(currentPolicyCount)}
          detail="Events matching active policy ID"
        />

        <AuditMetric
          label="Allowed"
          value={String(allowedCount)}
          detail="Requests authorized"
        />

        <AuditMetric
          label="Denied"
          value={String(deniedCount)}
          detail="Requests blocked before execution"
        />
      </div>

      <div className="mt-8">
        <AuditTable
          events={auditEvents}
        />
      </div>

      <div
        className="
          mt-6
          rounded-xl
          border border-white/[0.05]
          bg-white/[0.015]
          px-4 py-3
        "
      >
        <p
          className="
            text-xs
            leading-5
            text-slate-600
          "
        >
          Audit history may include earlier policy instances and deny-by-default
          events for the same task. The active policy is identified independently
          by its current policy ID.
        </p>
      </div>
    </>
  )
}


function AuditMetric({
  label,
  value,
  detail,
}: {
  label: string
  value: string
  detail: string
}) {
  return (
    <div
      className="
        rounded-xl
        border border-white/[0.06]
        bg-white/[0.02]
        p-5
      "
    >
      <p
        className="
          tf-mono
          text-[9px]
          uppercase
          tracking-[0.14em]
          text-slate-600
        "
      >
        {label}
      </p>

      <p
        className="
          mt-3
          text-2xl
          font-semibold
          tracking-tight
          text-slate-100
        "
      >
        {value}
      </p>

      <p
        className="
          mt-1
          text-xs
          leading-5
          text-slate-600
        "
      >
        {detail}
      </p>
    </div>
  )
}
