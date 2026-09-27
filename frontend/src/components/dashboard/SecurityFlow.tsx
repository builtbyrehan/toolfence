import {
  Activity,
  ArrowRight,
  Bot,
  CheckCircle2,
  LockKeyhole,
  ServerCog,
  ShieldCheck,
} from "lucide-react"

type SecurityFlowProps = {
  decision?: "ALLOW" | "DENY"
  tool?: string
  resource?: string
}

export function SecurityFlow({
  decision = "ALLOW",
  tool = "repo.write",
  resource = "project/src/cart.py",
}: SecurityFlowProps) {
  const allowed = decision === "ALLOW"

  const steps = [
    {
      label: "IBM Bob",
      helper: "Proposes capability",
      icon: Bot,
      tone: "blue",
    },
    {
      label: "ToolFence Policy",
      helper: "Checks active contract",
      icon: LockKeyhole,
      tone: "blue",
    },
    {
      label: decision,
      helper: allowed
        ? "Authorization granted"
        : "Authorization blocked",
      icon: allowed
        ? CheckCircle2
        : ShieldCheck,
      tone: allowed
        ? "green"
        : "red",
    },
    {
      label: "Protected Backend",
      helper: allowed
        ? "Request executes"
        : "Request not executed",
      icon: ServerCog,
      tone: allowed
        ? "green"
        : "red",
    },
    {
      label: "Audit Trail",
      helper: "Decision recorded",
      icon: Activity,
      tone: "blue",
    },
  ]

  return (
    <section className="tf-panel overflow-hidden">
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
          <p
            className="
              tf-mono
              text-[10px]
              uppercase
              tracking-[0.16em]
              text-blue-400
            "
          >
            Security flow
          </p>

          <h2
            className="
              mt-2
              text-xl
              font-medium
              text-white
            "
          >
            Protected request path
          </h2>

          <p className="mt-1 text-xs text-slate-600">
            Every tool call crosses the same deterministic boundary.
          </p>
        </div>

        <div
          className="
            rounded-lg
            border border-white/[0.06]
            bg-white/[0.02]
            px-3 py-2
          "
        >
          <p
            className="
              tf-mono
              text-[9px]
              text-slate-300
            "
          >
            {tool}
          </p>

          <p
            className="
              tf-mono
              mt-1
              max-w-[220px]
              truncate
              text-[8px]
              text-slate-600
            "
          >
            {resource}
          </p>
        </div>
      </div>

      <div className="p-5 sm:p-6">
        <div
          className="
            grid gap-3
            xl:grid-cols-[1fr_auto_1fr_auto_1fr_auto_1fr_auto_1fr]
            xl:items-center
          "
        >
          {steps.map(
            (
              {
                label,
                helper,
                icon: Icon,
                tone,
              },
              index,
            ) => {
              const blue = tone === "blue"
              const green = tone === "green"


              return (
                <div
                  key={label}
                  className="contents"
                >
                  <div
                    className={`
                      rounded-xl
                      border
                      p-4
                      ${
                        blue
                          ? "border-blue-400/[0.08] bg-blue-400/[0.025]"
                          : green
                            ? "border-emerald-400/[0.08] bg-emerald-400/[0.025]"
                            : "border-red-400/[0.08] bg-red-400/[0.025]"
                      }
                    `}
                  >
                    <div
                      className={`
                        flex h-9 w-9
                        items-center justify-center
                        rounded-xl
                        border
                        ${
                          blue
                            ? "border-blue-400/10 bg-blue-400/[0.04]"
                            : green
                              ? "border-emerald-400/10 bg-emerald-400/[0.04]"
                              : "border-red-400/10 bg-red-400/[0.04]"
                        }
                      `}
                    >
                      <Icon
                        className={`
                          h-4 w-4
                          ${
                            blue
                              ? "text-blue-400"
                              : green
                                ? "text-emerald-400"
                                : "text-red-400"
                          }
                        `}
                        strokeWidth={1.8}
                      />
                    </div>

                    <p
                      className="
                        mt-4
                        text-sm
                        font-medium
                        text-slate-200
                      "
                    >
                      {label}
                    </p>

                    <p
                      className="
                        mt-1
                        text-xs
                        leading-5
                        text-slate-600
                      "
                    >
                      {helper}
                    </p>
                  </div>

                  {index < steps.length - 1 && (
                    <div
                      className="
                        hidden
                        items-center justify-center
                        xl:flex
                      "
                    >
                      <ArrowRight
                        className="
                          h-4 w-4
                          text-slate-700
                        "
                      />
                    </div>
                  )}
                </div>
              )
            },
          )}
        </div>

        <div
          className="
            mt-5
            grid gap-3
            md:grid-cols-3
          "
        >
          <div
            className="
              rounded-xl
              border border-white/[0.05]
              bg-white/[0.015]
              p-4
            "
          >
            <p
              className="
                tf-mono
                text-[9px]
                uppercase
                tracking-[0.14em]
                text-slate-700
              "
            >
              Proposed action
            </p>

            <p
              className="
                tf-mono
                mt-2
                text-[10px]
                text-slate-300
              "
            >
              {tool}
            </p>
          </div>

          <div
            className="
              rounded-xl
              border border-white/[0.05]
              bg-white/[0.015]
              p-4
            "
          >
            <p
              className="
                tf-mono
                text-[9px]
                uppercase
                tracking-[0.14em]
                text-slate-700
              "
            >
              Resource
            </p>

            <p
              className="
                tf-mono
                mt-2
                break-all
                text-[10px]
                text-slate-300
              "
            >
              {resource}
            </p>
          </div>

          <div
            className="
              rounded-xl
              border border-white/[0.05]
              bg-white/[0.015]
              p-4
            "
          >
            <p
              className="
                tf-mono
                text-[9px]
                uppercase
                tracking-[0.14em]
                text-slate-700
              "
            >
              Final decision
            </p>

            <p
              className={`
                tf-mono
                mt-2
                text-[10px]
                ${
                  allowed
                    ? "text-emerald-400"
                    : "text-red-400"
                }
              `}
            >
              {decision}
            </p>
          </div>
        </div>
      </div>
    </section>
  )
}
