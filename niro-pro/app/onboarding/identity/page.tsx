"use client";
import { useEffect } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useRouter } from "next/navigation";
import OnboardingLayout from "@/components/onboarding/OnboardingLayout";
import { MOCK_PRACTITIONER, TRADITIONS, LANGUAGES } from "@/lib/mock-data";
import { IdentityForm } from "@/lib/types";

const schema = z.object({
  full_name: z.string().min(2, "Required"),
  primary_tradition: z.string().min(1, "Required"),
  languages: z.array(z.string()).min(1, "Select at least one language"),
  years_of_practice: z.coerce.number().min(1, "Required"),
  credential_education: z.string().optional(),
  city: z.string().min(1, "Required"),
});

type SchemaForm = z.infer<typeof schema>;

export default function IdentityPage() {
  const router = useRouter();
  const { register, handleSubmit, setValue, watch, formState: { errors } } = useForm<SchemaForm>({
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    resolver: zodResolver(schema) as any,
    defaultValues: {
      full_name: MOCK_PRACTITIONER.full_name,
      primary_tradition: MOCK_PRACTITIONER.primary_tradition,
      languages: MOCK_PRACTITIONER.languages,
      years_of_practice: MOCK_PRACTITIONER.years_of_practice,
      credential_education: MOCK_PRACTITIONER.credential_education,
      city: MOCK_PRACTITIONER.city,
    },
  });

  const selectedLanguages = watch("languages") ?? [];

  useEffect(() => {
    const saved = localStorage.getItem("niro_onboarding_identity");
    if (saved) {
      const parsed = JSON.parse(saved) as SchemaForm;
      Object.entries(parsed).forEach(([k, v]) => setValue(k as keyof SchemaForm, v as never));
    }
  }, [setValue]);

  function onSubmit(data: SchemaForm) {
    localStorage.setItem("niro_onboarding_identity", JSON.stringify(data));
    router.push("/onboarding/story");
  }

  const inputCls = "w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-violet-400 focus:ring-2 focus:ring-violet-100";
  const labelCls = "block text-sm font-medium text-gray-700 mb-1";
  const errCls = "text-red-500 text-xs mt-1";

  return (
    <OnboardingLayout step={1} totalSteps={6} percent={17} backHref="/onboarding/welcome" onContinue={handleSubmit(onSubmit)}>
      <h2 className="text-2xl font-bold text-gray-900 mb-1">About you</h2>
      <p className="text-gray-400 text-sm mb-6">This is what clients see on your profile.</p>
      <div className="space-y-5">
        <div>
          <label className={labelCls}>Full name *</label>
          <input {...register("full_name")} className={inputCls} />
          {errors.full_name && <p className={errCls}>{errors.full_name.message}</p>}
        </div>
        <div>
          <label className={labelCls}>Primary tradition *</label>
          <select {...register("primary_tradition")} className={inputCls}>
            <option value="">Select...</option>
            {TRADITIONS.map(t => <option key={t} value={t}>{t}</option>)}
          </select>
          {errors.primary_tradition && <p className={errCls}>{errors.primary_tradition.message}</p>}
        </div>
        <div>
          <label className={labelCls}>Languages *</label>
          <div className="grid grid-cols-2 gap-2">
            {LANGUAGES.map(lang => (
              <label key={lang} className="flex items-center gap-2 text-sm text-gray-700 cursor-pointer">
                <input
                  type="checkbox"
                  value={lang}
                  checked={selectedLanguages.includes(lang)}
                  onChange={e => {
                    const next = e.target.checked
                      ? [...selectedLanguages, lang]
                      : selectedLanguages.filter((l: string) => l !== lang);
                    setValue("languages", next as string[], { shouldValidate: true });
                  }}
                  className="rounded border-gray-300 text-violet-600"
                />
                {lang}
              </label>
            ))}
          </div>
          {errors.languages && <p className={errCls}>{errors.languages.message}</p>}
        </div>
        <div>
          <label className={labelCls}>Years of practice *</label>
          <input {...register("years_of_practice")} type="number" min={1} className={inputCls} />
          {errors.years_of_practice && <p className={errCls}>{errors.years_of_practice.message}</p>}
        </div>
        <div>
          <label className={labelCls}>Credential / Education <span className="text-gray-400 font-normal">(optional)</span></label>
          <input {...register("credential_education")} className={inputCls} placeholder="e.g. Jyotish Visharad, BVB 2012" />
        </div>
        <div>
          <label className={labelCls}>City *</label>
          <input {...register("city")} className={inputCls} />
          {errors.city && <p className={errCls}>{errors.city.message}</p>}
        </div>
      </div>
    </OnboardingLayout>
  );
}
