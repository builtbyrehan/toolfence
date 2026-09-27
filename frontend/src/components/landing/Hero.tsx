import { Link } from "react-router-dom"
import { motion } from "motion/react"
import {
  ArrowRight,
  Check,
  LockKeyhole,
  ShieldCheck,
  X,
} from "lucide-react"

const grantedCapabilities = [
  "ticket.get",
  "repo.read",
  "repo.write",
  "ci.run",
  "ci.status",
  "pull_request.create",
]

const blockedCapabilities = [
  "ticket.delete",
  "release.deploy",
  "secret.read",
]

export function Hero() {
  return (
    <section
      className="
        relative overflow-hidden
        border-b border-white/[0.06]
        pt-28 sm:pt-32
      "
    >
      {/* Background */}
      <div className="pointer-events-none absolute inset-0">
        <div className="tf-grid-background absolute inset-0 opacity-60" />

        <div
          className="
            absolute left-1/2 top-[-220px]
            h-[600px] w-[900px]
            -translate-x-1/2
            rounded-full
            bg-blue-500/[0.08]
            blur-[120px]
          "
        />

        <div
          className="
            absolute right-[-180px] top-[200px]
            h-[400px] w-[400px]
            rounded-full
            bg-emerald-500/[0.045]
            blur-[100px]
          "
        />
      </div>

      <div className="tf-container relative">
        <div
          className="
            grid items-center gap-16
            pb-20
            lg:grid-cols-[1.05fr_0.95fr]
            lg:pb-28
          "
        >
          {/* =====================================================
              LEFT — PRODUCT MESSAGE
             ===================================================== */}

          <motion.div
            initial={{
              opacity: 0,
              y: 18,
            }}
            animate={{
              opacity: 1,
              y: 0,
            }}
            transition={{
              duration: 0.55,
              ease: "easeOut",
            }}
          >
            {/* Eyebrow */}
            <div
              className="
                mb-7 inline-flex items-center gap-2
                rounded-full
                border border-blue-400/15
                bg-blue-500/[0.07]
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
                Task-scoped security for AI agents
              </span>
            </div>

            {/* Heading */}
            <h1
              className="
                max-w-[760px]
                text-[clamp(3.1rem,7vw,6.7rem)]
                font-semibold
                leading-[0.93]
                tracking-[-0.055em]
                text-white
              "
            >
              Give AI agents
              <span className="block tf-gradient-text">
                only what they need.
              </span>
            </h1>

            {/* Copy */}
            <p
              className="
                mt-7
                max-w-[640px]
                text-base
                leading-7
                text-slate-400
                sm:text-lg
                sm:leading-8
              "
            >
              ToolFence turns a coding task into a deterministic
              capability boundary—so IBM Bob can reason freely while
              every protected tool call is independently authorized,
              scoped, and audited.
            </p>

            {/* Principle */}
            <div className="mt-7 flex items-center gap-3">
              <div
                className="
                  h-px w-8
                  bg-gradient-to-r
                  from-blue-500
                  to-transparent
                "
              />

              <p
                className="
                  tf-mono
                  text-xs
                  tracking-[0.12em]
                  text-slate-300
                "
              >
                BOB REASONS.
                <span className="ml-2 text-blue-400">
                  TOOLFENCE ENFORCES.
                </span>
              </p>
            </div>

            {/* CTA */}
            <div
              className="
                mt-10
                flex flex-col gap-3
                sm:flex-row
              "
            >
              <Link
                to="/dashboard"
                className="
                  group
                  inline-flex items-center justify-center gap-2
                  rounded-xl
                  bg-blue-500
                  px-5 py-3
                  text-sm
                  font-medium
                  text-white
                  shadow-[0_0_36px_rgba(59,130,246,0.20)]
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
                href="#how-it-works"
                className="
                  inline-flex items-center justify-center
                  rounded-xl
                  border border-white/[0.10]
                  bg-white/[0.025]
                  px-5 py-3
                  text-sm
                  font-medium
                  text-slate-300
                  transition
                  hover:border-white/[0.18]
                  hover:bg-white/[0.05]
                  hover:text-white
                "
              >
                See how it works
              </a>
            </div>

            {/* Proof points */}
            <div
              className="
                mt-12
                flex flex-wrap gap-x-7 gap-y-3
                text-xs
                text-slate-500
              "
            >
              <span>
                <strong className="mr-1 text-slate-200">
                  11
                </strong>
                protected capabilities
              </span>

              <span>
                <strong className="mr-1 text-slate-200">
                  16/16
                </strong>
                benchmark cases
              </span>

              <span>
                <strong className="mr-1 text-emerald-400">
                  100%
                </strong>
                forbidden actions blocked
              </span>
            </div>
          </motion.div>

          {/* =====================================================
              RIGHT — SECURITY VISUAL
             ===================================================== */}

          <motion.div
            initial={{
              opacity: 0,
              x: 22,
            }}
            animate={{
              opacity: 1,
              x: 0,
            }}
            transition={{
              delay: 0.12,
              duration: 0.6,
              ease: "easeOut",
            }}
            className="relative"
          >
            <div
              className="
                absolute -inset-10
                rounded-[40px]
                bg-blue-500/[0.04]
                blur-3xl
              "
            />

            <div
              className="
                tf-panel
                relative
                overflow-hidden
                rounded-[22px]
              "
            >
              {/* Console header */}
              <div
                className="
                  flex items-center justify-between
                  border-b border-white/[0.07]
                  px-5 py-4
                "
              >
                <div className="flex items-center gap-3">
                  <div className="flex gap-1.5">
                    <span className="h-2.5 w-2.5 rounded-full bg-slate-700" />
                    <span className="h-2.5 w-2.5 rounded-full bg-slate-700" />
                    <span className="h-2.5 w-2.5 rounded-full bg-slate-700" />
                  </div>

                  <span
                    className="
                      tf-mono
                      text-[10px]
                      uppercase
                      tracking-[0.16em]
                      text-slate-500
                    "
                  >
                    Active Task Boundary
                  </span>
                </div>

                <div
                  className="
                    inline-flex items-center gap-2
                    rounded-full
                    border border-emerald-400/15
                    bg-emerald-400/[0.07]
                    px-2.5 py-1
                  "
                >
                  <span
                    className="
                      h-1.5 w-1.5
                      rounded-full
                      bg-emerald-400
                      shadow-[0_0_8px_rgba(74,222,128,0.8)]
                    "
                  />

                  <span
                    className="
                      tf-mono
                      text-[9px]
                      tracking-[0.12em]
                      text-emerald-300
                    "
                  >
                    POLICY ACTIVE
                  </span>
                </div>
              </div>

              {/* Task */}
              <div className="border-b border-white/[0.07] p-5">
                <div
                  className="
                    mb-2
                    flex items-center justify-between
                  "
                >
                  <span
                    className="
                      tf-mono
                      text-[10px]
                      uppercase
                      tracking-[0.16em]
                      text-slate-500
                    "
                  >
                    BUG-17-FIX
                  </span>

                  <LockKeyhole className="h-4 w-4 text-blue-400" />
                </div>

                <p
                  className="
                    text-sm
                    leading-6
                    text-slate-200
                  "
                >
                  Fix BUG-17, run CI, and create a pull request.
                </p>
              </div>

              {/* Capability boundary */}
              <div className="p-5">
                <div
                  className="
                    mb-4
                    flex items-center justify-between
                  "
                >
                  <p
                    className="
                      text-xs
                      font-medium
                      text-slate-300
                    "
                  >
                    Capability Boundary
                  </p>

                  <span
                    className="
                      tf-mono
                      text-[10px]
                      text-slate-500
                    "
                  >
                    6 / 11 GRANTED
                  </span>
                </div>

                <div className="space-y-2">
                  {grantedCapabilities.map((capability) => (
                    <div
                      key={capability}
                      className="
                        flex items-center justify-between
                        rounded-lg
                        border border-emerald-400/[0.09]
                        bg-emerald-400/[0.035]
                        px-3 py-2
                      "
                    >
                      <span className="tf-mono text-[11px] text-slate-300">
                        {capability}
                      </span>

                      <span className="flex items-center gap-1.5">
                        <Check className="h-3.5 w-3.5 text-emerald-400" />

                        <span
                          className="
                            tf-mono
                            text-[9px]
                            text-emerald-400
                          "
                        >
                          ALLOW
                        </span>
                      </span>
                    </div>
                  ))}

                  {blockedCapabilities.map((capability) => (
                    <div
                      key={capability}
                      className="
                        flex items-center justify-between
                        rounded-lg
                        border border-red-400/[0.08]
                        bg-red-400/[0.025]
                        px-3 py-2
                      "
                    >
                      <span className="tf-mono text-[11px] text-slate-500">
                        {capability}
                      </span>

                      <span className="flex items-center gap-1.5">
                        <X className="h-3.5 w-3.5 text-red-400" />

                        <span
                          className="
                            tf-mono
                            text-[9px]
                            text-red-400
                          "
                        >
                          DENY
                        </span>
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Footer status */}
              <div
                className="
                  flex items-center justify-between
                  border-t border-white/[0.07]
                  bg-black/10
                  px-5 py-3
                "
              >
                <span
                  className="
                    tf-mono
                    text-[9px]
                    uppercase
                    tracking-[0.12em]
                    text-slate-600
                  "
                >
                  deterministic authorization
                </span>

                <span
                  className="
                    tf-mono
                    text-[10px]
                    text-blue-400
                  "
                >
                  45.45% less privilege
                </span>
              </div>
            </div>

            {/* Floating deny card */}
            <motion.div
              initial={{
                opacity: 0,
                y: 12,
              }}
              animate={{
                opacity: 1,
                y: 0,
              }}
              transition={{
                delay: 0.55,
                duration: 0.4,
              }}
              className="
                absolute
                -bottom-8
                -left-5
                hidden
                w-[245px]
                rounded-xl
                border border-red-400/15
                bg-[#0b111b]/95
                p-3.5
                shadow-2xl
                backdrop-blur-xl
                sm:block
              "
            >
              <div className="flex items-start gap-3">
                <div
                  className="
                    mt-0.5
                    flex h-7 w-7
                    shrink-0
                    items-center justify-center
                    rounded-lg
                    bg-red-400/[0.08]
                  "
                >
                  <X className="h-3.5 w-3.5 text-red-400" />
                </div>

                <div>
                  <div className="flex items-center gap-2">
                    <span className="tf-mono text-[10px] text-slate-300">
                      secret.read
                    </span>

                    <span className="tf-mono text-[9px] text-red-400">
                      DENY
                    </span>
                  </div>

                  <p className="mt-1 text-[10px] leading-4 text-slate-500">
                    TOOL_NOT_GRANTED · NOT_EXECUTED
                  </p>
                </div>
              </div>
            </motion.div>
          </motion.div>
        </div>
      </div>
    </section>
  )
}