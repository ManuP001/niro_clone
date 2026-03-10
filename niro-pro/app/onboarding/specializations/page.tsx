"use client";
import { useEffect } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useRouter } from "next/navigation";
import OnboardingLayout from "@/components/onboarding/OnboardingLayout";
import { MOCK_PRACTITIONER, TOPICS } from "@/lib/mock-data";
import { SpecializationsForm } from "@/lib/types";

const schema = z.object({
  primary_topic: z.string().min(1, "Required"),
  secondary_topics: z.array(z.string()).max(3, "Max 3"),
  typical_availability: z.string().optional(),
  max_sessions_per_week: z.coerce.number().min(1).max(20),
});

type SchemaForm = z.infer<typeof schema>;

export default function SpecializationsPage() {
  const router = useRouter();
  const { register, handleSubmit, watch, setValue, formState: { errors } } = useForm<SchemaForm>({
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    resolver: zodResolver(schema) as any,
    defaultValues: {
      primary_topic: MOCK_PRACTITIONER.primary_topic,
      secondary_topics: MOCK_PRACTITIONER.secondary_topics,
      typical_availability: MOCK_PRACTITIONER.typical_availability,
      max_sessions_per_week: MOCK_PRACTITIONER.max_sessions_per_week,
    },
  });

  const primaryTopic = watch("primary_topic");
  const secondaryTopics = watch("secondary_topics") ?? [];

  useEffect(() => {
    const saved = localStorage.getItem("niro_onboarding_specializations");
    if (saved) {
      const parsed = JSON.parse(saved) as SchemaForm;
      Object.entries(parsed).forEach(([k, v]) => setValue(k as keyof SchemaForm, v as never));
    }
  }, [setValue]);

  function onSubmit(data: SchemaForm) {
    localStorage.setItem("niro_onboarding_specializations", JSON.stringify(data));
    router.push("/onboarding/packages");
  }

  const inputCls = "w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-violet-400 focus:ring-2 focus:ring-violet-100";

  return (
    <OnboardingLayout step={3} totalSteps={6} percent={50} backHref="/onboarding/story" onContinue={handleSubmit(onSubmit)}>
      <h2 className="text-2xl font-bold text-gray-900 mb-1">Your specializations</h2>
      <p className="text-gray-400 text-sm mb-6">Tell us what you focus on and when you&apos;re available.</p>
      <div className="space-y-5">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Primary topic *</label>
          <select {...register("primary_topic")} className={inputCls}>
            {TOPICS.map(t => <option key={t.value} value={t.value}>{t.label}</option>)}
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Secondary topics <span className="text-gray-400 font-normal">(max 3)</span></label>
          <div className="grid grid-cols-2 gap-2">
            {TOPICS.filter(t => t.value !== primaryTopic).map(t => {
              const checked = secondaryTopics.includes(t.value);
              const disabled = !checked && secondaryTopics.length >= 3;
              return (
                <label key={t.value} className={`flex items-center gap-2 text-sm cursor-pointer ${disabled ? "opacity-40" : "text-gray-700"}`}>
                  <input
                    type="checkbox"
                    value={t.value}
                    checked={checked}
                    disabled={disabled}
                    onChange={e => {
                      const next = e.target.checked
                        ? [...secondaryTopics, t.value]
                        : secondaryTopics.filter((x: string) => x !== t.value);
                      setValue("secondary_topics", next as string[]);
                    }}
                    className="rounded border-gray-300 text-violet-600"
                  />
                  {t.label}
                </label>
              );
            })}
          </div>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Typical availability <span className="text-gray-400 font-normal">(optional)</span></label>
          <input {...register("typical_availability")} className={inputCls} placeholder="e.g. Weekday evenings 7–10pm" />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Max sessions per week *</label>
          <input {...register("max_sessions_per_week")} type="number" min={1} max={20} className={inputCls} />
          {errors.max_sessions_per_week && <p className="text-red-500 text-xs mt-1">{errors.max_sessions_per_week.message}</p>}
        </div>
      </div>
    </OnboardingLayout>
  );
}
