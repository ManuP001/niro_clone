"use client";
import { useRouter } from "next/navigation";
import ProgressBar from "@/components/ui/ProgressBar";
import Button from "@/components/ui/Button";
import { ReactNode } from "react";

interface OnboardingLayoutProps {
  children: ReactNode;
  step: number;
  totalSteps: number;
  percent: number;
  backHref?: string;
  onContinue?: () => void;
  continueLabel?: string;
  continueLoading?: boolean;
  hideContinue?: boolean;
}

export default function OnboardingLayout({
  children, step, totalSteps, percent, backHref,
  onContinue, continueLabel = "Continue →", continueLoading, hideContinue
}: OnboardingLayoutProps) {
  const router = useRouter();
  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <header className="bg-white border-b border-gray-100 px-6 py-4">
        <div className="max-w-2xl mx-auto">
          <p className="text-[#1E1B4B] font-bold text-lg mb-3">NIRO ✦</p>
          <ProgressBar percent={percent} step={step} totalSteps={totalSteps} />
        </div>
      </header>
      <main className="flex-1 max-w-2xl mx-auto w-full px-4 py-8">
        {children}
      </main>
      {!hideContinue && (
        <footer className="bg-white border-t border-gray-100 px-6 py-4">
          <div className="max-w-2xl mx-auto flex items-center justify-between">
            {backHref ? (
              <Button variant="ghost" onClick={() => router.push(backHref)}>← Back</Button>
            ) : <div />}
            <Button onClick={onContinue} loading={continueLoading} size="lg">{continueLabel}</Button>
          </div>
        </footer>
      )}
    </div>
  );
}
