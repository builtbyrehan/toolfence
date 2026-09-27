import {
  CheckCircle2,
  Fingerprint,
  GitPullRequest,
  ShieldCheck,
  TrendingDown,
} from "lucide-react"

type TaskOverviewProps = {
  taskId: string
  task: string
  policyId: string
  grantedCount: number
  totalCapabilities: number
  privilegeReduction: number
  result?: string
  resultDetail?: string
}

export function TaskOverview({
  taskId,
  task,
  policyId,
  grantedCount,
  totalCapabilities,
  privilegeReduction,
  result = "BUG-17 fixed",
  resultDetail = "CI passed · PR #1 opened",
}: TaskOverviewProps) {
  return (
    <section
      id="overview"
      className="
        grid gap-5
        xl:grid-cols-[1.35fr_0.65fr]
      "
    >
      <div
        className="
          tf-panel
          overflow-hidden
        "
      >
        <div
          className="
            border-b border-white/[0.06]
            px-5 py-5
            sm:px-6
          "
        >
          <div
            className="
              flex flex-col gap-4
              sm:flex-row
              sm:items-start
              sm:justify-between
            "
          >
            <div>
              <div
                className="
                  inline-flex items-center gap-2
                  rounded-full
                  border border-blue-400/12
                  bg-blue-500/[0.05]
                  px-2.5 py-1
                "
              >
                <ShieldCheck className="h-3 w-3 text-blue-400" />

                <span
                  className="
                    tf-mono
                    text-[9px]
                    uppercase
                    tracking-[0.14em]
                    text-blue-300
                  "
                >
                  Active task
                </span>
              </div>

              <h1
                className="
                  mt-4
                  text-3xl
                  font-semibold
                  tracking-[-0.035em]
                  text-white
                  sm:text-4xl
                "
              >
                {taskId}
              </h1>

              <p
                className="
                  mt-3
                  max-w-2xl
                  text-sm
                  leading-6
                  text-slate-500
                "
              >
                {task}
              </p>
            </div>

            <div
              className="
                inline-flex
                shrink-0
                items-center gap-2
                rounded-full
                border border-emerald-400/12
                bg-emerald-400/[0.05]
                px-3 py-1.5
              "
            >
              <span
                className="
                  h-1.5 w-1.5
                  rounded-full
                  bg-emerald-400
                  shadow-[0_0_8px_rgba(74,222,128,0.7)]
                "
              />

              <span
                className="
                  tf-mono
                  text-[9px]
                  uppercase
                  tracking-[0.12em]
                  text-emerald-300
                "
              >
                Protected
              </span>
            </div>
          </div>
        </div>

        <div
          className="
            grid gap-px
            bg-white/[0.05]
            sm:grid-cols-3
          "
        >
          <Metric
            icon={ShieldCheck}
            label="Granted"
            value={`${grantedCount} / ${totalCapabilities}`}
            helper="capabilities"
          />

          <Metric
            icon={TrendingDown}
            label="Privilege reduction"
            value={`${privilegeReduction.toFixed(2)}%`}
            helper="active surface"
          />

          <Metric
            icon={Fingerprint}
            label="Policy identity"
            value={`${policyId.slice(0, 10)}...`}
            helper="compiled hash"
            mono
          />
        </div>
      </div>

      <div
        className="
          relative
          overflow-hidden
          rounded-[18px]
          border border-emerald-400/10
          bg-emerald-400/[0.025]
          p-5
          sm:p-6
        "
      >
        <div
          className="
            pointer-events-none
            absolute inset-0
            bg-[radial-gradient(circle_at_100%_0%,rgba(34,197,94,0.08),transparent_50%)]
          "
        />

        <div className="relative">
          <div
            className="
              flex h-10 w-10
              items-center justify-center
              rounded-xl
              border border-emerald-400/12
              bg-emerald-400/[0.05]
            "
          >
            <CheckCircle2 className="h-4.5 w-4.5 text-emerald-400" />
          </div>

          <p
            className="
              tf-mono
              mt-5
              text-[9px]
              uppercase
              tracking-[0.15em]
              text-emerald-400
            "
          >
            Current result
          </p>

          <h2
            className="
              mt-3
              text-2xl
              font-medium
              tracking-tight
              text-white
            "
          >
            {result}
          </h2>

          <div
            className="
              mt-3
              flex items-center gap-2
              text-sm
              text-slate-500
            "
          >
            <GitPullRequest className="h-4 w-4 text-slate-600" />

            <span>{resultDetail}</span>
          </div>

          <div
            className="
              mt-6
              border-t border-emerald-400/[0.08]
              pt-5
            "
          >
            <p
              className="
                text-xs
                leading-5
                text-slate-600
              "
            >
              ToolFence authorized the required workflow while keeping
              non-task capabilities outside the active execution boundary.
            </p>
          </div>
        </div>
      </div>
    </section>
  )
}

type MetricProps = {
  icon: typeof ShieldCheck
  label: string
  value: string
  helper: string
  mono?: boolean
}

function Metric({
  icon: Icon,
  label,
  value,
  helper,
  mono = false,
}: MetricProps) {
  return (
    <div className="bg-[#0d1420] p-5">
      <div className="flex items-center gap-2">
        <Icon
          className="h-3.5 w-3.5 text-slate-600"
          strokeWidth={1.8}
        />

        <p
          className="
            text-xs
            text-slate-600
          "
        >
          {label}
        </p>
      </div>

      <p
        className={`
          mt-3
          text-2xl
          font-semibold
          tracking-[-0.03em]
          text-white
          ${mono ? "tf-mono text-xl" : ""}
        `}
      >
        {value}
      </p>

      <p
        className="
          tf-mono
          mt-1
          text-[9px]
          uppercase
          tracking-[0.12em]
          text-slate-700
        "
      >
        {helper}
      </p>
    </div>
  )
}
