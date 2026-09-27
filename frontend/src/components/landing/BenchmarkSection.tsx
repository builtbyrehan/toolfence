import { motion } from "motion/react"
import {
  Activity,
  Ban,
  Gauge,
  ShieldCheck,
  TrendingDown,
} from "lucide-react"

const metrics = [
  {
    label: "Ground-truth match",
    value: "16 / 16",
    helper: "Every benchmark case matched its expected decision.",
    icon: ShieldCheck,
    accent: "blue",
  },
  {
    label: "Forbidden actions blocked",
    value: "100%",
    helper: "All seeded forbidden actions were denied correctly.",
    icon: Ban,
    accent: "green",
  },
  {
    label: "False denial rate",
    value: "0%",
    helper: "No legitimate benchmark action was incorrectly denied.",
    icon: Activity,
    accent: "green",
  },
  {
    label: "Privilege reduction",
    value: "45.45%",
    helper: "6 task capabilities granted from 11 available capabilities.",
    icon: TrendingDown,
    accent: "blue",
  },
]

const benchmarkGroups = [
  {
    label: "Legitimate",
    count: 7,
    result: "7 / 7 correct",
  },
  {
    label: "Forbidden",
    count: 4,
    result: "4 / 4 blocked",
  },
  {
    label: "Boundary",
    count: 5,
    result: "5 / 5 correct",
  },
]

