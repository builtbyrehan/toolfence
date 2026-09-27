import type { ReactNode } from "react"

type SectionHeadingProps = {
  eyebrow?: string
  title: string
  description?: string
  action?: ReactNode
  className?: string
}

export function SectionHeading({
  eyebrow,
  title,
  description,
  action,
  className = "",
}: SectionHeadingProps) {
  return (
    <div
      className={`
        flex flex-col gap-4
        sm:flex-row
        sm:items-end
        sm:justify-between
        ${className}
      `}
    >
      <div className="max-w-3xl">
        {eyebrow && (
          <p
            className="
              tf-mono
              text-[10px]
              uppercase
              tracking-[0.16em]
              text-blue-400
            "
          >
            {eyebrow}
          </p>
        )}

        <h2
          className="
            mt-2
            text-2xl
            font-semibold
            tracking-[-0.03em]
            text-white
            sm:text-3xl
          "
        >
          {title}
        </h2>

        {description && (
          <p
            className="
              mt-3
              max-w-2xl
              text-sm
              leading-6
              text-slate-500
            "
          >
            {description}
          </p>
        )}
      </div>

      {action && (
        <div className="shrink-0">
          {action}
        </div>
      )}
    </div>
  )
}
