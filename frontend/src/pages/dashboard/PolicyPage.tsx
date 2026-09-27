import { useOutletContext } from "react-router-dom"

import { CapabilityMatrix } from "@/components/dashboard/CapabilityMatrix"
import { PolicyCard } from "@/components/dashboard/PolicyCard"
import { SecurityFlow } from "@/components/dashboard/SecurityFlow"
import { SectionHeading } from "@/components/shared/SectionHeading"
import type { DashboardContextValue } from "@/pages/dashboard/DashboardLayout"


export function PolicyPage() {
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

  const latestEvent =
    currentPolicyEvents[
      currentPolicyEvents.length - 1
    ]

  const flowDecision =
    latestEvent?.decision ??
    "ALLOW"

  const flowTool =
    latestEvent?.tool ??
    policy.grants[0]?.tool ??
    "ticket.get"

  const flowResource =
    latestEvent?.resource ??
    policy.grants[0]?.resource ??
    "—"

  return (
    <>
      <SectionHeading
        eyebrow="Policy enforcement"
        title="Current capability boundary"
        description="This page reflects the policy ToolFence actually activated for the current task. It does not expose or substitute the trusted developer approval ceiling."
      />

      <div
        className="
          mt-5
          grid gap-5
          xl:grid-cols-[0.72fr_1.28fr]
          xl:items-start
        "
      >
        <PolicyCard
          taskId={task.taskId}
          policyId={policy.policyId}
          status={policy.status}
          grantedCount={policy.grantedCount}
        />

        <CapabilityMatrix
          capabilities={
            capabilities.capabilities.map(
              (capability) => ({
                tool: capability.tool,
                granted: capability.granted,
                resource:
                  capability.resource ??
                  undefined,
              }),
            )
          }
        />
      </div>

      <div className="mt-8">
        <SectionHeading
          eyebrow="Request path"
          title="Deterministic execution flow"
          description="Bob proposes a protected action. ToolFence independently checks the trusted active policy before backend execution is allowed."
        />

        <div className="mt-5">
          <SecurityFlow
            decision={flowDecision}
            tool={flowTool}
            resource={flowResource}
          />
        </div>
      </div>

      <div
        className="
          mt-8
          grid gap-4
          md:grid-cols-3
        "
      >
        <PolicyMetric
          label="Granted capabilities"
          value={`${capabilities.granted}/${capabilities.total}`}
          detail="Available through the active policy"
        />

        <PolicyMetric
          label="Excluded capabilities"
          value={String(capabilities.excluded)}
          detail="Unavailable to this task"
        />

        <PolicyMetric
          label="Privilege reduction"
          value={`${capabilities.privilegeReductionPercent}%`}
          detail="Reduction from full tool inventory"
        />
      </div>
    </>
  )
}


function PolicyMetric({
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
