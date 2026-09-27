import {
  CheckCircle2,
  ShieldCheck,
  XCircle,
} from "lucide-react"

export type CapabilityMatrixItem = {
  tool: string
  granted: boolean
  resource?: string
}

type CapabilityMatrixProps = {
  capabilities: CapabilityMatrixItem[]
}

export function CapabilityMatrix({
  capabilities,
}: CapabilityMatrixProps) {
  const grantedCount =
    capabilities.filter(
      (capability) => capability.granted,
    ).length

  const excludedCount =
    capabilities.length - grantedCount

  return (
    <section
      id="capabilities"
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
          <p
            className="
              tf-mono
              text-[10px]
              uppercase
              tracking-[0.16em]
              text-blue-400
            "
          >
            Capability boundary
          </p>

          <h2
            className="
              mt-2
              text-xl
              font-medium
              text-white
            "
          >
            Protected MCP capabilities
          </h2>

          <p
            className="
              mt-1
              text-xs
              text-slate-600
            "
          >
            Visibility does not imply authorization.
          </p>
        </div>

        <div className="flex gap-2">
          <span
            className="
              rounded-lg
              border border-emerald-400/10
              bg-emerald-400/[0.04]
              px-2.5 py-1.5
              tf-mono
              text-[9px]
              text-emerald-400
            "
          >
            {grantedCount} GRANTED
          </span>

          <span
            className="
              rounded-lg
              border border-red-400/10
              bg-red-400/[0.04]
              px-2.5 py-1.5
              tf-mono
              text-[9px]
              text-red-400
            "
          >
            {excludedCount} EXCLUDED
          </span>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full min-w-[680px] border-collapse">
          <thead>
            <tr
              className="
                border-b border-white/[0.05]
                bg-white/[0.01]
              "
            >
              <th
                className="
                  px-5 py-3
                  text-left
                  tf-mono
                  text-[9px]
                  font-normal
                  uppercase
                  tracking-[0.14em]
                  text-slate-700
                  sm:px-6
                "
              >
                Capability
              </th>

              <th
                className="
                  px-5 py-3
                  text-left
                  tf-mono
                  text-[9px]
                  font-normal
                  uppercase
                  tracking-[0.14em]
                  text-slate-700
                "
              >
                Resource scope
              </th>

              <th
                className="
                  px-5 py-3
                  text-right
                  tf-mono
                  text-[9px]
                  font-normal
                  uppercase
                  tracking-[0.14em]
                  text-slate-700
                  sm:px-6
                "
              >
                Policy state
              </th>
            </tr>
          </thead>

          <tbody>
            {capabilities.map(
              ({
                tool,
                granted,
                resource,
              }) => (
                <tr
                  key={tool}
                  className="
                    border-b border-white/[0.04]
                    transition
                    last:border-b-0
                    hover:bg-white/[0.015]
                  "
                >
                  <td
                    className="
                      px-5 py-3.5
                      sm:px-6
                    "
                  >
                    <div className="flex items-center gap-3">
                      <div
                        className={`
                          flex h-8 w-8
                          shrink-0
                          items-center justify-center
                          rounded-lg
                          border
                          ${
                            granted
                              ? "border-emerald-400/10 bg-emerald-400/[0.04]"
                              : "border-white/[0.05] bg-white/[0.015]"
                          }
                        `}
                      >
                        <ShieldCheck
                          className={`
                            h-3.5 w-3.5
                            ${
                              granted
                                ? "text-emerald-400"
                                : "text-slate-700"
                            }
                          `}
                          strokeWidth={1.8}
                        />
                      </div>

                      <span
                        className={`
                          tf-mono
                          text-[10px]
                          ${
                            granted
                              ? "text-slate-300"
                              : "text-slate-600"
                          }
                        `}
                      >
                        {tool}
                      </span>
                    </div>
                  </td>

                  <td className="px-5 py-3.5">
                    {granted && resource ? (
                      <code
                        className="
                          tf-mono
                          rounded-md
                          border border-white/[0.05]
                          bg-black/20
                          px-2 py-1
                          text-[9px]
                          text-slate-500
                        "
                      >
                        {resource}
                      </code>
                    ) : (
                      <span
                        className="
                          tf-mono
                          text-[9px]
                          text-slate-700
                        "
                      >
                        —
                      </span>
                    )}
                  </td>

                  <td
                    className="
                      px-5 py-3.5
                      text-right
                      sm:px-6
                    "
                  >
                    {granted ? (
                      <span
                        className="
                          inline-flex
                          items-center gap-1.5
                          rounded-md
                          border border-emerald-400/10
                          bg-emerald-400/[0.04]
                          px-2 py-1
                          tf-mono
                          text-[8px]
                          tracking-[0.08em]
                          text-emerald-400
                        "
                      >
                        <CheckCircle2 className="h-3 w-3" />
                        GRANTED
                      </span>
                    ) : (
                      <span
                        className="
                          inline-flex
                          items-center gap-1.5
                          rounded-md
                          border border-red-400/10
                          bg-red-400/[0.03]
                          px-2 py-1
                          tf-mono
                          text-[8px]
                          tracking-[0.08em]
                          text-red-400
                        "
                      >
                        <XCircle className="h-3 w-3" />
                        EXCLUDED
                      </span>
                    )}
                  </td>
                </tr>
              ),
            )}
          </tbody>
        </table>
      </div>

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
          Excluded capabilities remain available in the platform inventory
          but cannot execute through ToolFence unless granted by the active
          task policy.
        </p>
      </div>
    </section>
  )
}
