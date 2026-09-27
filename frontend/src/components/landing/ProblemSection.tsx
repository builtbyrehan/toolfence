import { motion } from "motion/react"
import {
  Bot,
  KeyRound,
  ShieldAlert,
  Waypoints,
} from "lucide-react"

const problems = [
  {
    icon: KeyRound,
    title: "Too much authority",
    description:
      "An agent may need one repository file and one CI branch, while still having access to unrelated tickets, deployments, and secrets.",
  },
  {
    icon: Waypoints,
    title: "Task intent is not enforcement",
    description:
      "Prompt instructions can tell an agent what it should use, but they do not create a deterministic security boundary around tool execution.",
  },
  {
    icon: ShieldAlert,
    title: "Sensitive tools stay reachable",
    description:
      "A capable agent can see powerful actions such as secret access or deployment even when the current task has no legitimate reason to use them.",
  },
]

export function ProblemSection() {
  return (
    <section
      id="problem"
      className="
        relative
        border-b border-white/[0.06]
        py-24 sm:py-28
      "
    >
      <div className="tf-container">
        <div
          className="
            grid gap-12
            lg:grid-cols-[0.85fr_1.15fr]
            lg:items-start
          "
        >
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
              amount: 0.35,
            }}
            transition={{
              duration: 0.5,
            }}
          >
            <div
              className="
                mb-5
                inline-flex items-center gap-2
                rounded-full
                border border-red-400/10
                bg-red-400/[0.04]
                px-3 py-1.5
              "
            >
              <Bot className="h-3.5 w-3.5 text-red-400" />

              <span
                className="
                  tf-mono
                  text-[10px]
                  uppercase
                  tracking-[0.18em]
                  text-red-300
                "
              >
                The problem
              </span>
            </div>

            <h2
              className="
                max-w-xl
                text-4xl
                font-semibold
                leading-[1.05]
                tracking-[-0.035em]
                text-white
                sm:text-5xl
              "
            >
              AI agents are useful.
              <span className="block text-slate-500">
                Their permissions are often not.
              </span>
            </h2>

            <p
              className="
                mt-6
                max-w-xl
                text-base
                leading-7
                text-slate-400
              "
            >
              Modern coding agents can operate across source control,
              CI, tickets, deployments, and secrets. The security problem
              is that tool availability is usually much broader than the
              authority required for one specific task.
            </p>

            <div
              className="
                mt-8
                border-l border-blue-400/30
                pl-5
              "
            >
              <p
                className="
                  text-sm
                  leading-6
                  text-slate-300
                "
              >
                The goal is not to make the agent less capable.
                It is to make its authority match the task.
              </p>
            </div>
          </motion.div>

          <div className="space-y-3">
            {problems.map(
              (
                {
                  icon: Icon,
                  title,
                  description,
                },
                index,
              ) => (
                <motion.article
                  key={title}
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
                    amount: 0.25,
                  }}
                  transition={{
                    duration: 0.45,
                    delay: index * 0.08,
                  }}
                  className="
                    tf-panel
                    tf-panel-interactive
                    group
                    p-5 sm:p-6
                  "
                >
                  <div
                    className="
                      flex flex-col gap-4
                      sm:flex-row
                      sm:items-start
                    "
                  >
                    <div
                      className="
                        flex h-10 w-10
                        shrink-0
                        items-center justify-center
                        rounded-xl
                        border border-white/[0.07]
                        bg-white/[0.025]
                        transition
                        group-hover:border-red-400/15
                        group-hover:bg-red-400/[0.04]
                      "
                    >
                      <Icon
                        className="
                          h-4.5 w-4.5
                          text-slate-400
                          transition
                          group-hover:text-red-400
                        "
                        strokeWidth={1.7}
                      />
                    </div>

                    <div>
                      <h3
                        className="
                          text-base
                          font-medium
                          text-slate-100
                        "
                      >
                        {title}
                      </h3>

                      <p
                        className="
                          mt-2
                          max-w-2xl
                          text-sm
                          leading-6
                          text-slate-500
                        "
                      >
                        {description}
                      </p>
                    </div>
                  </div>
                </motion.article>
              ),
            )}
          </div>
        </div>

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
          }}
          transition={{
            duration: 0.5,
            delay: 0.2,
          }}
          className="
            mt-16
            overflow-hidden
            rounded-2xl
            border border-white/[0.07]
            bg-[#080d16]
          "
        >
          <div
            className="
              grid
              md:grid-cols-[1fr_auto_1fr]
              md:items-center
            "
          >
            <div className="p-6 sm:p-8">
              <p
                className="
                  tf-mono
                  text-[10px]
                  uppercase
                  tracking-[0.18em]
                  text-slate-600
                "
              >
                Typical agent access
              </p>

              <p
                className="
                  mt-3
                  text-2xl
                  font-semibold
                  tracking-tight
                  text-white
                "
              >
                11 capabilities visible
              </p>

              <p
                className="
                  mt-2
                  text-sm
                  leading-6
                  text-slate-500
                "
              >
                Repository, CI, tickets, pull requests,
                releases, and secrets.
              </p>
            </div>

            <div
              className="
                hidden h-20 w-px
                bg-gradient-to-b
                from-transparent
                via-white/10
                to-transparent
                md:block
              "
            />

            <div className="p-6 sm:p-8">
              <p
                className="
                  tf-mono
                  text-[10px]
                  uppercase
                  tracking-[0.18em]
                  text-blue-400
                "
              >
                Actual BUG-17 need
              </p>

              <p
                className="
                  mt-3
                  text-2xl
                  font-semibold
                  tracking-tight
                  text-white
                "
              >
                Only 6 capabilities required
              </p>

              <p
                className="
                  mt-2
                  text-sm
                  leading-6
                  text-slate-500
                "
              >
                ToolFence reduces the active capability
                surface by 45.45% for the golden task.
              </p>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  )
}
