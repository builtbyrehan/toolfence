import {
  Fingerprint,
  LockKeyhole,
  ShieldCheck,
} from "lucide-react"

type PolicyCardProps = {
  taskId: string
  policyId: string
  status: string
  grantedCount: number
}

export function PolicyCard({
  taskId,
  policyId,
  status,
  grantedCount,
}: PolicyCardProps) {
  const active =
    status.toUpperCase() === "ACTIVE"

  return (
    <section
      id="policy"
      className="
        tf-panel
        overflow-hidden
      "
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
            Active policy
          </p>

          <h2
            className="
              mt-2
              text-xl
              font-medium
              text-white
            "
          >
            Task capability contract
          </h2>
        </div>

        <div
          className={`
            inline-flex
            items-center gap-2
            rounded-full
            border
            px-2.5 py-1
            ${
              active
                ? "border-emerald-400/15 bg-emerald-400/[0.06]"
                : "border-amber-400/15 bg-amber-400/[0.06]"
            }
          `}
        >
          <span
            className={`
              h-1.5 w-1.5
              rounded-full
              ${
                active
                  ? "bg-emerald-400"
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
            {status}
          </span>
        </div>
      </div>

      <div className="p-5 sm:p-6">
        <div
          className="
            grid gap-3
            sm:grid-cols-2
          "
        >
          <div
            className="
              rounded-xl
              border border-white/[0.06]
              bg-white/[0.015]
              p-4
            "
          >
            <div className="flex items-center gap-2">
              <LockKeyhole className="h-4 w-4 text-blue-400" />

              <p
                className="
                  tf-mono
                  text-[9px]
                  uppercase
                  tracking-[0.14em]
                  text-slate-600
                "
              >
                Task binding
              </p>
            </div>

            <p
              className="
                mt-3
                text-sm
                font-medium
                text-slate-200
              "
            >
              {taskId}
            </p>

            <p
              className="
                mt-2
                text-xs
                leading-5
                text-slate-600
              "
            >
              The policy is registered against this trusted task identity.
            </p>
          </div>

          <div
            className="
              rounded-xl
              border border-white/[0.06]
              bg-white/[0.015]
              p-4
            "
          >
            <div className="flex items-center gap-2">
              <ShieldCheck className="h-4 w-4 text-emerald-400" />

              <p
                className="
                  tf-mono
                  text-[9px]
                  uppercase
                  tracking-[0.14em]
                  text-slate-600
                "
              >
                Granted authority
              </p>
            </div>

            <p
              className="
                mt-3
                text-2xl
                font-semibold
                tracking-[-0.03em]
                text-white
              "
            >
              {grantedCount}
            </p>

            <p
              className="
                mt-1
                text-xs
                text-slate-600
              "
            >
              task-scoped capabilities
            </p>
          </div>
        </div>

        <div
          className="
            mt-4
            rounded-xl
            border border-blue-400/[0.08]
            bg-blue-400/[0.025]
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
            <div className="flex items-start gap-3">
              <div
                className="
                  flex h-9 w-9
                  shrink-0
                  items-center justify-center
                  rounded-lg
                  border border-blue-400/10
                  bg-blue-500/[0.05]
                "
              >
                <Fingerprint className="h-4 w-4 text-blue-400" />
              </div>

              <div>
                <p
                  className="
                    text-sm
                    font-medium
                    text-slate-300
                  "
                >
                  Policy identity
                </p>

                <p
                  className="
                    mt-1
                    text-xs
                    leading-5
                    text-slate-600
                  "
                >
                  Deterministic hash of the compiled task policy.
                </p>
              </div>
            </div>

            <code
              className="
                tf-mono
                max-w-full
                break-all
                rounded-lg
                border border-white/[0.05]
                bg-black/20
                px-3 py-2
                text-[9px]
                leading-5
                text-slate-500
              "
            >
              {policyId}
            </code>
          </div>
        </div>

        <div
          className="
            mt-4
            rounded-xl
            border border-white/[0.05]
            bg-black/10
            p-4
          "
        >
          <p
            className="
              tf-mono
              text-[9px]
              uppercase
              tracking-[0.14em]
              text-slate-600
            "
          >
            Enforcement rule
          </p>

          <p
            className="
              mt-2
              text-xs
              leading-5
              text-slate-500
            "
          >
            Protected backend execution occurs only after ToolFence evaluates
            the requested capability and resource against the active policy and
            returns ALLOW.
          </p>
        </div>
      </div>
    </section>
  )
}
