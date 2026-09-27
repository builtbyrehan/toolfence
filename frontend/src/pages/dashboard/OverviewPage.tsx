import { useOutletContext } from "react-router-dom"

import { SecurityFlow } from "@/components/dashboard/SecurityFlow"
import { TaskOverview } from "@/components/dashboard/TaskOverview"
import { SectionHeading } from "@/components/shared/SectionHeading"
import type { DashboardContextValue } from "@/pages/dashboard/DashboardLayout"


export function OverviewPage() {
  const {
    task,
    policy,
    capabilities,
    audit,
  } = useOutletContext<DashboardContextValue>()

  if (
    !task ||
    !policy ||
    !capabilities ||
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

  const successfulExecutions =
    currentPolicyEvents.filter(
      (event) =>
        event.decision === "ALLOW" &&
        event.executionStatus === "SUCCEEDED",
    ).length

  const deniedRequests =
    currentPolicyEvents.filter(
      (event) =>
        event.decision === "DENY",
    ).length

  const latestEvent =
    currentPolicyEvents[
      currentPolicyEvents.length - 1
    ]

  const latestDecision =
    latestEvent?.decision ??
    "ALLOW"

  const latestTool =
    latestEvent?.tool ??
    policy.grants[0]?.tool ??
    "ticket.get"

  const latestResource =
    latestEvent?.resource ??
    policy.grants[0]?.resource ??
    "—"

  return (
    <>
      <TaskOverview
        taskId={task.taskId}
        task={task.task}
        policyId={policy.policyId}
        grantedCount={capabilities.granted}
        totalCapabilities={capabilities.total}
        privilegeReduction={
          capabilities.privilegeReductionPercent
        }
        result="Live ToolFence runtime"
        resultDetail={
          `${successfulExecutions} successful executions · ` +
          `${deniedRequests} denied requests`
        }
      />

      <div className="mt-8">
        <SectionHeading
          eyebrow="Runtime state"
          title="Latest protected request"
          description="A live view of the most recent protected tool request recorded for the currently active ToolFence policy."
        />

        <div className="mt-5">
          <SecurityFlow
            decision={latestDecision}
            tool={latestTool}
            resource={latestResource}
          />
        </div>
      </div>

      <div
        className="
          mt-8
          grid gap-4
          sm:grid-cols-2
          xl:grid-cols-4
        "
      >
        <OverviewMetric
          label="Policy state"
          value={policy.status}
          detail="Current lifecycle state"
        />

        <OverviewMetric
          label="Granted"
          value={`${capabilities.granted}/${capabilities.total}`}
          detail="Protected capabilities"
        />

        <OverviewMetric
          label="Privilege reduction"
          value={`${capabilities.privilegeReductionPercent}%`}
          detail="Capabilities excluded"
        />

        <OverviewMetric
          label="Audit evidence"
          value={String(currentPolicyEvents.length)}
          detail="Events for this policy"
        />
      </div>
    </>
  )
}


function OverviewMetric({
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
