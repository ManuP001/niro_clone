"use client";
import { useEffect } from "react";
import { useForm } from "react-hook-form";
import { useRouter } from "next/navigation";
import { MOCK_PRACTITIONER, TRADITIONS, LANGUAGES, TOPICS } from "@/lib/mock-data";
import { simulateDelay } from "@/lib/simulate";
import { useToast } from "@/components/ui/Toast";
import Button from "@/components/ui/Button";
import { useState } from "react";

interface SettingsForm {
  full_name: string;
  primary_tradition: string;
  languages: string[];
  years_of_practice: number;
  credential_education: string;
  city: string;
  philosophy: string;
  short_bio: string;
  typical_availability: string;
  max_sessions_per_week: number;
}

export default function SettingsPage() {
  const { showToast } = useToast();
  const router = useRouter();
  const [saving, setSaving] = useState(false);

  const { register, handleSubmit, setValue, watch } = useForm<SettingsForm>({
    defaultValues: {
      full_name: MOCK_PRACTITIONER.full_name,
      primary_tradition: MOCK_PRACTITIONER.primary_tradition,
      languages: MOCK_PRACTITIONER.languages,
      years_of_practice: MOCK_PRACTITIONER.years_of_practice,
      credential_education: MOCK_PRACTITIONER.credential_education ?? "",
      city: MOCK_PRACTITIONER.city,
      philosophy: MOCK_PRACTITIONER.philosophy,
      short_bio: MOCK_PRACTITIONER.short_bio,
      typical_availability: MOCK_PRACTITIONER.typical_availability ?? "",
      max_sessions_per_week: MOCK_PRACTITIONER.max_sessions_per_week,
    },
  });

  const selectedLanguages = watch("languages") ?? [];

  useEffect(() => {
    const saved = localStorage.getItem("niro_settings");
    if (saved) {
      const parsed = JSON.parse(saved) as SettingsForm;
      Object.entries(parsed).forEach(([k, v]) => setValue(k as keyof SettingsForm, v as never));
    }
  }, [setValue]);

  async function onSubmit(data: SettingsForm) {
    setSaving(true);
    await simulateDelay(800);
    localStorage.setItem("niro_settings", JSON.stringify(data));
    setSaving(false);
    showToast("Profile updated ✓");
  }

  const inputCls = "w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-violet-400 focus:ring-2 focus:ring-violet-100";
  const labelCls = "block text-sm font-medium text-gray-700 mb-1";

  function Section({ title, children }: { title: string; children: React.ReactNode }) {
    return (
      <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-6 mb-5">
        <h2 className="text-base font-semibold text-gray-900 mb-4 pb-3 border-b border-gray-100">{title}</h2>
        <div className="space-y-4">{children}</div>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Settings</h1>

      <Section title="Profile">
        <div className="grid grid-cols-2 gap-4">
          <div className="col-span-2">
            <label className={labelCls}>Full name</label>
            <input {...register("full_name")} className={inputCls} />
          </div>
          <div>
            <label className={labelCls}>Tradition</label>
            <select {...register("primary_tradition")} className={inputCls}>
              {TRADITIONS.map(t => <option key={t} value={t}>{t}</option>)}
            </select>
          </div>
          <div>
            <label className={labelCls}>City</label>
            <input {...register("city")} className={inputCls} />
          </div>
          <div>
            <label className={labelCls}>Years of practice</label>
            <input {...register("years_of_practice")} type="number" min={1} className={inputCls} />
          </div>
          <div>
            <label className={labelCls}>Credential</label>
            <input {...register("credential_education")} className={inputCls} />
          </div>
          <div className="col-span-2">
            <label className={labelCls}>Languages</label>
            <div className="grid grid-cols-4 gap-2">
              {LANGUAGES.map(lang => (
                <label key={lang} className="flex items-center gap-2 text-sm text-gray-700 cursor-pointer">
                  <input
                    type="checkbox"
                    value={lang}
                    checked={selectedLanguages.includes(lang)}
                    onChange={e => {
                      const next = e.target.checked ? [...selectedLanguages, lang] : selectedLanguages.filter((l: string) => l !== lang);
                      setValue("languages", next);
                    }}
                    className="rounded border-gray-300 text-violet-600"
                  />
                  {lang}
                </label>
              ))}
            </div>
          </div>
        </div>
      </Section>

      <Section title="Your Story">
        <div>
          <label className={labelCls}>Philosophy</label>
          <textarea {...register("philosophy")} rows={5} className={`${inputCls} resize-none`} />
        </div>
        <div>
          <label className={labelCls}>Short bio</label>
          <textarea {...register("short_bio")} rows={2} className={`${inputCls} resize-none`} />
        </div>
      </Section>

      <Section title="Availability">
        <div className="grid grid-cols-2 gap-4">
          <div className="col-span-2">
            <label className={labelCls}>Typical availability</label>
            <input {...register("typical_availability")} className={inputCls} />
          </div>
          <div>
            <label className={labelCls}>Max sessions / week</label>
            <input {...register("max_sessions_per_week")} type="number" min={1} max={20} className={inputCls} />
          </div>
        </div>
      </Section>

      <Section title="Packages">
        <p className="text-sm text-gray-400">Manage your packages from the <button onClick={() => router.push("/packages")} className="text-violet-600 underline">Packages page</button>.</p>
      </Section>

      <div className="flex justify-end">
        <Button size="lg" loading={saving} onClick={handleSubmit(onSubmit)}>Save Changes</Button>
      </div>
    </div>
  );
}
