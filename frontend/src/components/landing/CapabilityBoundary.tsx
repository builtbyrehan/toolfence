import { motion } from "motion/react"
import {
  Check,
  LockKeyhole,
  ShieldCheck,
  X,
} from "lucide-react"

const granted = [
  {
    tool: "ticket.get",
    resource: "BUG-17",
  },
  {
    tool: "repo.read",
    resource: "project/*",
  },
  {
    tool: "repo.write",
    resource: "project/src/*",
  },
  {
    tool: "ci.run",
    resource: "feature/BUG-17",
  },
  {
    tool: "ci.status",
    resource: "feature/BUG-17",
  },
  {
    tool: "pull_request.create",
    resource: "feature/BUG-17",
  },
]

const excluded = [
  "ticket.comment",
  "ticket.delete",
  "release.status",
  "release.deploy",
  "secret.read",
]

export function CapabilityBoundary() {
  return (
    <section
      id="capability-boundary"
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
              border border-blue-400/15
              bg-blue-500/[0.06]
              px-3 py-1.5
            "
          >
            <ShieldCheck className="h-3.5 w-3.5 text-blue-400" />

            <span
              className="
                tf-mono
                text-[10px]
                uppercase
                tracking-[0.18em]
                text-blue-300
              "
            >
              Least-privilege boundary
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
            11 capabilities exist.
            <span className="block text-slate-500">
              This task receives only 6.
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
            ToolFence keeps capability availability separate from
            authorization. IBM Bob can see what the platform supports,
            but the active task policy determines what may actually execute.
          </p>
        </motion.div>

        <div
          className="
            mt-14
            grid gap-5
            lg:grid-cols-[1fr_auto_1fr]
            lg:items-stretch
          "
        >
          {/* Available */}
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
            className="tf-panel p-5 sm:p-6"
          >
            <div
              className="
                flex items-center justify-between
                border-b border-white/[0.06]
                pb-4
              "
            >
              <div>
                <p
                  className="
                    tf-mono
                    text-[10px]
                    uppercase
                    tracking-[0.16em]
                    text-slate-500
                  "
                >
                  Capability inventory
                </p>

                <h3
                  className="
                    mt-2
                    text-xl
                    font-medium
                    tracking-tight
                    text-white
                  "
                >
                  Available to ToolFence
                </h3>
              </div>

              <span
                className="
                  rounded-lg
                  border border-white/[0.08]
                  bg-white/[0.03]
                  px-2.5 py-1
                  tf-mono
                  text-[10px]
                  text-slate-400
                "
              >
                11 TOTAL
              </span>
            </div>

            <div className="mt-5 space-y-2">
              {[
                ...granted.map((item) => item.tool),
                ...excluded,
              ].map((tool) => (
                <div
                  key={tool}
                  className="
                    flex items-center justify-between
                    rounded-lg
                    border border-white/[0.05]
                    bg-white/[0.015]
                    px-3 py-2.5
                  "
                >
                  <span className="tf-mono text-[11px] text-slate-400">
                    {tool}
                  </span>

                  <span
                    className="
                      tf-mono
                      text-[9px]
                      text-slate-600
                    "
                  >
                    VISIBLE
                  </span>
                </div>
              ))}
            </div>
          </motion.div>

          {/* Fence */}
          <motion.div
            initial={{
              opacity: 0,
              scale: 0.96,
            }}
            whileInView={{
              opacity: 1,
              scale: 1,
            }}
            viewport={{
              once: true,
              amount: 0.4,
            }}
            transition={{
              duration: 0.45,
              delay: 0.1,
            }}
            className="
              flex
              items-center
              justify-center
              py-2
              lg:px-2
              lg:py-0
            "
          >
            <div
              className="
                flex
                min-w-[150px]
                flex-col
                items-center
                rounded-2xl
                border border-blue-400/15
                bg-blue-500/[0.05]
                px-6 py-6
                text-center
                shadow-[0_0_50px_rgba(59,130,246,0.08)]
              "
            >
              <div
                className="
                  flex h-11 w-11
                  items-center justify-center
                  rounded-xl
                  border border-blue-400/20
                  bg-blue-500/10
                "
              >
                <LockKeyhole className="h-5 w-5 text-blue-400" />
              </div>

              <p
                className="
                  mt-4
                  text-sm
                  font-medium
                  text-white
                "
              >
                ToolFence
              </p>

              <p
                className="
                  tf-mono
                  mt-2
                  text-[9px]
                  uppercase
                  tracking-[0.14em]
                  text-blue-400
                "
              >
                deterministic gate
              </p>
            </div>
          </motion.div>

          {/* Active policy */}
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
            className="tf-panel overflow-hidden"
          >
            <div className="p-5 sm:p-6">
              <div
                className="
                  flex items-center justify-between
                  border-b border-white/[0.06]
                  pb-4
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
                    Active task policy
                  </p>

                  <h3
                    className="
                      mt-2
                      text-xl
                      font-medium
                      tracking-tight
                      text-white
                    "
                  >
                    BUG-17-FIX
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
                    ACTIVE
                  </span>
                </div>
              </div>

              <div className="mt-5 space-y-2">
                {granted.map((item) => (
                  <div
                    key={item.tool}
                    className="
                      rounded-lg
                      border border-emerald-400/[0.09]
                      bg-emerald-400/[0.03]
                      px-3 py-2.5
                    "
                  >
                    <div className="flex items-center justify-between">
                      <span
                        className="
                          tf-mono
                          text-[11px]
                          text-slate-300
                        "
                      >
                        {item.tool}
                      </span>

                      <Check className="h-3.5 w-3.5 text-emerald-400" />
                    </div>

                    <p
                      className="
                        tf-mono
                        mt-1
                        truncate
                        text-[9px]
                        text-slate-600
                      "
                    >
                      {item.resource}
                    </p>
                  </div>
                ))}
              </div>
            </div>

            <div
              className="
                border-t border-white/[0.06]
                bg-black/10
                px-5 py-4
                sm:px-6
              "
            >
              <div className="flex items-center justify-between">
                <span
                  className="
                    text-xs
                    text-slate-500
                  "
                >
                  Active privilege reduction
                </span>

                <span
                  className="
                    tf-mono
                    text-xs
                    text-blue-400
                  "
                >
                  45.45%
                </span>
              </div>
            </div>
          </motion.div>
        </div>

        {/* Excluded */}
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
            amount: 0.3,
          }}
          transition={{
            duration: 0.45,
            delay: 0.1,
          }}
          className="
            mt-5
            rounded-2xl
            border border-red-400/[0.08]
            bg-red-400/[0.02]
            p-5
          "
        >
          <div
            className="
              flex flex-col gap-4
              sm:flex-row
              sm:items-center
              sm:justify-between
            "
          >
            <div>
              <p
                className="
                  tf-mono
                  text-[10px]
                  uppercase
                  tracking-[0.16em]
                  text-red-400
                "
              >
                Not granted
              </p>

              <p
                className="
                  mt-2
                  text-sm
                  text-slate-400
                "
              >
                These capabilities remain outside the active task boundary.
              </p>
            </div>

            <div className="flex flex-wrap gap-2">
              {excluded.map((tool) => (
                <span
                  key={tool}
                  className="
                    inline-flex items-center gap-1.5
                    rounded-lg
                    border border-red-400/[0.09]
                    bg-red-400/[0.04]
                    px-2.5 py-1.5
                    tf-mono
                    text-[10px]
                    text-slate-500
                  "
                >
                  <X className="h-3 w-3 text-red-400" />
                  {tool}
                </span>
              ))}
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  )
}
