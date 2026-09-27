import { useOutletContext } from "react-router-dom"

import { ActivityTimeline } from "@/components/dashboard/ActivityTimeline"
import { SectionHeading } from "@/components/shared/SectionHeading"
import type { DashboardContextValue } from "@/pages/dashboard/DashboardLayout"


function toTimelineExecutionStatus(
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


function describeResult(
  tool: string,
  decision: "ALLOW" | "DENY",
  executionStatus: string,
  reasonCode: string,
): string {
  if (decision === "DENY") {
    return `Blocked by ToolFence · ${reasonCode}`
  }

  if (executionStatus === "FAILED") {
    return `${tool} was authorized, but backend execution failed.`
  }

  if (executionStatus === "SUCCEEDED") {
    return `${tool} authorized and executed successfully.`
  }

  return `${tool} authorization recorded.`
}


export function ActivityPage() {
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

  const currentPolicyEvents =
    audit.events.filter(
      (event) =>
        event.taskId === task.taskId &&
        event.policyId === policy.policyId,
    )

  const recentEvents =
    [...currentPolicyEvents]
      .reverse()
      .slice(0, 12)
      .reverse()

  const activityEvents =
    recentEvents.map((event) => ({
      id: event.eventId,
      tool: event.tool,
      resource: event.resource,
      decision: event.decision,
      executionStatus:
        toTimelineExecutionStatus(
          event.executionStatus,
        ),
      result: describeResult(
        event.tool,
        event.decision,
        event.executionStatus,
        event.reasonCode,
      ),
    }))

  const allowedCount =
    currentPolicyEvents.filter(
      (event) =>
        event.decision === "ALLOW",
    ).length

  const deniedCount =
    currentPolicyEvents.filter(
      (event) =>
        event.decision === "DENY",
    ).length

  const successfulCount =
    currentPolicyEvents.filter(
      (event) =>
        event.decision === "ALLOW" &&
        event.executionStatus === "SUCCEEDED",
    ).length

  return (
    <>
      <SectionHeading
        eyebrow="Runtime activity"
        title="Protected tool activity"
        description="Every protected request is checked against the active Task Capability Contract before ToolFence permits backend execution."
      />

      <div
        className="
          mt-5
          grid gap-4
          sm:grid-cols-3
        "
      >
        <ActivityMetric
          label="Requests"
          value={String(
            currentPolicyEvents.length
          )}
          detail="Recorded for current policy"
        />

        <ActivityMetric
          label="Allowed"
          value={String(allowedCount)}
          detail={`${successfulCount} executed successfully`}
        />

        <ActivityMetric
          label="Denied"
          value={String(deniedCount)}
          detail="Protected actions not executed"
        />
      </div>

      <div className="mt-8">
        <ActivityTimeline
          events={activityEvents}
        />
      </div>

      {activityEvents.length === 0 && (
        <div
          className="
            mt-8
            rounded-xl
            border border-white/[0.06]
            bg-white/[0.02]
            px-6 py-10
            text-center
          "
        >
          <p
            className="
              text-sm font-medium
              text-slate-400
            "
          >
            No protected tool activity yet
          </p>

          <p
            className="
              mt-2
              text-xs
              leading-5
              text-slate-600
            "
          >
            Runtime events will appear here after Bob invokes
            ToolFence-protected tools.
          </p>
        </div>
      )}
    </>
  )
}


function ActivityMetric({
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
          text-slate-600
        "
      >
        {detail}
      </p>
    </div>
  )
}
