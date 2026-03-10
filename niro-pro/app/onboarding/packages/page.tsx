"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import OnboardingLayout from "@/components/onboarding/OnboardingLayout";
import { MOCK_PACKAGES, TOPICS } from "@/lib/mock-data";
import { Package } from "@/lib/types";
import { Trash2, Plus } from "lucide-react";

const INTRO_TEMPLATE: Omit<Package, "id"> = {
  name: "Intro Clarity Call",
  who_its_for: "Someone exploring astrology for the first time",
  topic: "career",
  outcomes: ["A clear answer to your most pressing question", "One key timing window for the next 90 days", "A simple next step you can take immediately"],
  duration_days: 15,
  sessions_included: 1,
  price_inr: 499,
  is_intro_template: true,
};

export default function PackagesPage() {
  const router = useRouter();
  const [packages, setPackages] = useState<Package[]>(MOCK_PACKAGES);

  useEffect(() => {
    const saved = localStorage.getItem("niro_onboarding_packages");
    if (saved) setPackages(JSON.parse(saved));
  }, []);

  function save() {
    localStorage.setItem("niro_onboarding_packages", JSON.stringify(packages));
    router.push("/onboarding/photos");
  }

  function update(id: string, field: keyof Package, value: unknown) {
    setPackages(prev => prev.map(p => p.id === id ? { ...p, [field]: value } : p));
  }

  function updateOutcome(id: string, idx: number, value: string) {
    setPackages(prev => prev.map(p => {
      if (p.id !== id) return p;
      const outcomes = [...p.outcomes] as [string, string, string];
      outcomes[idx] = value;
      return { ...p, outcomes };
    }));
  }

  function addPackage() {
    if (packages.length >= 4) return;
    setPackages(prev => [...prev, { ...INTRO_TEMPLATE, id: `pkg_${Date.now()}`, is_intro_template: false }]);
  }

  function addIntroTemplate() {
    setPackages(prev => [...prev, { ...INTRO_TEMPLATE, id: `pkg_${Date.now()}` }]);
  }

  function remove(id: string) {
    if (packages.length <= 1) return;
    setPackages(prev => prev.filter(p => p.id !== id));
  }

  const hasIntro = packages.some(p => p.price_inr < 1000);
  const inputCls = "w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-violet-400 focus:ring-2 focus:ring-violet-100";

  return (
    <OnboardingLayout step={4} totalSteps={6} percent={67} backHref="/onboarding/specializations" onContinue={save}>
      <h2 className="text-2xl font-bold text-gray-900 mb-1">Your packages</h2>
      <p className="text-gray-400 text-sm mb-4">Define what clients can book. At least 1, max 4.</p>

      {!hasIntro && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg px-4 py-3 mb-4 flex items-center justify-between">
          <p className="text-sm text-blue-700">Add an Intro Session at ₹499 — first-time clients convert 3× better</p>
          <button onClick={addIntroTemplate} className="text-sm font-medium text-blue-600 hover:text-blue-800 ml-3 shrink-0">+ Add Template</button>
        </div>
      )}

      <div className="space-y-4">
        {packages.map((pkg, i) => (
          <div key={pkg.id} className="bg-white border border-gray-200 rounded-xl p-4">
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-semibold text-gray-400 uppercase tracking-wide">Package {i + 1}</span>
              {packages.length > 1 && (
                <button onClick={() => remove(pkg.id)} className="text-gray-300 hover:text-red-500">
                  <Trash2 className="w-4 h-4" />
                </button>
              )}
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div className="sm:col-span-2">
                <label className="block text-xs font-medium text-gray-500 mb-1">Package name</label>
                <input value={pkg.name} onChange={e => update(pkg.id, "name", e.target.value)} className={inputCls} />
              </div>
              <div className="sm:col-span-2">
                <label className="block text-xs font-medium text-gray-500 mb-1">Who it&apos;s for</label>
                <input value={pkg.who_its_for} onChange={e => update(pkg.id, "who_its_for", e.target.value)} className={inputCls} />
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-500 mb-1">Price (₹)</label>
                <input type="number" value={pkg.price_inr} onChange={e => update(pkg.id, "price_inr", Number(e.target.value))} className={inputCls} />
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-500 mb-1">Topic</label>
                <select value={pkg.topic} onChange={e => update(pkg.id, "topic", e.target.value)} className={inputCls}>
                  {TOPICS.map(t => <option key={t.value} value={t.value}>{t.label}</option>)}
                </select>
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-500 mb-1">Duration (days)</label>
                <select value={pkg.duration_days} onChange={e => update(pkg.id, "duration_days", Number(e.target.value))} className={inputCls}>
                  {[15, 30, 60, 90].map(d => <option key={d} value={d}>{d} days</option>)}
                </select>
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-500 mb-1">Sessions included</label>
                <select value={pkg.sessions_included} onChange={e => update(pkg.id, "sessions_included", Number(e.target.value))} className={inputCls}>
                  {[1, 2, 3, 4].map(n => <option key={n} value={n}>{n}</option>)}
                </select>
              </div>
              {pkg.outcomes.map((out, idx) => (
                <div key={idx} className="sm:col-span-2">
                  <label className="block text-xs font-medium text-gray-500 mb-1">Outcome {idx + 1}</label>
                  <input value={out} onChange={e => updateOutcome(pkg.id, idx, e.target.value)} className={inputCls} />
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>

      {packages.length < 4 && (
        <button onClick={addPackage} className="mt-4 flex items-center gap-2 text-sm text-violet-600 hover:text-violet-700 font-medium">
          <Plus className="w-4 h-4" /> Add another package
        </button>
      )}
    </OnboardingLayout>
  );
}
