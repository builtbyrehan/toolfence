import { motion } from "motion/react"
import {
  Activity,
  BadgeCheck,
  Bot,
  FileLock2,
  ScanSearch,
} from "lucide-react"

const steps = [
  {
    number: "01",
    icon: FileLock2,
    title: "Read trusted task context",
    description:
      "Bob retrieves the canonical task ID and task text without seeing the developer-approved permission ceiling.",
    accent: "blue",
  },
  {
    number: "02",
    icon: Bot,
    title: "Reason about minimum authority",
    description:
      "The agent inspects the capability inventory and determines the smallest set of tools and resource scopes required.",
    accent: "blue",
  },
  {
    number: "03",
    icon: ScanSearch,
    title: "Validate the proposal",
    description:
      "ToolFence compares the proposed task capability contract against the separately trusted developer approval limit.",
    accent: "blue",
  },
  {
    number: "04",
    icon: BadgeCheck,
    title: "Enforce every call",
    description:
      "Each protected action is deterministically evaluated against the active task policy before backend execution.",
    accent: "green",
  },
  {
    number: "05",
    icon: Activity,
    title: "Record the decision",
    description:
      "ALLOW and DENY outcomes, resources, reasons, policy IDs, and execution status are written to the audit trail.",
    accent: "green",
  },
]

export function HowItWorks() {
  return (
    <section
      id="how-it-works"
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
          className="max-w-3xl"
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
            How ToolFence works
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
            Semantic reasoning in.
            <span className="block text-slate-500">
              Deterministic security out.
            </span>
          </h2>

          <p
            className="
              mt-6
              max-w-2xl
              text-base
              leading-7
              text-slate-400
            "
          >
            ToolFence does not ask the language model to enforce its own
            permissions. Bob reasons about the task; the gateway independently
            validates and enforces the resulting capability boundary.
          </p>
        </motion.div>

        <div className="relative mt-16">
          <div
            className="
              absolute
              left-[23px]
              top-6
              hidden
              h-[calc(100%-48px)]
              w-px
              bg-gradient-to-b
              from-blue-400/30
              via-blue-400/10
              to-emerald-400/20
              sm:block
            "
          />

          <div className="space-y-4">
            {steps.map(
              (
                {
                  number,
                  icon: Icon,
                  title,
                  description,
                  accent,
                },
                index,
              ) => {
                const isGreen =
                  accent === "green"

                return (
                  <motion.article
                    key={number}
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
                      duration: 0.45,
                      delay: index * 0.07,
                    }}
                    className="
                      relative
                      grid gap-4
                      sm:grid-cols-[48px_1fr]
                    "
                  >
                    <div
                      className={`
                        relative z-10
                        flex h-12 w-12
                        items-center justify-center
                        rounded-xl
                        border
                        ${
                          isGreen
                            ? "border-emerald-400/15 bg-emerald-400/[0.06]"
                            : "border-blue-400/15 bg-blue-400/[0.06]"
                        }
                      `}
                    >
                      <Icon
                        className={`
                          h-5 w-5
                          ${
                            isGreen
                              ? "text-emerald-400"
                              : "text-blue-400"
                          }
                        `}
                        strokeWidth={1.7}
                      />
                    </div>

                    <div
                      className="
                        tf-panel
                        tf-panel-interactive
                        p-5 sm:p-6
                      "
                    >
                      <div
                        className="
                          flex flex-col gap-4
                          md:flex-row
                          md:items-start
                          md:justify-between
                        "
                      >
                        <div>
                          <div
                            className="
                              flex items-center gap-3
                            "
                          >
                            <span
                              className="
                                tf-mono
                                text-[10px]
                                tracking-[0.16em]
                                text-slate-600
                              "
                            >
                              {number}
                            </span>

                            <h3
                              className="
                                text-base
                                font-medium
                                text-slate-100
                              "
                            >
                              {title}
                            </h3>
                          </div>

                          <p
                            className="
                              mt-3
                              max-w-3xl
                              text-sm
                              leading-6
                              text-slate-500
                            "
                          >
                            {description}
                          </p>
                        </div>

                        <span
                          className={`
                            tf-mono
                            shrink-0
                            rounded-lg
                            border
                            px-2.5 py-1
                            text-[9px]
                            uppercase
                            tracking-[0.12em]
                            ${
                              isGreen
                                ? "border-emerald-400/10 bg-emerald-400/[0.04] text-emerald-400"
                                : "border-blue-400/10 bg-blue-400/[0.04] text-blue-400"
                            }
                          `}
                        >
                          {index < 2
                            ? "Agent reasoning"
                            : index === 2
                              ? "Trust boundary"
                              : index === 3
                                ? "Enforcement"
                                : "Audit"}
                        </span>
                      </div>
                    </div>
                  </motion.article>
                )
              },
            )}
          </div>
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
            delay: 0.2,
          }}
          className="
            mt-14
            grid gap-px
            overflow-hidden
            rounded-2xl
            border border-white/[0.06]
            bg-white/[0.06]
            sm:grid-cols-3
          "
        >
          <div className="bg-[#080d16] p-6">
            <p
              className="
                tf-mono
                text-[10px]
                uppercase
                tracking-[0.15em]
                text-slate-600
              "
            >
              Bob decides
            </p>

            <p
              className="
                mt-2
                text-sm
                text-slate-300
              "
            >
              What capabilities appear necessary for the task.
            </p>
          </div>

          <div className="bg-[#080d16] p-6">
            <p
              className="
                tf-mono
                text-[10px]
                uppercase
                tracking-[0.15em]
                text-blue-400
              "
            >
              ToolFence decides
            </p>

            <p
              className="
                mt-2
                text-sm
                text-slate-300
              "
            >
              Whether the proposed and requested actions are authorized.
            </p>
          </div>

          <div className="bg-[#080d16] p-6">
            <p
              className="
                tf-mono
                text-[10px]
                uppercase
                tracking-[0.15em]
                text-emerald-400
              "
            >
              Backend executes
            </p>

            <p
              className="
                mt-2
                text-sm
                text-slate-300
              "
            >
              Only after the deterministic policy decision returns ALLOW.
            </p>
          </div>
        </motion.div>
      </div>
    </section>
  )
}
