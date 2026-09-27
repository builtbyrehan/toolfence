import {
  Activity,
  Ban,
  Gauge,
  ShieldCheck,
  TrendingDown,
} from "lucide-react"

type BenchmarkCardsProps = {
  matchedCases: number
  totalCases: number
  forbiddenBlockRate: number
  falseDenialRate: number
  privilegeReduction: number
  meanEvaluationMs: number
  maxEvaluationMs?: number
}

export function BenchmarkCards({
  matchedCases,
  totalCases,
  forbiddenBlockRate,
  falseDenialRate,
  privilegeReduction,
  meanEvaluationMs,
  maxEvaluationMs,
}: BenchmarkCardsProps) {
  const cards = [
    {
      label: "Ground-truth match",
      value: `${matchedCases} / ${totalCases}`,
      helper: "benchmark cases",
      icon: ShieldCheck,
      tone: "blue",
    },
    {
      label: "Forbidden blocked",
      value: `${forbiddenBlockRate.toFixed(0)}%`,
      helper: "forbidden actions",
      icon: Ban,
      tone: "green",
    },
    {
      label: "False denial rate",
      value: `${falseDenialRate.toFixed(0)}%`,
      helper: "legitimate actions",
      icon: Activity,
      tone: "green",
    },
    {
      label: "Privilege reduction",
      value: `${privilegeReduction.toFixed(2)}%`,
      helper: "capability surface",
      icon: TrendingDown,
      tone: "blue",
    },
  ]

  return (
    <section
      id="benchmark"
      className="tf-panel overflow-hidden"
    >
      <div
        className="
          flex flex-col gap-4
          border-b border-white/[0.06]
          px-5 py-4
          sm:flex-row
          sm:items-center
          sm:justify-between
          sm:px-6
        "
      >
        <div>
          <div className="flex items-center gap-2">
            <Gauge className="h-4 w-4 text-blue-400" />

            <p
              className="
                tf-mono
                text-[10px]
                uppercase
                tracking-[0.16em]
                text-blue-400
              "
            >
              Replay benchmark
            </p>
          </div>

          <h2
            className="
              mt-2
              text-xl
              font-medium
              text-white
            "
          >
            Security evaluation
          </h2>

          <p className="mt-1 text-xs text-slate-600">
            Deterministic replay results from the policy evaluator.
          </p>
        </div>

        <span
          className="
            w-fit
            rounded-lg
            border border-emerald-400/10
            bg-emerald-400/[0.04]
            px-2.5 py-1.5
            tf-mono
            text-[9px]
            text-emerald-400
          "
        >
          {matchedCases === totalCases
            ? "ALL CASES MATCHED"
            : `${matchedCases}/${totalCases} MATCHED`}
        </span>
      </div>

      <div className="p-5 sm:p-6">
        <div
          className="
            grid gap-3
            sm:grid-cols-2
            xl:grid-cols-4
          "
        >
          {cards.map(
            ({
              label,
              value,
              helper,
              icon: Icon,
              tone,
            }) => {
              const green =
                tone === "green"

              return (
                <article
                  key={label}
                  className="
                    rounded-xl
                    border border-white/[0.06]
                    bg-white/[0.015]
                    p-4
                  "
                >
                  <div
                    className={`
                      flex h-9 w-9
                      items-center justify-center
                      rounded-xl
                      border
                      ${
                        green
                          ? "border-emerald-400/10 bg-emerald-400/[0.04]"
                          : "border-blue-400/10 bg-blue-400/[0.04]"
                      }
                    `}
                  >
                    <Icon
                      className={`
                        h-4 w-4
                        ${
                          green
                            ? "text-emerald-400"
                            : "text-blue-400"
                        }
                      `}
                      strokeWidth={1.8}
                    />
                  </div>

                  <p
                    className={`
                      mt-5
                      text-3xl
                      font-semibold
                      tracking-[-0.04em]
                      ${
                        green
                          ? "text-emerald-400"
                          : "text-white"
                      }
                    `}
                  >
                    {value}
                  </p>

                  <p
                    className="
                      mt-2
                      text-sm
                      font-medium
                      text-slate-300
                    "
                  >
                    {label}
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
                </article>
              )
            },
          )}
        </div>

        <div
          className="
            mt-4
            grid gap-3
            md:grid-cols-2
          "
        >
          <div
            className="
              rounded-xl
              border border-blue-400/[0.08]
              bg-blue-400/[0.025]
              p-5
            "
          >
            <p
              className="
                tf-mono
                text-[9px]
                uppercase
                tracking-[0.14em]
                text-blue-400
              "
            >
              Mean policy evaluation
            </p>

            <div className="mt-3 flex items-baseline gap-2">
              <span
                className="
                  text-3xl
                  font-semibold
                  tracking-[-0.04em]
                  text-white
                "
              >
                {meanEvaluationMs.toFixed(4)}
              </span>

              <span className="text-sm text-slate-500">
                ms
              </span>
            </div>

            <p
              className="
                mt-3
                text-xs
                leading-5
                text-slate-600
              "
            >
              Authorization policy-evaluation time only.
            </p>
          </div>

          <div
            className="
              rounded-xl
              border border-white/[0.06]
              bg-white/[0.015]
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
              Measurement scope
            </p>

            {maxEvaluationMs !== undefined && (
              <div
                className="
                  mt-3
                  flex items-center justify-between
                "
              >
                <span className="text-xs text-slate-500">
                  Max evaluation
                </span>

                <span
                  className="
                    tf-mono
                    text-xs
                    text-slate-300
                  "
                >
                  {maxEvaluationMs.toFixed(4)} ms
                </span>
              </div>
            )}

            <p
              className="
                mt-4
                text-xs
                leading-5
                text-slate-600
              "
            >
              These timings do not represent end-to-end IBM Bob,
              MCP transport, or backend execution latency.
            </p>
          </div>
        </div>
      </div>
    </section>
  )
}
