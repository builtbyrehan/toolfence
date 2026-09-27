import { Link } from "react-router-dom"
import { motion } from "motion/react"
import {
  ArrowRight,
  ShieldCheck,
  TerminalSquare,
} from "lucide-react"

export function CTASection() {
  return (
    <section
      id="cta"
      className="
        relative
        overflow-hidden
        border-b border-white/[0.06]
        py-24 sm:py-28
      "
    >
      <div
        className="
          pointer-events-none
          absolute inset-0
          bg-[radial-gradient(circle_at_50%_50%,rgba(59,130,246,0.08),transparent_52%)]
        "
      />

      <div className="tf-container relative">
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
            amount: 0.3,
          }}
          transition={{
            duration: 0.5,
          }}
          className="
            relative
            overflow-hidden
            rounded-[24px]
            border border-blue-400/15
            bg-[#0a101a]
            px-6 py-12
            shadow-[0_0_80px_rgba(59,130,246,0.06)]
            sm:px-10
            sm:py-16
            lg:px-14
          "
        >
          <div
            className="
              pointer-events-none
              absolute
              inset-0
              tf-grid-background
              opacity-30
            "
          />

          <div
            className="
              relative
              grid gap-10
              lg:grid-cols-[1fr_auto]
              lg:items-end
            "
          >
            <div className="max-w-3xl">
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
                  Security console ready
                </span>
              </div>

              <h2
                className="
                  text-4xl
                  font-semibold
                  leading-[1.03]
                  tracking-[-0.04em]
                  text-white
                  sm:text-5xl
                  lg:text-6xl
                "
              >
                See every capability.
                <span className="block tf-gradient-text">
                  See every decision.
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
                Open the ToolFence Security Console to inspect the
                active task policy, capability boundary, live tool
                activity, audit events, and replay benchmark evidence.
              </p>

              <div
                className="
                  mt-8
                  flex flex-wrap gap-x-6 gap-y-3
                  tf-mono
                  text-[10px]
                  uppercase
                  tracking-[0.12em]
                  text-slate-600
                "
              >
                <span>15 MCP tools</span>
                <span>11 protected capabilities</span>
                <span>16 benchmark scenarios</span>
              </div>
            </div>

            <div
              className="
                flex flex-col gap-3
                sm:flex-row
                lg:flex-col
              "
            >
              <Link
                to="/dashboard"
                className="
                  group
                  inline-flex
                  min-w-[220px]
                  items-center
                  justify-center
                  gap-2
                  rounded-xl
                  bg-blue-500
                  px-5 py-3
                  text-sm
                  font-medium
                  text-white
                  shadow-[0_0_36px_rgba(59,130,246,0.18)]
                  transition
                  hover:bg-blue-400
                "
              >
                Open Security Console

                <ArrowRight
                  className="
                    h-4 w-4
                    transition-transform
                    group-hover:translate-x-0.5
                  "
                />
              </Link>

              <a
                href="https://github.com/builtbyrehan/toolfence"
                target="_blank"
                rel="noreferrer"
                className="
                  inline-flex
                  min-w-[220px]
                  items-center
                  justify-center
                  gap-2
                  rounded-xl
                  border border-white/[0.09]
                  bg-white/[0.02]
                  px-5 py-3
                  text-sm
                  font-medium
                  text-slate-300
                  transition
                  hover:border-white/[0.16]
                  hover:bg-white/[0.04]
                  hover:text-white
                "
              >
                <TerminalSquare className="h-4 w-4" />
                View Repository
              </a>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  )
}
