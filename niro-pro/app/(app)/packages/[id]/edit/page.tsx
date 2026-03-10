"use client";
import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { MOCK_PACKAGES, TOPICS } from "@/lib/mock-data";
import { Package } from "@/lib/types";
import { simulateDelay } from "@/lib/simulate";
import { useToast } from "@/components/ui/Toast";
import Button from "@/components/ui/Button";

export default function EditPackagePage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const { showToast } = useToast();
  const [form, setForm] = useState<Package | null>(null);
  const [saving, setSaving] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [confirmDelete, setConfirmDelete] = useState(false);

  useEffect(() => {
    const saved = localStorage.getItem("niro_packages");
    const all: Package[] = saved ? JSON.parse(saved) : MOCK_PACKAGES;
    const pkg = all.find(p => p.id === id) ?? MOCK_PACKAGES.find(p => p.id === id);
    if (pkg) setForm(pkg);
  }, [id]);

  function update(field: keyof Package, val: unknown) {
    setForm(prev => prev ? { ...prev, [field]: val } : prev);
  }

  function updateOutcome(idx: number, val: string) {
    if (!form) return;
    const outcomes = [...form.outcomes] as [string, string, string];
    outcomes[idx] = val;
    setForm(prev => prev ? { ...prev, outcomes } : prev);
  }

  async function save() {
    if (!form) return;
    setSaving(true);
    await simulateDelay(800);
    const saved = localStorage.getItem("niro_packages");
    const all: Package[] = saved ? JSON.parse(saved) : MOCK_PACKAGES;
    const updated = all.some(p => p.id === form.id) ? all.map(p => p.id === form.id ? form : p) : [...all, form];
    localStorage.setItem("niro_packages", JSON.stringify(updated));
    setSaving(false);
    showToast("Package saved ✓");
    router.push("/packages");
  }

  async function doDelete() {
    if (!form) return;
    setDeleting(true);
    await simulateDelay(500);
    const saved = localStorage.getItem("niro_packages");
    const all: Package[] = saved ? JSON.parse(saved) : MOCK_PACKAGES;
    localStorage.setItem("niro_packages", JSON.stringify(all.filter(p => p.id !== form.id)));
    showToast("Package removed", "info");
    router.push("/packages");
  }

  if (!form) return <div className="p-8 text-gray-400">Loading...</div>;

  const inputCls = "w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-violet-400 focus:ring-2 focus:ring-violet-100";

  return (
    <div className="max-w-xl mx-auto">
      <div className="flex items-center gap-3 mb-6">
        <button onClick={() => router.push("/packages")} className="text-sm text-gray-400 hover:text-gray-600">← Back</button>
        <h1 className="text-2xl font-bold text-gray-900">Edit Package</h1>
      </div>
      <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-6 space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Package name</label>
          <input value={form.name} onChange={e => update("name", e.target.value)} className={inputCls} />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Who it&apos;s for</label>
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
        <div className="flex gap-3 pt-2">
          <Button className="flex-1" loading={saving} onClick={save}>Save Changes</Button>
          <Button variant="danger" onClick={() => setConfirmDelete(true)}>Delete</Button>
        </div>
      </div>

      {confirmDelete && (
        <div className="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-xl p-6 max-w-sm w-full shadow-xl">
            <h3 className="font-semibold text-gray-900 mb-2">Delete this package?</h3>
            <p className="text-sm text-gray-400 mb-5">This can&apos;t be undone.</p>
            <div className="flex gap-3">
              <Button variant="secondary" className="flex-1" onClick={() => setConfirmDelete(false)}>Cancel</Button>
              <Button variant="danger" className="flex-1" loading={deleting} onClick={doDelete}>Delete</Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
