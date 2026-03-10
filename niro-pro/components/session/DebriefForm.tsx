"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { simulateDelay } from "@/lib/simulate";
import { useToast } from "@/components/ui/Toast";
import Button from "@/components/ui/Button";

const QUESTIONS = [
  { q: "Did you complete Phase 01 (opening + past observation)?", options: ["Yes", "Partial", "No"] },
  { q: "Did you complete Phase 03 (the invite deeper)?", options: ["Yes", "Partial", "No"] },
  { q: "Did you send a package offer?", options: ["Yes", "No"] },
  { q: "What price did you offer?", type: "number" },
  { q: "How did the client respond?", options: ["Interested", "Not now", "Has an astrologer", "No response"] },
  { q: "One thing you'd do differently? (optional)", type: "textarea" },
];

export default function DebriefForm() {
  const router = useRouter();
  const { showToast } = useToast();
  const [step, setStep] = useState(0);
  const [answers, setAnswers] = useState<Record<number, string>>({});
  const [submitting, setSubmitting] = useState(false);

  const current = QUESTIONS[step];
  // Skip price question if offer wasn't sent
  const effectiveStep = step === 3 && answers[2] === "No" ? 4 : step;
  const q = QUESTIONS[effectiveStep];

  async function handleSubmit() {
    setSubmitting(true);
    await simulateDelay(500);
    showToast("Debrief saved ✓");
    router.push("/dashboard");
  }

  function next(val: string) {
    const newAnswers = { ...answers, [effectiveStep]: val };
    setAnswers(newAnswers);
    if (effectiveStep === 3 && answers[2] === "No") {
      setStep(4);
    } else if (effectiveStep >= QUESTIONS.length - 1) {
      handleSubmit();
    } else {
      setStep(effectiveStep + 1);
    }
  }

  return (
    <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-5">
      <div className="flex items-center justify-between mb-1">
        <h3 className="font-semibold text-gray-900 text-sm">Session debrief</h3>
        <span className="text-xs text-gray-400">Question {effectiveStep + 1} of {QUESTIONS.length}</span>
      </div>
      <div className="h-1 bg-gray-100 rounded-full mb-4">
        <div className="h-1 bg-violet-500 rounded-full transition-all" style={{ width: `${((effectiveStep) / QUESTIONS.length) * 100}%` }} />
      </div>

      <p className="text-sm font-medium text-gray-900 mb-4">{q.q}</p>

      {q.options && (
        <div className="space-y-2">
          {q.options.map(opt => (
            <button
              key={opt}
              onClick={() => next(opt)}
              className="w-full text-left px-4 py-2.5 rounded-lg border border-gray-200 text-sm text-gray-700 hover:border-violet-300 hover:bg-violet-50 transition-colors"
            >
              {opt}
            </button>
          ))}
        </div>
      )}
      {q.type === "number" && (
        <div className="flex gap-3">
          <input
            type="number"
            placeholder="₹ Amount"
            className="flex-1 border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-violet-400"
            onKeyDown={e => e.key === "Enter" && next((e.target as HTMLInputElement).value)}
          />
          <Button size="sm" onClick={e => {
            const input = (e.currentTarget.previousSibling as HTMLInputElement);
            next(input.value);
          }}>Next</Button>
        </div>
      )}
      {q.type === "textarea" && (
        <div className="space-y-3">
          <textarea
            className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-violet-400 resize-none"
            rows={3}
            placeholder="Optional..."
          />
          <Button
            className="w-full"
            loading={submitting}
            onClick={e => next((e.currentTarget.previousSibling as HTMLTextAreaElement).value)}
          >
            Submit Debrief
          </Button>
        </div>
      )}
    </div>
  );
}
