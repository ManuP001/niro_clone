"use client";
import { useEffect, useState, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { MOCK_PACKAGES, TOPICS } from "@/lib/mock-data";
import { Package } from "@/lib/types";
import { simulateDelay } from "@/lib/simulate";
import { useToast } from "@/components/ui/Toast";
import Button from "@/components/ui/Button";

const INTRO_DEFAULT: Omit<Package, "id"> = {
  name: "Intro Clarity Call",
  who_its_for: "Someone exploring astrology for the first time",
  topic: "career",
  outcomes: ["A clear answer to your most pressing question", "One key timing window for the next 90 days", "A simple next step you can take immediately"],
  duration_days: 15,
  sessions_included: 1,
  price_inr: 499,
  is_intro_template: true,
};

const BLANK: Omit<Package, "id"> = {
  name: "",
  who_its_for: "",
  topic: "career",
  outcomes: ["", "", ""],
  duration_days: 30,
  sessions_included: 1,
  price_inr: 1500,
  is_intro_template: false,
};

function NewPackageForm() {
  const router = useRouter();
  const params = useSearchParams();
  const { showToast } = useToast();
  const isIntro = params.get("template") === "intro";
  const [form, setForm] = useState<Omit<Package, "id">>(isIntro ? INTRO_DEFAULT : BLANK);
  const [saving, setSaving] = useState(false);

  function update(field: keyof typeof form, val: unknown) {
    setForm(prev => ({ ...prev, [field]: val }));
  }

  function updateOutcome(idx: number, val: string) {
    const outcomes = [...form.outcomes] as [string, string, string];
    outcomes[idx] = val;
    setForm(prev => ({ ...prev, outcomes }));
  }

  async function save() {
    setSaving(true);
    await simulateDelay(800);
    const saved = localStorage.getItem("niro_packages");
    const existing: Package[] = saved ? JSON.parse(saved) : MOCK_PACKAGES;
    const newPkg = { ...form, id: `pkg_${Date.now()}` };
    localStorage.setItem("niro_packages", JSON.stringify([...existing, newPkg]));
    setSaving(false);
    showToast("Package saved ✓");
    router.push("/packages");
  }

  const inputCls = "w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-violet-400 focus:ring-2 focus:ring-violet-100";

  return (
    <div className="max-w-xl mx-auto">
      <div className="flex items-center gap-3 mb-6">
        <button onClick={() => router.push("/packages")} className="text-sm text-gray-400 hover:text-gray-600">← Back</button>
        <h1 className="text-2xl font-bold text-gray-900">New Package</h1>
      </div>
      <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-6 space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Package name *</label>
          <input value={form.name} onChange={e => update("name", e.target.value)} className={inputCls} />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Who it&apos;s for *</label>
          <input value={form.who_its_for} onChange={e => update("who_its_for", e.target.value)} className={inputCls} />
        </div>
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Price (₹)</label>
            <input type="number" value={form.price_inr} onChange={e => update("price_inr", Number(e.target.value))} className={inputCls} />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Topic</label>
            <select value={form.topic} onChange={e => update("topic", e.target.value)} className={inputCls}>
              {TOPICS.map(t => <option key={t.value} value={t.value}>{t.label}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Duration</label>
            <select value={form.duration_days} onChange={e => update("duration_days", Number(e.target.value))} className={inputCls}>
              {[15, 30, 60, 90].map(d => <option key={d} value={d}>{d} days</option>)}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Sessions</label>
            <select value={form.sessions_included} onChange={e => update("sessions_included", Number(e.target.value))} className={inputCls}>
              {[1, 2, 3, 4].map(n => <option key={n} value={n}>{n}</option>)}
            </select>
          </div>
        </div>
        {form.outcomes.map((out, i) => (
          <div key={i}>
            <label className="block text-sm font-medium text-gray-700 mb-1">Outcome {i + 1}</label>
            <input value={out} onChange={e => updateOutcome(i, e.target.value)} className={inputCls} />
          </div>
        ))}
        <Button className="w-full" loading={saving} onClick={save}>Save Package</Button>
      </div>
    </div>
  );
}

export default function NewPackagePage() {
  return (
    <Suspense>
      <NewPackageForm />
    </Suspense>
  );
}
