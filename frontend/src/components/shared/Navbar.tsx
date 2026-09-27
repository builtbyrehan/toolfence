import { ExternalLink, LayoutDashboard } from "lucide-react"
import { Link } from "react-router-dom"

import { Logo } from "@/components/shared/Logo"

const navItems = [
  {
    label: "How it works",
    href: "#how-it-works",
  },
  {
    label: "Security",
    href: "#security",
  },
  {
    label: "Benchmark",
    href: "#benchmark",
  },
  {
    label: "Architecture",
    href: "#architecture",
  },
]

export function Navbar() {
  return (
    <header
      className="
        fixed inset-x-0 top-0 z-50
        border-b border-white/[0.06]
        bg-[#060910]/80
        backdrop-blur-xl
      "
    >
      <div
        className="
          tf-container
          flex h-[72px]
          items-center
          justify-between
          gap-6
        "
      >
        <Link
          to="/"
          aria-label="ToolFence home"
          className="shrink-0"
        >
          <Logo />
        </Link>

        <nav
          className="
            hidden
            items-center
            gap-7
            lg:flex
          "
          aria-label="Primary navigation"
        >
          {navItems.map((item) => (
            <a
              key={item.href}
              href={item.href}
              className="
                text-sm
                text-slate-400
                transition-colors
                hover:text-white
              "
            >
              {item.label}
            </a>
          ))}
        </nav>

        <div className="flex items-center gap-2">
          <a
            href="https://github.com/builtbyrehan/toolfence"
            target="_blank"
            rel="noreferrer"
            aria-label="Open ToolFence on GitHub"
            className="
              hidden h-10 w-10
              items-center justify-center
              rounded-xl
              border border-white/[0.08]
              bg-white/[0.03]
              text-slate-400
              transition-all
              hover:border-white/[0.15]
              hover:bg-white/[0.06]
              hover:text-white
              sm:flex
            "
          >
            <ExternalLink
              className="h-[18px] w-[18px]"
              strokeWidth={1.8}
            />
          </a>

          <Link
            to="/dashboard"
            className="
              inline-flex h-10
              items-center
              gap-2
              rounded-xl
              border border-blue-400/20
              bg-blue-500
              px-4
              text-sm
              font-medium
              text-white
              shadow-[0_0_30px_rgba(59,130,246,0.16)]
              transition-all
              hover:bg-blue-400
              hover:shadow-[0_0_40px_rgba(59,130,246,0.24)]
            "
          >
            <LayoutDashboard
              className="h-4 w-4"
              strokeWidth={1.8}
            />

            <span className="hidden sm:inline">
              Open Security Console
            </span>

            <span className="sm:hidden">
              Console
            </span>
          </Link>
        </div>
      </div>
    </header>
  )
}