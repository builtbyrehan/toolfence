import { Link } from "react-router-dom"
import {
  ArrowLeft,
  ShieldCheck,
} from "lucide-react"

type DashboardHeaderProps = {
  taskId: string
  policyStatus: string
}

export function DashboardHeader({
  taskId,
  policyStatus,
}: DashboardHeaderProps) {
  const active =
    policyStatus.toUpperCase() === "ACTIVE"

  return (
    <header
      className="
        sticky top-0 z-30
        flex min-h-16
        items-center justify-between
        border-b border-white/[0.06]
        bg-[#070b12]/90
        px-4
        backdrop-blur-xl
        sm:px-6
      "
    >
      <div className="flex items-center gap-4">
        <Link
          to="/"
          className="
            inline-flex h-9 w-9
            items-center justify-center
            rounded-lg
            border border-white/[0.06]
            bg-white/[0.02]
            text-slate-500
            transition
            hover:border-white/[0.12]
            hover:bg-white/[0.04]
            hover:text-white
            lg:hidden
          "
          aria-label="Back to ToolFence landing page"
        >
          <ArrowLeft className="h-4 w-4" />
        </Link>

        <div>
          <p
            className="
              tf-mono
              text-[9px]
              uppercase
              tracking-[0.16em]
              text-slate-600
            "
          >
            Current task
          </p>

          <p className="mt-1 text-sm font-medium text-slate-200">
            {taskId}
          </p>
        </div>
      </div>

      <div
        className={`
          inline-flex
          items-center gap-2
          rounded-full
          border
          px-3 py-1.5
          ${
            active
              ? "border-emerald-400/15 bg-emerald-400/[0.06]"
              : "border-amber-400/15 bg-amber-400/[0.06]"
          }
        `}
      >
        <ShieldCheck
          className={`
            h-3.5 w-3.5
            ${
              active
                ? "text-emerald-400"
                : "text-amber-400"
            }
          `}
        />

        <span
          className={`
            h-1.5 w-1.5
            rounded-full
            ${
              active
                ? "bg-emerald-400 shadow-[0_0_8px_rgba(74,222,128,0.75)]"
                : "bg-amber-400"
            }
          `}
        />

        <span
          className={`
            tf-mono
            text-[9px]
            uppercase
            tracking-[0.12em]
            ${
              active
                ? "text-emerald-300"
                : "text-amber-300"
            }
          `}
        >
          Policy {policyStatus}
        </span>
      </div>
    </header>
  )
}
