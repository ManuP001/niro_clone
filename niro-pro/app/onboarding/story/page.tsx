"use client";
import { useEffect } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useRouter } from "next/navigation";
import OnboardingLayout from "@/components/onboarding/OnboardingLayout";
import { MOCK_PRACTITIONER } from "@/lib/mock-data";
import { StoryForm } from "@/lib/types";
import { getWordCount } from "@/lib/utils";

const schema = z.object({
  philosophy: z.string().refine(v => { const w = getWordCount(v); return w >= 80 && w <= 200; }, "Must be 80–200 words"),
  short_bio: z.string().min(50, "Min 50 characters").max(300, "Max 300 characters"),
});

export default function StoryPage() {
  const router = useRouter();
  const { register, handleSubmit, watch, setValue, formState: { errors } } = useForm<StoryForm>({
    resolver: zodResolver(schema),
    defaultValues: {
      philosophy: MOCK_PRACTITIONER.philosophy,
      short_bio: MOCK_PRACTITIONER.short_bio,
    },
  });

  const philosophy = watch("philosophy") ?? "";
  const short_bio = watch("short_bio") ?? "";
  const wordCount = getWordCount(philosophy);
  const bioLen = short_bio.length;

  useEffect(() => {
    const saved = localStorage.getItem("niro_onboarding_story");
    if (saved) {
      const parsed = JSON.parse(saved) as StoryForm;
      setValue("philosophy", parsed.philosophy);
      setValue("short_bio", parsed.short_bio);
    }
  }, [setValue]);

  function onSubmit(data: StoryForm) {
    localStorage.setItem("niro_onboarding_story", JSON.stringify(data));
    router.push("/onboarding/specializations");
  }

  const inputCls = "w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-violet-400 focus:ring-2 focus:ring-violet-100 resize-none";

  return (
    <OnboardingLayout step={2} totalSteps={6} percent={33} backHref="/onboarding/identity" onContinue={handleSubmit(onSubmit)}>
      <h2 className="text-2xl font-bold text-gray-900 mb-1">Your story</h2>
      <p className="text-gray-400 text-sm mb-6">This is your voice. Clients read this before they book.</p>
      <div className="space-y-6">
        <div>
          <div className="flex justify-between mb-1">
            <label className="text-sm font-medium text-gray-700">Philosophy *</label>
            <span className={`text-xs font-medium ${wordCount >= 80 && wordCount <= 200 ? "text-emerald-600" : "text-red-500"}`}>
              {wordCount} words {wordCount >= 80 && wordCount <= 200 ? "✓" : "(80–200 required)"}
            </span>
          </div>
          <textarea {...register("philosophy")} rows={7} className={inputCls} />
          {errors.philosophy && <p className="text-red-500 text-xs mt-1">{errors.philosophy.message}</p>}
        </div>
        <div>
          <div className="flex justify-between mb-1">
            <label className="text-sm font-medium text-gray-700">Short bio *</label>
            <span className={`text-xs font-medium ${bioLen >= 50 && bioLen <= 300 ? "text-emerald-600" : "text-red-500"}`}>
              {bioLen} / 300
            </span>
          </div>
          <textarea {...register("short_bio")} rows={3} className={inputCls} />
          {errors.short_bio && <p className="text-red-500 text-xs mt-1">{errors.short_bio.message}</p>}
        </div>
      </div>
    </OnboardingLayout>
  );
}
