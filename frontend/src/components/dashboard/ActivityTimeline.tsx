import {
  CheckCircle2,
  CircleSlash2,
  FileCode2,
  GitPullRequest,
  PlayCircle,
  Ticket,
} from "lucide-react"

export type ActivityEvent = {
  id: number
  tool: string
  resource: string
  decision: "ALLOW" | "DENY"
  executionStatus: string
  result?: string
}

type ActivityTimelineProps = {
  events: ActivityEvent[]
}

const toolIcons = {
  "ticket.get": Ticket,
  "repo.read": FileCode2,
  "repo.write": FileCode2,
  "ci.run": PlayCircle,
  "ci.status": PlayCircle,
  "pull_request.create": GitPullRequest,
} as const

export function ActivityTimeline({
  events,
}: ActivityTimelineProps) {
  return (
    <section
      id="activity"
      className="tf-panel overflow-hidden"
    >
      <div
        className="
          flex items-center justify-between
          border-b border-white/[0.06]
          px-5 py-4
          sm:px-6
        "
      >
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
            Protected activity
          </p>

          <h2
            className="
              mt-2
              text-xl
              font-medium
              text-white
            "
          >
            Authorization timeline
          </h2>

          <p className="mt-1 text-xs text-slate-600">
            Protected calls evaluated by ToolFence.
          </p>
        </div>

        <span
          className="
            rounded-lg
            border border-white/[0.06]
            bg-white/[0.02]
            px-2.5 py-1.5
            tf-mono
            text-[9px]
            text-slate-500
          "
        >
          {events.length} EVENTS
        </span>
      </div>

      <div className="p-5 sm:p-6">
        <div className="relative">
          <div
            className="
              absolute
              bottom-5 left-[17px] top-5
              w-px
              bg-white/[0.06]
            "
          />

          <div className="space-y-4">
            {events.map(
              (
                {
                  id,
                  tool,
                  resource,
                  decision,
                  executionStatus,
                  result,
                },
                index,
              ) => {
                const allowed =
                  decision === "ALLOW"

                const Icon =
                  toolIcons[
                    tool as keyof typeof toolIcons
                  ] ??
                  (allowed
                    ? CheckCircle2
                    : CircleSlash2)

                return (
                  <div
                    key={`${id}-${tool}`}
                    className="
                      relative
                      grid gap-3
                      pl-12
                    "
                  >
                    <div
                      className={`
                        absolute left-0 top-1
                        z-10
                        flex h-9 w-9
                        items-center justify-center
                        rounded-xl
                        border
                        ${
                          allowed
                            ? "border-emerald-400/12 bg-[#0d1714]"
                            : "border-red-400/12 bg-[#171011]"
                        }
                      `}
                    >
                      <Icon
                        className={`
                          h-4 w-4
                          ${
                            allowed
                              ? "text-emerald-400"
                              : "text-red-400"
                          }
                        `}
                        strokeWidth={1.8}
                      />
                    </div>

                    <div
                      className="
                        rounded-xl
                        border border-white/[0.05]
                        bg-white/[0.015]
                        p-4
                      "
                    >
                      <div
                        className="
                          flex flex-col gap-3
                          sm:flex-row
                          sm:items-start
                          sm:justify-between
                        "
                      >
                        <div>
                          <div
                            className="
                              flex flex-wrap
                              items-center gap-2
                            "
                          >
                            <span
                              className="
                                tf-mono
                                text-[10px]
                                text-slate-600
                              "
                            >
                              #{id}
                            </span>

                            <span
                              className="
                                tf-mono
                                text-[11px]
                                text-slate-200
                              "
                            >
                              {tool}
                            </span>

                            <span
                              className={`
                                rounded-md
                                border
                                px-2 py-0.5
                                tf-mono
                                text-[8px]
                                tracking-[0.08em]
                                ${
                                  allowed
                                    ? "border-emerald-400/10 bg-emerald-400/[0.04] text-emerald-400"
                                    : "border-red-400/10 bg-red-400/[0.04] text-red-400"
                                }
                              `}
                            >
                              {decision}
                            </span>
                          </div>

                          <p
                            className="
                              tf-mono
                              mt-2
                              break-all
                              text-[9px]
                              text-slate-600
                            "
                          >
                            {resource}
                          </p>
                        </div>

                        <div className="sm:text-right">
                          <p
                            className="
                              tf-mono
                              text-[8px]
                              uppercase
                              tracking-[0.12em]
                              text-slate-700
                            "
                          >
                            Execution
                          </p>

                          <p
                            className={`
                              tf-mono
                              mt-1
                              text-[9px]
                              ${
                                allowed
                                  ? "text-slate-400"
                                  : "text-red-400"
                              }
                            `}
                          >
                            {executionStatus}
                          </p>
                        </div>
                      </div>

                      {result && (
                        <div
                          className="
                            mt-3
                            border-t border-white/[0.05]
                            pt-3
                          "
                        >
                          <p
                            className="
                              text-xs
                              text-slate-500
                            "
                          >
                            {result}
                          </p>
                        </div>
                      )}

                      {index ===
                        events.length - 1 && (
                        <div
                          className="
                            mt-3
                            flex items-center gap-2
                          "
                        >
                          <span
                            className="
                              h-1.5 w-1.5
                              rounded-full
                              bg-blue-400
                            "
                          />

                          <span
                            className="
                              tf-mono
                              text-[8px]
                              uppercase
                              tracking-[0.12em]
                              text-blue-400
                            "
                          >
                            latest event
                          </span>
                        </div>
                      )}
                    </div>
                  </div>
                )
              },
            )}
          </div>
        </div>
      </div>
    </section>
  )
}
