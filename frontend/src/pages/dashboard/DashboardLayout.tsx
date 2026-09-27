import { Outlet } from "react-router-dom"

import { DashboardHeader } from "@/components/dashboard/DashboardHeader"
import { DashboardSidebar } from "@/components/dashboard/DashboardSidebar"
import { useDashboardData } from "@/hooks/useDashboardData"


export type DashboardContextValue =
  ReturnType<typeof useDashboardData>


export function DashboardLayout() {
  const dashboard = useDashboardData()

  const {
    task,
    policy,
    isLoading,
    isError,
    error,
    isFetching,
    refetchAll,
  } = dashboard

  if (isLoading) {
    return (
      <main className="tf-page min-h-screen">
        <div className="flex min-h-screen">
          <DashboardSidebar />

          <div className="min-w-0 flex-1">
            <div
              className="
                flex min-h-screen
                items-center justify-center
                px-6
              "
            >
              <div
                className="
                  rounded-2xl
                  border border-white/[0.06]
                  bg-white/[0.025]
                  px-8 py-7
                  text-center
                "
              >
                <div
                  className="
                    mx-auto
                    h-8 w-8
                    animate-spin
                    rounded-full
                    border-2
                    border-white/[0.08]
                    border-t-blue-400
                  "
                />

                <p
                  className="
                    mt-4
                    text-sm font-medium
                    text-slate-300
                  "
                >
                  Loading ToolFence runtime…
                </p>

                <p
                  className="
                    mt-2
                    text-xs
                    text-slate-600
                  "
                >
                  Reading policy, capability, audit, and benchmark data.
                </p>
              </div>
            </div>
          </div>
        </div>
      </main>
    )
  }

  if (
    isError ||
    !task ||
    !policy
  ) {
    const message =
      error instanceof Error
        ? error.message
        : "Unable to load ToolFence dashboard data."

    return (
      <main className="tf-page min-h-screen">
        <div className="flex min-h-screen">
          <DashboardSidebar />

          <div className="min-w-0 flex-1">
            <div
              className="
                flex min-h-screen
                items-center justify-center
                px-6
              "
            >
              <div
                className="
                  w-full
                  max-w-lg
                  rounded-2xl
                  border border-red-500/20
                  bg-red-500/[0.035]
                  p-7
                "
              >
                <p
                  className="
                    text-sm font-semibold
                    text-red-300
                  "
                >
                  Dashboard data unavailable
                </p>

                <p
                  className="
                    mt-2
                    text-sm
                    leading-6
                    text-slate-400
                  "
                >
                  {message}
                </p>

                <button
                  type="button"
                  disabled={isFetching}
                  onClick={() => {
                    void refetchAll()
                  }}
                  className="
                    mt-5
                    rounded-lg
                    border border-white/10
                    bg-white/[0.04]
                    px-4 py-2
                    text-xs font-medium
                    text-slate-300
                    transition
                    hover:bg-white/[0.07]
                    disabled:cursor-wait
                    disabled:opacity-50
                  "
                >
                  {isFetching
                    ? "Retrying…"
                    : "Retry"}
                </button>
              </div>
            </div>
          </div>
        </div>
      </main>
    )
  }

  return (
    <main className="tf-page min-h-screen">
      <div className="flex min-h-screen">
        <DashboardSidebar />

        <div className="min-w-0 flex-1">
          <DashboardHeader
            taskId={task.taskId}
            policyStatus={policy.status}
          />

          <div
            className="
              mx-auto
              w-full
              max-w-[1600px]
              p-4
              sm:p-6
              xl:p-7
            "
          >
            <Outlet
              context={dashboard}
            />

            <div
              className="
                mt-8
                mb-6
                flex flex-col gap-3
                rounded-xl
                border border-white/[0.05]
                bg-white/[0.015]
                px-4 py-3
                sm:flex-row
                sm:items-center
                sm:justify-between
              "
            >
              <p
                className="
                  text-xs
                  leading-5
                  text-slate-600
                "
              >
                Live dashboard data is read from the ToolFence FastAPI
                observability bridge. Authorization continues to use the
                trusted in-memory policy store.
              </p>

              <button
                type="button"
                disabled={isFetching}
                onClick={() => {
                  void refetchAll()
                }}
                className="
                  shrink-0
                  rounded-lg
                  border border-white/[0.07]
                  bg-white/[0.025]
                  px-3 py-2
                  text-xs font-medium
                  text-slate-400
                  transition
                  hover:bg-white/[0.05]
                  hover:text-slate-200
                  disabled:cursor-wait
                  disabled:opacity-50
                "
              >
                {isFetching
                  ? "Refreshing…"
                  : "Refresh data"}
              </button>
            </div>
          </div>
        </div>
      </div>
    </main>
  )
}
