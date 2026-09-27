type StatusBadgeProps = {
  status:
    | "ACTIVE"
    | "ALLOW"
    | "DENY"
    | "PASSED"
    | "FAILED"
    | "COMPLETED"
    | "REVOKED"
    | "EXPIRED"
    | "PENDING"
  className?: string
}

export function StatusBadge({
  status,
  className = "",
}: StatusBadgeProps) {
  const normalized =
    status.toUpperCase()

  const tone = getTone(normalized)

  return (
    <span
      className={`
        inline-flex
        items-center gap-1.5
        rounded-md
        border
        px-2 py-1
        tf-mono
        text-[8px]
        uppercase
        tracking-[0.08em]
        ${tone.container}
        ${className}
      `}
    >
      <span
        className={`
          h-1.5 w-1.5
          rounded-full
          ${tone.dot}
        `}
      />

      {normalized}
    </span>
  )
}

function getTone(
  status: string,
) {
  if (
    status === "ACTIVE" ||
    status === "ALLOW" ||
    status === "PASSED" ||
    status === "COMPLETED"
  ) {
    return {
      container:
        "border-emerald-400/10 bg-emerald-400/[0.04] text-emerald-400",
      dot:
        "bg-emerald-400",
    }
  }

  if (
    status === "DENY" ||
    status === "FAILED" ||
    status === "REVOKED" ||
    status === "EXPIRED"
  ) {
    return {
      container:
        "border-red-400/10 bg-red-400/[0.04] text-red-400",
      dot:
        "bg-red-400",
    }
  }

  return {
    container:
      "border-amber-400/10 bg-amber-400/[0.04] text-amber-400",
    dot:
      "bg-amber-400",
  }
}
