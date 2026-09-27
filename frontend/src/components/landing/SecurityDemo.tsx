import { motion } from "motion/react"
import {
  Check,
  CircleSlash2,
  FileCode2,
  GitPullRequest,
  PlayCircle,
  ShieldAlert,
  Ticket,
  X,
} from "lucide-react"

const allowedActions = [
  {
    tool: "ticket.get",
    resource: "BUG-17",
    icon: Ticket,
    result: "Ticket read",
  },
  {
    tool: "repo.read",
    resource: "project/src/cart.py",
    icon: FileCode2,
    result: "Source inspected",
  },
  {
    tool: "repo.write",
    resource: "project/src/cart.py",
    icon: FileCode2,
    result: "Fix written",
  },
  {
    tool: "ci.run",
    resource: "feature/BUG-17",
    icon: PlayCircle,
    result: "CI PASSED",
  },
  {
    tool: "pull_request.create",
    resource: "feature/BUG-17",
    icon: GitPullRequest,
    result: "PR #1 opened",
  },
]

export function SecurityDemo() {
  return (
    <section
      id="security-demo"
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
            mx-auto
            max-w-3xl
            text-center
          "
        >
          <div
            className="
              mx-auto mb-5
              inline-flex items-center gap-2
              rounded-full
              border border-red-400/10
              bg-red-400/[0.04]
              px-3 py-1.5
            "
          >
            <ShieldAlert className="h-3.5 w-3.5 text-red-400" />

            <span
              className="
                tf-mono
                text-[10px]
                uppercase
                tracking-[0.18em]
                text-red-300
              "
            >
              Live enforcement demo
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
            Useful actions continue.
            <span className="block text-slate-500">
              Unnecessary actions stop at the fence.
            </span>
          </h2>

          <p
            className="
              mx-auto mt-6
              max-w-2xl
              text-base
              leading-7
              text-slate-400
            "
          >
            In the live IBM Bob demo, ToolFence allowed the protected
            actions required to fix BUG-17 while independently blocking
            an attempted secret read that was outside the task policy.
          </p>
        </motion.div>

        <div
          className="
            mt-14
            grid gap-5
            lg:grid-cols-[1.15fr_0.85fr]
          "
        >
          {/* Allowed workflow */}
          <motion.div
            initial={{
              opacity: 0,
              x: -18,
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
                    text-emerald-400
                  "
                >
                  Legitimate workflow
                </p>

                <h3
                  className="
                    mt-2
                    text-xl
                    font-medium
                    text-white
                  "
                >
                  BUG-17 execution path
                </h3>
              </div>

              <div
                className="
                  inline-flex items-center gap-2
                  rounded-full
                  border border-emerald-400/15
                  bg-emerald-400/[0.06]
                  px-2.5 py-1
                "
              >
                <span className="h-1.5 w-1.5 rounded-full bg-emerald-400" />

                <span
                  className="
                    tf-mono
                    text-[9px]
                    text-emerald-300
                  "
                >
                  ALLOWED
                </span>
              </div>
            </div>

            <div className="p-5 sm:p-6">
              <div className="space-y-3">
                {allowedActions.map(
                  (
                    {
                      tool,
                      resource,
                      icon: Icon,
                      result,
                    },
                    index,
                  ) => (
                    <motion.div
                      key={tool}
                      initial={{
                        opacity: 0,
                        y: 12,
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
                        duration: 0.4,
                        delay: index * 0.06,
                      }}
                      className="
                        grid gap-3
                        rounded-xl
                        border border-emerald-400/[0.08]
                        bg-emerald-400/[0.025]
                        p-4
                        sm:grid-cols-[36px_1fr_auto]
                        sm:items-center
                      "
                    >
                      <div
                        className="
                          flex h-9 w-9
                          items-center justify-center
                          rounded-lg
                          border border-emerald-400/10
                          bg-emerald-400/[0.05]
                        "
                      >
                        <Icon className="h-4 w-4 text-emerald-400" />
                      </div>

                      <div>
                        <div className="flex flex-wrap items-center gap-2">
                          <span
                            className="
                              tf-mono
                              text-[11px]
                              text-slate-200
                            "
                          >
                            {tool}
                          </span>

                          <span
                            className="
                              rounded
                              bg-emerald-400/[0.06]
                              px-1.5 py-0.5
                              tf-mono
                              text-[8px]
                              text-emerald-400
                            "
                          >
                            ALLOW
                          </span>
                        </div>

                        <p
                          className="
                            tf-mono
                            mt-1
                            text-[9px]
                            text-slate-600
                          "
                        >
                          {resource}
                        </p>
                      </div>

                      <div
                        className="
                          flex items-center gap-1.5
                          text-xs
                          text-slate-400
                        "
                      >
                        <Check className="h-3.5 w-3.5 text-emerald-400" />
                        {result}
                      </div>
                    </motion.div>
                  ),
                )}
              </div>
            </div>
          </motion.div>

          {/* Denied action */}
          <motion.div
            initial={{
              opacity: 0,
              x: 18,
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
              border border-red-400/15
              bg-[#0b1018]
              shadow-[0_0_70px_rgba(239,68,68,0.06)]
            "
          >
            <div
              className="
                pointer-events-none
                absolute inset-0
                bg-[radial-gradient(circle_at_50%_0%,rgba(239,68,68,0.08),transparent_45%)]
              "
            />

            <div
              className="
                relative
                border-b border-red-400/[0.08]
                px-5 py-4
                sm:px-6
              "
            >
              <p
                className="
                  tf-mono
                  text-[10px]
                  uppercase
                  tracking-[0.16em]
                  text-red-400
                "
              >
                Forbidden attempt
              </p>

              <h3
                className="
                  mt-2
                  text-xl
                  font-medium
                  text-white
                "
              >
                Secret access blocked
              </h3>
            </div>

            <div className="relative p-5 sm:p-6">
              <div
                className="
                  rounded-xl
                  border border-red-400/10
                  bg-red-400/[0.035]
                  p-4
                "
              >
                <div className="flex items-start gap-3">
                  <div
                    className="
                      flex h-10 w-10
                      shrink-0
                      items-center justify-center
                      rounded-xl
                      border border-red-400/10
                      bg-red-400/[0.06]
                    "
                  >
                    <CircleSlash2 className="h-5 w-5 text-red-400" />
                  </div>

                  <div>
                    <div className="flex flex-wrap items-center gap-2">
                      <span
                        className="
                          tf-mono
                          text-[12px]
                          text-slate-200
                        "
                      >
                        secret.read
                      </span>

                      <span
                        className="
                          inline-flex items-center gap-1
                          rounded
                          bg-red-400/[0.08]
                          px-1.5 py-0.5
                          tf-mono
                          text-[8px]
                          text-red-400
                        "
                      >
                        <X className="h-2.5 w-2.5" />
                        DENY
                      </span>
                    </div>

                    <p
                      className="
                        tf-mono
                        mt-2
                        text-[10px]
                        text-slate-500
                      "
                    >
                      production-key
                    </p>
                  </div>
                </div>
              </div>

              <div
                className="
                  mt-5
                  space-y-3
                "
              >
                <div
                  className="
                    flex items-center justify-between
                    border-b border-white/[0.05]
                    pb-3
                  "
                >
                  <span className="text-xs text-slate-500">
                    Decision
                  </span>

                  <span
                    className="
                      tf-mono
                      text-[10px]
                      text-red-400
                    "
                  >
                    DENY
                  </span>
                </div>

                <div
                  className="
                    flex items-center justify-between
                    border-b border-white/[0.05]
                    pb-3
                  "
                >
                  <span className="text-xs text-slate-500">
                    Reason
                  </span>

                  <span
                    className="
                      tf-mono
                      text-[10px]
                      text-slate-300
                    "
                  >
                    TOOL_NOT_GRANTED
                  </span>
                </div>

                <div
                  className="
                    flex items-center justify-between
                    border-b border-white/[0.05]
                    pb-3
                  "
                >
                  <span className="text-xs text-slate-500">
                    Execution
                  </span>

                  <span
                    className="
                      tf-mono
                      text-[10px]
                      text-red-400
                    "
                  >
                    NOT_EXECUTED
                  </span>
                </div>

                <div
                  className="
                    flex items-center justify-between
                  "
                >
                  <span className="text-xs text-slate-500">
                    Result
                  </span>

                  <span
                    className="
                      tf-mono
                      text-[10px]
                      text-slate-600
                    "
                  >
                    null
                  </span>
                </div>
              </div>

              <div
                className="
                  mt-6
                  rounded-xl
                  border border-red-400/[0.08]
                  bg-red-400/[0.025]
                  p-4
                "
              >
                <p
                  className="
                    text-xs
                    leading-5
                    text-slate-500
                  "
                >
                  The capability existed on the MCP server, but it was
                  outside the active BUG-17 policy. ToolFence stopped the
                  request before the secret backend executed.
                </p>
              </div>
            </div>
          </motion.div>
        </div>

        <motion.div
          initial={{
            opacity: 0,
            y: 12,
          }}
          whileInView={{
            opacity: 1,
            y: 0,
          }}
          viewport={{
            once: true,
          }}
          transition={{
            duration: 0.45,
            delay: 0.18,
          }}
          className="
            mt-6
            flex flex-col gap-3
            rounded-2xl
            border border-white/[0.06]
            bg-white/[0.015]
            p-5
            sm:flex-row
            sm:items-center
            sm:justify-between
          "
        >
          <p
            className="
              text-sm
              text-slate-400
            "
          >
            Tool visibility does not imply permission.
          </p>

          <p
            className="
              tf-mono
              text-[10px]
              uppercase
              tracking-[0.14em]
              text-blue-400
            "
          >
            every call crosses the policy boundary
          </p>
        </motion.div>
      </div>
    </section>
  )
}
