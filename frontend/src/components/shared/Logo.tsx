import { ShieldCheck } from "lucide-react"

type LogoProps = {
  compact?: boolean
}

export function Logo({
  compact = false,
}: LogoProps) {
  return (
    <div className="inline-flex items-center gap-3">
      <div
        className="
          flex h-9 w-9 items-center justify-center
          rounded-xl
          border border-blue-400/20
          bg-blue-500/10
          shadow-[0_0_30px_rgba(59,130,246,0.12)]
        "
      >
        <ShieldCheck
          className="h-5 w-5 text-blue-400"
          strokeWidth={1.8}
        />
      </div>

      {!compact && (
        <div className="flex flex-col leading-none">
          <span className="text-[15px] font-semibold tracking-tight text-white">
            ToolFence
          </span>

          <span className="tf-mono mt-1 text-[9px] tracking-[0.18em] text-slate-500">
            TASK-SCOPED SECURITY
          </span>
        </div>
      )}
    </div>
  )
}