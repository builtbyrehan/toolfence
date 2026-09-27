import { Link } from "react-router-dom"
import {
  ExternalLink,
  ShieldCheck,
} from "lucide-react"

export function Footer() {
  return (
    <footer className="border-t border-white/[0.06] bg-[#060910]">
      <div className="tf-container py-10">
        <div className="grid gap-10 md:grid-cols-[1.2fr_0.8fr_0.8fr]">
          <div>
            <div className="flex items-center gap-3">
              <div
                className="
                  flex h-9 w-9 items-center justify-center
                  rounded-xl
                  border border-blue-400/20
                  bg-blue-500/10
                "
              >
                <ShieldCheck
                  className="h-5 w-5 text-blue-400"
                  strokeWidth={1.8}
                />
              </div>

              <div>
                <p className="text-sm font-semibold tracking-tight text-white">
                  ToolFence
                </p>

                <p
                  className="
                    tf-mono mt-1
                    text-[9px] uppercase
                    tracking-[0.16em]
                    text-slate-600
                  "
                >
                  Task-scoped security
                </p>
              </div>
            </div>

            <p
              className="
                mt-5 max-w-sm
                text-sm leading-6
                text-slate-500
              "
            >
              Deterministic task-scoped authorization for AI coding-agent
              tool calls.
            </p>

            <p
              className="
                tf-mono mt-5
                text-[10px] uppercase
                tracking-[0.14em]
                text-blue-400
              "
            >
              Bob reasons. ToolFence enforces.
            </p>
          </div>

          <div>
            <p
              className="
                tf-mono
                text-[10px] uppercase
                tracking-[0.16em]
                text-slate-600
              "
            >
              Product
            </p>

            <div className="mt-4 flex flex-col gap-3 text-sm text-slate-500">
              <a
                href="#how-it-works"
                className="transition hover:text-white"
              >
                How it works
              </a>

              <a
                href="#architecture"
                className="transition hover:text-white"
              >
                Architecture
              </a>

              <a
                href="#benchmark"
                className="transition hover:text-white"
              >
                Benchmark
              </a>

              <Link
                to="/dashboard"
                className="transition hover:text-white"
              >
                Security Console
              </Link>
            </div>
          </div>

          <div>
            <p
              className="
                tf-mono
                text-[10px] uppercase
                tracking-[0.16em]
                text-slate-600
              "
            >
              Project
            </p>

            <div className="mt-4 flex flex-col gap-3 text-sm text-slate-500">
              <a
                href="https://github.com/builtbyrehan/toolfence"
                target="_blank"
                rel="noreferrer"
                className="
                  inline-flex items-center gap-2
                  transition hover:text-white
                "
              >
                GitHub
                <ExternalLink className="h-3.5 w-3.5" />
              </a>

              <span>IBM Bob 2.0 Hackathon</span>
              <span>MCP Security Gateway</span>
            </div>
          </div>
        </div>

        <div
          className="
            mt-10 flex flex-col gap-3
            border-t border-white/[0.06]
            pt-6
            sm:flex-row
            sm:items-center
            sm:justify-between
          "
        >
          <p className="text-xs text-slate-600">
            ToolFence — Hackathon MVP
          </p>

          <p
            className="
              tf-mono
              text-[9px] uppercase
              tracking-[0.12em]
              text-slate-700
            "
          >
            least privilege · deterministic enforcement · auditability
          </p>
        </div>
      </div>
    </footer>
  )
}
