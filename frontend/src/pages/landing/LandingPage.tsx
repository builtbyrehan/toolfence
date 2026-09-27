import { ArchitectureSection } from "@/components/landing/ArchitectureSection"
import { BenchmarkSection } from "@/components/landing/BenchmarkSection"
import { CapabilityBoundary } from "@/components/landing/CapabilityBoundary"
import { CTASection } from "@/components/landing/CTASection"
import { Hero } from "@/components/landing/Hero"
import { HowItWorks } from "@/components/landing/HowItWorks"
import { ProblemSection } from "@/components/landing/ProblemSection"
import { SecurityDemo } from "@/components/landing/SecurityDemo"
import { Footer } from "@/components/shared/Footer"
import { Navbar } from "@/components/shared/Navbar"

export function LandingPage() {
  return (
    <main className="tf-page min-h-screen overflow-x-hidden">
      <Navbar />

      <Hero />

      <ProblemSection />

      <CapabilityBoundary />

      <HowItWorks />

      <SecurityDemo />

      <ArchitectureSection />

      <BenchmarkSection />

      <CTASection />

      <Footer />
    </main>
  )
}
