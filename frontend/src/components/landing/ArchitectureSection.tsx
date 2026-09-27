import { motion } from "motion/react"
import {
  Activity,
  Bot,
  Boxes,
  Braces,
  CheckCircle2,
  Database,
  GitBranch,
  LockKeyhole,
  ServerCog,
  ShieldCheck,
  Ticket,
} from "lucide-react"

const controlPlane = [
  {
    icon: Braces,
    label: "Task Context",
  },
  {
    icon: LockKeyhole,
    label: "Approval Ceiling",
  },
  {
    icon: ShieldCheck,
    label: "Policy Compiler",
  },
]

const services = [
  {
    icon: Ticket,
    label: "Tickets",
  },
  {
    icon: GitBranch,
    label: "Repository",
  },
  {
    icon: Activity,
    label: "CI",
  },
  {
    icon: CheckCircle2,
    label: "Pull Requests",
  },
  {
    icon: ServerCog,
    label: "Release",
  },
  {
    icon: Database,
    label: "Secrets",
  },
]

export function ArchitectureSection() {
  return (
    <section
      id="architecture"
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
          <p
            className="
              tf-mono
              text-[10px]
              uppercase
              tracking-[0.18em]
              text-blue-400
            "
          >
            Architecture
          </p>

          <h2
            className="
              mt-4
              text-4xl
              font-semibold
              leading-[1.05]
              tracking-[-0.035em]
              text-white
              sm:text-5xl
            "
          >
            One policy boundary
            <span className="block text-slate-500">
              between the agent and every protected tool.
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
            ToolFence keeps semantic reasoning inside IBM Bob while
            deterministic authorization, execution control, and auditing
            remain inside the gateway.
          </p>
        </motion.div>

        <div
          className="
            mt-16
            grid gap-5
            lg:grid-cols-[0.8fr_1.2fr_0.9fr]
            lg:items-stretch
          "
        >
          {/* IBM Bob */}
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
              amount: 0.3,
            }}
            transition={{
              duration: 0.5,
            }}
            className="
              tf-panel
              flex flex-col
              justify-between
              p-6
            "
          >
            <div>
              <div
                className="
                  flex h-11 w-11
                  items-center justify-center
                  rounded-xl
                  border border-blue-400/15
                  bg-blue-500/[0.07]
                "
              >
                <Bot className="h-5 w-5 text-blue-400" />
              </div>

              <p
                className="
                  tf-mono
                  mt-5
                  text-[10px]
                  uppercase
                  tracking-[0.16em]
                  text-blue-400
                "
              >
                Agent
              </p>

              <h3
                className="
                  mt-2
                  text-2xl
                  font-medium
                  tracking-tight
                  text-white
                "
              >
                IBM Bob
              </h3>

              <p
                className="
                  mt-3
                  text-sm
                  leading-6
                  text-slate-500
                "
              >
                Understands the developer task, reasons about what actions
                are required, and proposes the minimum capability contract.
              </p>
            </div>

            <div
              className="
                mt-8
                rounded-xl
                border border-white/[0.06]
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
                  text-slate-600
                "
              >
                Responsibility
              </p>

              <p
                className="
                  mt-2
                  text-xs
                  leading-5
                  text-slate-400
                "
              >
                Reason about the task.
              </p>
            </div>
          </motion.div>

          {/* ToolFence */}
          <motion.div
            initial={{
              opacity: 0,
              y: 18,
            }}
            whileInView={{
              opacity: 1,
              y: 0,
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
              rounded-[20px]
              border border-blue-400/15
              bg-[#0a101a]
              shadow-[0_0_80px_rgba(59,130,246,0.06)]
            "
          >
            <div
              className="
                pointer-events-none
                absolute inset-0
                bg-[radial-gradient(circle_at_50%_0%,rgba(59,130,246,0.08),transparent_42%)]
              "
            />

            <div
              className="
                relative
                border-b border-white/[0.06]
                px-6 py-5
              "
            >
              <div className="flex items-center justify-between">
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
                    Security boundary
                  </p>

                  <h3
                    className="
                      mt-2
                      text-2xl
                      font-medium
                      tracking-tight
                      text-white
                    "
                  >
                    ToolFence
                  </h3>
                </div>

                <div
                  className="
                    flex h-11 w-11
                    items-center justify-center
                    rounded-xl
                    border border-blue-400/20
                    bg-blue-500/10
                  "
                >
                  <ShieldCheck className="h-5 w-5 text-blue-400" />
                </div>
              </div>
            </div>

            <div className="relative p-6">
              <p
                className="
                  tf-mono
                  text-[9px]
                  uppercase
                  tracking-[0.14em]
                  text-slate-600
                "
              >
                Control plane
              </p>

              <div className="mt-3 grid gap-2 sm:grid-cols-3">
                {controlPlane.map(
                  ({
                    icon: Icon,
                    label,
                  }) => (
                    <div
                      key={label}
                      className="
                        rounded-xl
                        border border-white/[0.06]
                        bg-white/[0.02]
                        p-3
                      "
                    >
                      <Icon className="h-4 w-4 text-blue-400" />

                      <p
                        className="
                          mt-3
                          text-xs
                          font-medium
                          text-slate-300
                        "
                      >
                        {label}
                      </p>
                    </div>
                  ),
                )}
              </div>

              <div
                className="
                  my-5
                  h-px
                  bg-gradient-to-r
                  from-transparent
                  via-blue-400/20
                  to-transparent
                "
              />

              <p
                className="
                  tf-mono
                  text-[9px]
                  uppercase
                  tracking-[0.14em]
                  text-slate-600
                "
              >
                Data plane
              </p>

              <div className="mt-3 grid gap-2 sm:grid-cols-2">
                <div
                  className="
                    rounded-xl
                    border border-emerald-400/[0.08]
                    bg-emerald-400/[0.025]
                    p-4
                  "
                >
                  <CheckCircle2 className="h-4 w-4 text-emerald-400" />

                  <p
                    className="
                      mt-3
                      text-sm
                      font-medium
                      text-slate-200
                    "
                  >
                    Deterministic Gateway
                  </p>

                  <p
                    className="
                      mt-2
                      text-xs
                      leading-5
                      text-slate-500
                    "
                  >
                    Validates arguments, derives resource identity, and
                    evaluates ALLOW / DENY before backend execution.
                  </p>
                </div>

                <div
                  className="
                    rounded-xl
                    border border-white/[0.06]
                    bg-white/[0.02]
                    p-4
                  "
                >
                  <Activity className="h-4 w-4 text-blue-400" />

                  <p
                    className="
                      mt-3
                      text-sm
                      font-medium
                      text-slate-200
                    "
                  >
                    Audit Trail
                  </p>

                  <p
                    className="
                      mt-2
                      text-xs
                      leading-5
                      text-slate-500
                    "
                  >
                    Records decision, resource, policy identity, execution
                    status, and reason for every protected request.
                  </p>
                </div>
              </div>
            </div>
          </motion.div>

          {/* Protected services */}
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
              amount: 0.3,
            }}
            transition={{
              duration: 0.5,
              delay: 0.12,
            }}
            className="tf-panel p-6"
          >
            <div className="flex items-center gap-3">
              <div
                className="
                  flex h-10 w-10
                  items-center justify-center
                  rounded-xl
                  border border-white/[0.07]
                  bg-white/[0.025]
                "
              >
                <Boxes className="h-4.5 w-4.5 text-slate-400" />
              </div>

              <div>
                <p
                  className="
                    tf-mono
                    text-[9px]
                    uppercase
                    tracking-[0.14em]
                    text-slate-600
                  "
                >
                  MCP services
                </p>

                <h3
                  className="
                    mt-1
                    text-xl
                    font-medium
                    text-white
                  "
                >
                  Protected tools
                </h3>
              </div>
            </div>

            <div className="mt-6 space-y-2">
              {services.map(
                ({
                  icon: Icon,
                  label,
                }) => (
                  <div
                    key={label}
                    className="
                      flex items-center gap-3
                      rounded-xl
                      border border-white/[0.05]
                      bg-white/[0.015]
                      px-3 py-3
                    "
                  >
                    <Icon className="h-4 w-4 text-slate-500" />

                    <span
                      className="
                        text-sm
                        text-slate-400
                      "
                    >
                      {label}
                    </span>
                  </div>
                ),
              )}
            </div>

            <div
              className="
                mt-6
                rounded-xl
                border border-emerald-400/[0.08]
                bg-emerald-400/[0.025]
                p-4
              "
            >
              <p
                className="
                  tf-mono
                  text-[9px]
                  uppercase
                  tracking-[0.14em]
                  text-emerald-400
                "
              >
                Execution rule
              </p>

              <p
                className="
                  mt-2
                  text-xs
                  leading-5
                  text-slate-500
                "
              >
                A protected backend receives the request only after
                ToolFence returns ALLOW.
              </p>
            </div>
          </motion.div>
        </div>

        <motion.div
          initial={{
            opacity: 0,
            y: 14,
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
            delay: 0.15,
          }}
          className="
            mt-6
            grid gap-px
            overflow-hidden
            rounded-2xl
            border border-white/[0.06]
            bg-white/[0.06]
            md:grid-cols-3
          "
        >
          <div className="bg-[#080d16] p-5">
            <p
              className="
                tf-mono
                text-[9px]
                uppercase
                tracking-[0.14em]
                text-blue-400
              "
            >
              01 · Proposal
            </p>

            <p className="mt-2 text-sm text-slate-400">
              Bob proposes the minimum task-specific permissions.
            </p>
          </div>

          <div className="bg-[#080d16] p-5">
            <p
              className="
                tf-mono
                text-[9px]
                uppercase
                tracking-[0.14em]
                text-blue-400
              "
            >
              02 · Enforcement
            </p>

            <p className="mt-2 text-sm text-slate-400">
              ToolFence evaluates every protected tool call.
            </p>
          </div>

          <div className="bg-[#080d16] p-5">
            <p
              className="
                tf-mono
                text-[9px]
                uppercase
                tracking-[0.14em]
                text-emerald-400
              "
            >
              03 · Evidence
            </p>

            <p className="mt-2 text-sm text-slate-400">
              Decisions and execution outcomes are recorded for audit.
            </p>
          </div>
        </motion.div>
      </div>
    </section>
  )
}
