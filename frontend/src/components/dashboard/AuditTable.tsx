import {
  CheckCircle2,
  CircleSlash2,
  FileText,
} from "lucide-react"

export type AuditEvent = {
  eventId: number
  tool: string
  resource: string
  decision: "ALLOW" | "DENY"
  reasonCode: string
  executionStatus: string
  policyId: string
}

type AuditTableProps = {
  events: AuditEvent[]
}

export function AuditTable({
  events,
}: AuditTableProps) {
  return (
    <section
      id="audit"
      className="tf-panel overflow-hidden"
    >
      <div
        className="
          flex flex-col gap-4
          border-b border-white/[0.06]
          px-5 py-4
          sm:flex-row
          sm:items-center
          sm:justify-between
          sm:px-6
        "
      >
        <div>
          <div className="flex items-center gap-2">
            <FileText className="h-4 w-4 text-blue-400" />

            <p
              className="
                tf-mono
                text-[10px]
                uppercase
                tracking-[0.16em]
                text-blue-400
              "
            >
              Audit trail
            </p>
          </div>

          <h2
            className="
              mt-2
              text-xl
              font-medium
              text-white
            "
          >
            Authorization evidence
          </h2>

          <p className="mt-1 text-xs text-slate-600">
            Decision and execution metadata for protected requests.
          </p>
        </div>

        <span
          className="
            w-fit
            rounded-lg
            border border-white/[0.06]
            bg-white/[0.02]
            px-2.5 py-1.5
            tf-mono
            text-[9px]
            text-slate-500
          "
        >
          {events.length} RECORDS
        </span>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full min-w-[1050px] border-collapse">
          <thead>
            <tr
              className="
                border-b border-white/[0.05]
                bg-white/[0.01]
              "
            >
              {[
                "Event",
                "Tool",
                "Resource",
                "Decision",
                "Reason",
                "Execution",
                "Policy",
              ].map((heading) => (
                <th
                  key={heading}
                  className="
                    px-4 py-3
                    text-left
                    tf-mono
                    text-[9px]
                    font-normal
                    uppercase
                    tracking-[0.12em]
                    text-slate-700
                    first:pl-6
                    last:pr-6
                  "
                >
                  {heading}
                </th>
              ))}
            </tr>
          </thead>

          <tbody>
            {events.map((event) => {
              const allowed =
                event.decision === "ALLOW"

              return (
                <tr
                  key={event.eventId}
                  className="
                    border-b border-white/[0.04]
                    transition
                    last:border-b-0
                    hover:bg-white/[0.015]
                  "
                >
                  <td className="px-4 py-3.5 pl-6">
                    <span
                      className="
                        tf-mono
                        text-[9px]
                        text-slate-600
                      "
                    >
                      #{event.eventId}
                    </span>
                  </td>

                  <td className="px-4 py-3.5">
                    <span
                      className="
                        tf-mono
                        text-[10px]
                        text-slate-300
                      "
                    >
                      {event.tool}
                    </span>
                  </td>

                  <td className="px-4 py-3.5">
                    <code
                      className="
                        tf-mono
                        text-[9px]
                        text-slate-600
                      "
                    >
                      {event.resource}
                    </code>
                  </td>

                  <td className="px-4 py-3.5">
                    <span
                      className={`
                        inline-flex
                        items-center gap-1.5
                        rounded-md
                        border
                        px-2 py-1
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
                      {allowed ? (
                        <CheckCircle2 className="h-3 w-3" />
                      ) : (
                        <CircleSlash2 className="h-3 w-3" />
                      )}

                      {event.decision}
                    </span>
                  </td>

                  <td className="px-4 py-3.5">
                    <span
                      className={`
                        tf-mono
                        text-[9px]
                        ${
                          allowed
                            ? "text-slate-600"
                            : "text-red-400"
                        }
                      `}
                    >
                      {event.reasonCode}
                    </span>
                  </td>

                  <td className="px-4 py-3.5">
                    <span
                      className={`
                        tf-mono
                        text-[9px]
                        ${
                          event.executionStatus ===
                          "NOT_EXECUTED"
                            ? "text-red-400"
                            : "text-slate-500"
                        }
                      `}
                    >
                      {event.executionStatus}
                    </span>
                  </td>

                  <td className="px-4 py-3.5 pr-6">
                    <code
                      className="
                        tf-mono
                        text-[9px]
                        text-slate-700
                      "
                    >
                      {event.policyId.slice(0, 10)}...
                    </code>
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>

      {events.length === 0 && (
        <div
          className="
            px-6 py-12
            text-center
          "
        >
          <p className="text-sm text-slate-500">
            No audit events recorded yet.
          </p>
        </div>
      )}

      <div
        className="
          border-t border-white/[0.05]
          bg-black/10
          px-5 py-4
          sm:px-6
        "
      >
        <p
          className="
            text-xs
            leading-5
            text-slate-600
          "
        >
          Audit events record authorization and execution state without
          exposing protected backend payloads.
        </p>
      </div>
    </section>
  )
}
