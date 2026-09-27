import {
  Link,
  NavLink,
} from "react-router-dom"

import {
  Activity,
  ArrowLeft,
  FileText,
  Gauge,
  LayoutDashboard,
  LockKeyhole,
  ShieldCheck,
} from "lucide-react"


const navigation = [
  {
    label: "Overview",
    icon: LayoutDashboard,
    to: "/dashboard",
    end: true,
  },
  {
    label: "Policy",
    icon: LockKeyhole,
    to: "/dashboard/policy",
    end: false,
  },
  {
    label: "Activity",
    icon: Activity,
    to: "/dashboard/activity",
    end: false,
  },
  {
    label: "Audit",
    icon: FileText,
    to: "/dashboard/audit",
    end: false,
  },
  {
    label: "Benchmark",
    icon: Gauge,
    to: "/dashboard/benchmark",
    end: false,
  },
]


export function DashboardSidebar() {
  return (
    <aside
      className="
        hidden w-64 shrink-0
        border-r border-white/[0.06]
        bg-[#070b12]
        lg:flex
        lg:flex-col
      "
    >
      <div
        className="
          flex h-16
          items-center gap-3
          border-b border-white/[0.06]
          px-5
        "
      >
        <div
          className="
            flex h-9 w-9
            items-center justify-center
            rounded-xl
            border border-blue-400/20
            bg-blue-500/10
            shadow-[0_0_30px_rgba(59,130,246,0.08)]
          "
        >
          <ShieldCheck
            className="h-5 w-5 text-blue-400"
            strokeWidth={1.8}
          />
        </div>

        <div>
          <p
            className="
              text-sm
              font-semibold
              tracking-tight
              text-white
            "
          >
            ToolFence
          </p>

          <p
            className="
              tf-mono mt-1
              text-[8px]
              uppercase
              tracking-[0.14em]
              text-slate-600
            "
          >
            Security Console
          </p>
        </div>
      </div>

      <div className="px-4 pt-5">
        <p
          className="
            tf-mono
            px-2
            text-[9px]
            uppercase
            tracking-[0.16em]
            text-slate-700
          "
        >
          Workspace
        </p>
      </div>

      <nav className="flex-1 p-3">
        <div className="space-y-1">
          {navigation.map(
            ({
              label,
              icon: Icon,
              to,
              end,
            }) => (
              <NavLink
                key={label}
                to={to}
                end={end}
                className={({
                  isActive,
                }) => `
                  group
                  flex w-full
                  items-center gap-3
                  rounded-lg
                  px-3 py-2.5
                  text-sm
                  transition
                  ${
                    isActive
                      ? `
                        border
                        border-blue-400/[0.10]
                        bg-blue-500/[0.08]
                        text-slate-100
                        shadow-[inset_0_0_20px_rgba(59,130,246,0.025)]
                      `
                      : `
                        border
                        border-transparent
                        text-slate-500
                        hover:bg-white/[0.035]
                        hover:text-slate-200
                      `
                  }
                `}
              >
                {({
                  isActive,
                }) => (
                  <>
                    <Icon
                      className={`
                        h-4 w-4
                        transition
                        ${
                          isActive
                            ? "text-blue-400"
                            : `
                              text-slate-600
                              group-hover:text-blue-400
                            `
                        }
                      `}
                      strokeWidth={1.8}
                    />

                    <span>
                      {label}
                    </span>

                    {isActive && (
                      <span
                        className="
                          ml-auto
                          h-1.5 w-1.5
                          rounded-full
                          bg-blue-400
                          shadow-[0_0_8px_rgba(96,165,250,0.65)]
                        "
                      />
                    )}
                  </>
                )}
              </NavLink>
            ),
          )}
        </div>
      </nav>

      <div className="px-4 pb-4">
        <div
          className="
            rounded-xl
            border border-emerald-400/[0.08]
            bg-emerald-400/[0.025]
            p-4
          "
        >
          <div className="flex items-center gap-2">
            <span
              className="
                h-1.5 w-1.5
                rounded-full
                bg-emerald-400
                shadow-[0_0_8px_rgba(74,222,128,0.65)]
              "
            />

            <span
              className="
                tf-mono
                text-[9px]
                uppercase
                tracking-[0.12em]
                text-emerald-400
              "
            >
              Gateway Online
            </span>
          </div>

          <p
            className="
              mt-3
              text-xs
              leading-5
              text-slate-600
            "
          >
            Protected MCP calls pass through deterministic authorization.
          </p>
        </div>
      </div>

      <div
        className="
          border-t border-white/[0.06]
          p-4
        "
      >
        <Link
          to="/"
          className="
            flex items-center gap-2
            rounded-lg
            px-2 py-2
            text-xs
            text-slate-500
            transition
            hover:bg-white/[0.03]
            hover:text-white
          "
        >
          <ArrowLeft className="h-3.5 w-3.5" />
          Back to product site
        </Link>
      </div>
    </aside>
  )
}
