"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { MOCK_PACKAGES } from "@/lib/mock-data";
import { Package } from "@/lib/types";
import Badge from "@/components/ui/Badge";
import Button from "@/components/ui/Button";
import { formatCurrency } from "@/lib/utils";
import { Plus, Pencil } from "lucide-react";

export default function PackagesPage() {
  const router = useRouter();
  const [packages, setPackages] = useState<Package[]>(MOCK_PACKAGES);

  useEffect(() => {
    const saved = localStorage.getItem("niro_packages");
    if (saved) setPackages(JSON.parse(saved));
  }, []);

  const hasIntro = packages.some(p => p.price_inr < 1000);

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Packages</h1>
        <Button onClick={() => router.push("/packages/new")} size="sm">
          <Plus className="w-4 h-4" /> Add Package
        </Button>
      </div>

      {!hasIntro && (
        <div className="bg-blue-50 border border-blue-200 rounded-xl px-5 py-3 mb-5 flex items-center justify-between">
          <p className="text-sm text-blue-700">Add an Intro Session at ₹499 — first-time clients convert 3× better</p>
          <button onClick={() => router.push("/packages/new?template=intro")} className="text-sm font-semibold text-blue-600 hover:text-blue-800 ml-4 shrink-0">
            Add Intro Template →
          </button>
        </div>
      )}

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {packages.map(pkg => (
          <div key={pkg.id} className="bg-white rounded-xl border border-gray-100 shadow-sm p-5">
            <div className="flex items-start justify-between mb-3">
              <div className="flex-1 min-w-0">
                <p className="font-semibold text-gray-900 truncate">{pkg.name}</p>
                <p className="text-xs text-gray-400 mt-0.5">{pkg.sessions_included} session · {pkg.duration_days} days</p>
              </div>
              <button onClick={() => router.push(`/packages/${pkg.id}/edit`)} className="ml-2 p-1.5 text-gray-300 hover:text-violet-600 rounded-lg hover:bg-violet-50">
                <Pencil className="w-3.5 h-3.5" />
              </button>
            </div>
            <Badge topic={pkg.topic} size="sm" className="mb-3" />
            <p className="text-2xl font-bold text-gray-900">{formatCurrency(pkg.price_inr)}</p>
            <p className="text-xs text-gray-400 mt-1 line-clamp-2">{pkg.who_its_for}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