export function BenchmarkSection() {
  return (
    <section
      id="benchmark"
      className="
        relative
        border-b border-white/[0.06]
        py-24 sm:py-28
      "
    >
      <div className="tf-container">
        <motion.div
          initial={{
            opacity: 0,
            y: 16,
          }}
          whileInView={{
            opacity: 1,
            y: 0,
          }}
          viewport={{
            once: true,
            amount: 0.35,
          }}
          transition={{
            duration: 0.5,
          }}
          className="
            grid gap-10
            lg:grid-cols-[0.85fr_1.15fr]
            lg:items-end
          "
        >
          <div>
            <div
              className="
                mb-5
                inline-flex items-center gap-2
                rounded-full
                border border-blue-400/15
                bg-blue-500/[0.06]
                px-3 py-1.5
              "
            >
              <Gauge className="h-3.5 w-3.5 text-blue-400" />

              <span
                className="
                  tf-mono
                  text-[10px]
                  uppercase
                  tracking-[0.18em]
                  text-blue-300
                "
              >
                Replay benchmark
              </span>
            </div>

            <h2
              className="
                text-4xl
                font-semibold
                leading-[1.05]
                tracking-[-0.035em]
                text-white
                sm:text-5xl
              "
            >
              Security claims backed
              <span className="block text-slate-500">
                by replayable evidence.
              </span>
            </h2>
          </div>

          <p
            className="
              max-w-2xl
              text-base
              leading-7
              text-slate-400
              lg:justify-self-end
            "
          >
            ToolFence replays predefined legitimate, forbidden, and
            resource-boundary scenarios against the compiled task policy.
            Results are measured from the real deterministic evaluator
            rather than hard-coded into the dashboard.
          </p>
        </motion.div>

        {/* Main metric cards */}
        <div
          className="
            mt-14
            grid gap-3
            sm:grid-cols-2
            xl:grid-cols-4
          "
        >
          {metrics.map(
            (
              {
                label,
                value,
                helper,
                icon: Icon,
                accent,
              },
              index,
            ) => {
              const green =
                accent === "green"

              return (
                <motion.article
                  key={label}
                  initial={{
                    opacity: 0,
                    y: 16,
                  }}
                  whileInView={{
                    opacity: 1,
                    y: 0,
                  }}
                  viewport={{
                    once: true,
                    amount: 0.3,
                  }}
                  transition={{
                    duration: 0.45,
                    delay: index * 0.06,
                  }}
                  className="
                    tf-panel
                    tf-panel-interactive
                    p-5
                  "
                >
                  <div
                    className="
                      flex items-start
                      justify-between
                      gap-4
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
                            ? "border-emerald-400/12 bg-emerald-400/[0.05]"
                            : "border-blue-400/12 bg-blue-400/[0.05]"
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
                      />
                    </div>

                    <span
                      className="
                        tf-mono
                        text-[9px]
                        uppercase
                        tracking-[0.12em]
                        text-slate-600
                      "
                    >
                      measured
                    </span>
                  </div>

                  <p
                    className={`
                      mt-7
                      text-4xl
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
                      mt-3
                      text-xs
                      leading-5
                      text-slate-600
                    "
                  >
                    {helper}
                  </p>
                </motion.article>
              )
            },
          )}
        </div>

        {/* Detailed benchmark panel */}
        <div
          className="
            mt-5
            grid gap-5
            lg:grid-cols-[1.2fr_0.8fr]
          "
        >
          <motion.div
            initial={{
              opacity: 0,
              x: -16,
            }}
            whileInView={{
              opacity: 1,
              x: 0,
            }}
            viewport={{
              once: true,
              amount: 0.25,
            }}
            transition={{
              duration: 0.5,
            }}
            className="tf-panel overflow-hidden"
          >
            <div
              className="
                flex items-center justify-between
                border-b border-white/[0.06]
                px-5 py-4
                sm:px-6
              "
            >
              <div>
                <p
                  className="
                    tf-mono
                    text-[10px]
                    uppercase
                    tracking-[0.16em]
                    text-blue-400
                  "
                >
                  Benchmark composition
                </p>

                <h3
                  className="
                    mt-2
                    text-xl
                    font-medium
                    text-white
                  "
                >
                  16 deterministic scenarios
                </h3>
              </div>

              <span
                className="
                  rounded-lg
                  border border-emerald-400/10
                  bg-emerald-400/[0.04]
                  px-2.5 py-1
                  tf-mono
                  text-[9px]
                  text-emerald-400
                "
              >
                100% MATCH
              </span>
            </div>

            <div className="p-5 sm:p-6">
              <div className="space-y-5">
                {benchmarkGroups.map(
                  ({
                    label,
                    count,
                    result,
                  }) => (
                    <div key={label}>
                      <div
                        className="
                          flex items-center
                          justify-between
                          gap-4
                        "
                      >
                        <div>
                          <p
                            className="
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
                              text-slate-600
                            "
                          >
                            {result}
                          </p>
                        </div>

                        <span
                          className="
                            tf-mono
                            text-xs
                            text-slate-400
                          "
                        >
                          {count}
                        </span>
                      </div>

                      <div
                        className="
                          mt-3
                          h-1.5
                          overflow-hidden
                          rounded-full
                          bg-white/[0.04]
                        "
                      >
                        <motion.div
                          initial={{
                            width: 0,
                          }}
                          whileInView={{
                            width: "100%",
                          }}
                          viewport={{
                            once: true,
                          }}
                          transition={{
                            duration: 0.8,
                            delay: 0.1,
                          }}
                          className="
                            h-full
                            rounded-full
                            bg-gradient-to-r
                            from-blue-500
                            to-emerald-400
                          "
                        />
                      </div>
                    </div>
                  ),
                )}
              </div>
            </div>
          </motion.div>

          {/* Timing */}
          <motion.div
            initial={{
              opacity: 0,
              x: 16,
            }}
            whileInView={{
              opacity: 1,
              x: 0,
            }}
            viewport={{
              once: true,
              amount: 0.25,
            }}
            transition={{
              duration: 0.5,
              delay: 0.08,
            }}
            className="
              relative
              overflow-hidden
              rounded-[18px]
              border border-blue-400/12
              bg-[#0a101a]
              p-6
            "
          >
            <div
              className="
                pointer-events-none
                absolute inset-0
                bg-[radial-gradient(circle_at_100%_0%,rgba(59,130,246,0.08),transparent_50%)]
              "
            />

            <div className="relative">
              <div
                className="
                  flex h-10 w-10
                  items-center justify-center
                  rounded-xl
                  border border-blue-400/15
                  bg-blue-500/[0.07]
                "
              >
                <Gauge className="h-4.5 w-4.5 text-blue-400" />
              </div>

              <p
                className="
                  tf-mono
                  mt-6
                  text-[10px]
                  uppercase
                  tracking-[0.16em]
                  text-blue-400
                "
              >
                Policy evaluator
              </p>

              <div className="mt-5">
                <p
                  className="
                    text-4xl
                    font-semibold
                    tracking-[-0.04em]
                    text-white
                  "
                >
                  0.0205
                  <span
                    className="
                      ml-2
                      text-lg
                      font-normal
                      text-slate-500
                    "
                  >
                    ms
                  </span>
                </p>

                <p
                  className="
                    mt-2
                    text-sm
                    text-slate-400
                  "
                >
                  Mean authorization evaluation
                </p>
              </div>

              <div
                className="
                  mt-6
                  border-t border-white/[0.06]
                  pt-5
                "
              >
                <div
                  className="
                    flex items-center
                    justify-between
                  "
                >
                  <span className="text-xs text-slate-500">
                    Max measured
                  </span>

                  <span
                    className="
                      tf-mono
                      text-xs
                      text-slate-300
                    "
                  >
                    0.0525 ms
                  </span>
                </div>
              </div>

              <p
                className="
                  mt-6
                  text-[11px]
                  leading-5
                  text-slate-600
                "
              >
                These numbers measure ToolFence authorization-policy
                evaluation only. They are not end-to-end IBM Bob or MCP
                request latency.
              </p>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  )
}
