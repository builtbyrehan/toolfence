import {
  lazy,
  Suspense,
  type ReactNode,
} from "react"
import { createBrowserRouter } from "react-router-dom"

const LandingPage = lazy(async () => {
  const module = await import("@/pages/landing/LandingPage")

  return {
    default: module.LandingPage,
  }
})

const DashboardLayout = lazy(async () => {
  const module = await import("@/pages/dashboard/DashboardLayout")

  return {
    default: module.DashboardLayout,
  }
})

const OverviewPage = lazy(async () => {
  const module = await import("@/pages/dashboard/OverviewPage")

  return {
    default: module.OverviewPage,
  }
})

const PolicyPage = lazy(async () => {
  const module = await import("@/pages/dashboard/PolicyPage")

  return {
    default: module.PolicyPage,
  }
})

const ActivityPage = lazy(async () => {
  const module = await import("@/pages/dashboard/ActivityPage")

  return {
    default: module.ActivityPage,
  }
})

const AuditPage = lazy(async () => {
  const module = await import("@/pages/dashboard/AuditPage")

  return {
    default: module.AuditPage,
  }
})

const BenchmarkPage = lazy(async () => {
  const module = await import("@/pages/dashboard/BenchmarkPage")

  return {
    default: module.BenchmarkPage,
  }
})

function RouteFallback() {
  return (
    <main
      className="
        tf-page
        flex min-h-screen
        items-center justify-center
      "
    >
      <div className="text-center">
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
            tf-mono
            mt-4
            text-[10px]
            uppercase
            tracking-[0.16em]
            text-slate-600
          "
        >
          Loading ToolFence
        </p>
      </div>
    </main>
  )
}

function LazyRoute({
  children,
}: {
  children: ReactNode
}) {
  return (
    <Suspense fallback={<RouteFallback />}>
      {children}
    </Suspense>
  )
}

export const router = createBrowserRouter([
  {
    path: "/",
    element: (
      <LazyRoute>
        <LandingPage />
      </LazyRoute>
    ),
  },

  {
    path: "/dashboard",
    element: (
      <LazyRoute>
        <DashboardLayout />
      </LazyRoute>
    ),
    children: [
      {
        index: true,
        element: (
          <LazyRoute>
            <OverviewPage />
          </LazyRoute>
        ),
      },
      {
        path: "policy",
        element: (
          <LazyRoute>
            <PolicyPage />
          </LazyRoute>
        ),
      },
      {
        path: "activity",
        element: (
          <LazyRoute>
            <ActivityPage />
          </LazyRoute>
        ),
      },
      {
        path: "audit",
        element: (
          <LazyRoute>
            <AuditPage />
          </LazyRoute>
        ),
      },
      {
        path: "benchmark",
        element: (
          <LazyRoute>
            <BenchmarkPage />
          </LazyRoute>
        ),
      },
    ],
  },
])
