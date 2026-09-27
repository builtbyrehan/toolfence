import { useOutletContext } from "react-router-dom"

import { BenchmarkCards } from "@/components/dashboard/BenchmarkCards"
import { SectionHeading } from "@/components/shared/SectionHeading"
import type { DashboardContextValue } from "@/pages/dashboard/DashboardLayout"


export function BenchmarkPage() {
  const {
    benchmark,
  } = useOutletContext<DashboardContextValue>()

  if (!benchmark) {
    return null
  }

  return (
    <>
      <SectionHeading
        eyebrow="Security evaluation"
        title="Replay benchmark"
        description="Measured authorization behavior for the ToolFence golden task, including blocking accuracy, false denials, privilege reduction, and policy-evaluation latency."
      />

      <div className="mt-5">
        <BenchmarkCards
          matchedCases={
            benchmark.matchedCases
          }
          totalCases={
            benchmark.totalCases
          }
          forbiddenBlockRate={
            benchmark.forbiddenActionBlockingPercent
          }
          falseDenialRate={
            benchmark.falseDenialPercent
          }
          privilegeReduction={
            benchmark.privilegeReductionPercent
          }
          meanEvaluationMs={
            benchmark.meanPolicyEvaluationMs
          }
          maxEvaluationMs={
            benchmark.maxPolicyEvaluationMs
          }
        />
      </div>

      <div
        className="
          mt-8
          grid gap-4
          md:grid-cols-2
          xl:grid-cols-3
        "
      >
        <BenchmarkMetric
          label="Ground-truth match"
          value={`${benchmark.groundTruthMatchPercent}%`}
          detail={`${benchmark.matchedCases}/${benchmark.totalCases} benchmark cases matched expected behavior`}
        />

        <BenchmarkMetric
          label="Forbidden blocking"
          value={`${benchmark.forbiddenActionBlockingPercent}%`}
          detail="Forbidden protected actions were blocked"
        />

        <BenchmarkMetric
          label="Boundary accuracy"
          value={`${benchmark.boundaryAccuracyPercent}%`}
          detail="Resource-scope boundary cases evaluated correctly"
        />

        <BenchmarkMetric
          label="False denial rate"
          value={`${benchmark.falseDenialPercent}%`}
          detail="Legitimate benchmark actions incorrectly denied"
        />

        <BenchmarkMetric
          label="Mean evaluation"
          value={`${benchmark.meanPolicyEvaluationMs.toFixed(4)} ms`}
          detail="Authorization policy-evaluation time"
        />

        <BenchmarkMetric
          label="Maximum evaluation"
          value={`${benchmark.maxPolicyEvaluationMs.toFixed(4)} ms`}
          detail="Maximum authorization policy-evaluation time"
        />
      </div>

      {benchmark.groups &&
        benchmark.groups.length > 0 && (
          <div className="mt-8">
            <SectionHeading
              eyebrow="Case categories"
              title="Benchmark groups"
              description="Breakdown of correct benchmark results by test category."
            />

            <div
              className="
                mt-5
                grid gap-4
                sm:grid-cols-2
                xl:grid-cols-3
              "
            >
              {benchmark.groups.map(
                (group) => (
                  <BenchmarkMetric
                    key={group.label}
                    label={group.label}
                    value={`${group.correct}/${group.total}`}
                    detail="Cases evaluated correctly"
                  />
                ),
              )}
            </div>
          </div>
        )}

      <div
        className="
          mt-8
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
          Latency values represent ToolFence authorization policy-evaluation
          time only. They are not end-to-end IBM Bob, MCP, network, or backend
          execution latency.
        </p>
      </div>
    </>
  )
}


function BenchmarkMetric({
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
