"use client";
import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { MOCK_SESSION, MOCK_PACKAGES } from "@/lib/mock-data";
import Badge from "@/components/ui/Badge";
import Button from "@/components/ui/Button";

export default function PrepPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const session = MOCK_SESSION;
  const [countdown, setCountdown] = useState(60);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    const t = setInterval(() => {
      setCountdown(s => {
        if (s <= 1) { clearInterval(t); setReady(true); return 0; }
        return s - 1;
      });
    }, 1000);
    return () => clearInterval(t);
  }, []);

  const sortedPackages = [...MOCK_PACKAGES].sort((a, b) => a.price_inr - b.price_inr);

  return (
    <div className="max-w-2xl mx-auto">
      <div className="flex items-center gap-3 mb-6">
        <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
        <p className="text-sm text-gray-500 font-medium">Session starting soon</p>
      </div>

      <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-6 mb-4">
        <div className="flex items-center gap-3 mb-4">
          <p className="text-2xl font-black text-gray-900 tracking-wide">{session.client_name.toUpperCase()}</p>
          <Badge topic={session.life_area} />
        </div>

        <div className="mb-4">
          <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-1">Her Question</p>
          <p className="text-lg font-medium text-gray-900 leading-relaxed">&ldquo;{session.question}&rdquo;</p>
        </div>

        <div className="mb-4">
          <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-1">Niro AI Context</p>
          <p className="text-sm text-gray-500">{session.niro_ai_context}</p>
        </div>

        {session.chart && (
          <div className="bg-gray-50 rounded-lg p-3 mb-4">
            <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-2">Chart</p>
            <div className="flex flex-wrap gap-3 text-sm text-gray-700 mb-2">
              <span>Asc: <strong>{session.chart.ascendant}</strong></span>
              <span>Moon: <strong>{session.chart.moon_sign}</strong></span>
              <span>Dasha: <strong>{session.chart.current_mahadasha}</strong></span>
            </div>
            <ul className="space-y-1">
              {session.top_transits.map((t, i) => (
                <li key={i} className="text-xs text-gray-500 flex gap-2"><span>•</span>{t}</li>
              ))}
            </ul>
          </div>
        )}
      </div>

      <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-6 mb-6">
        <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-3">Your Packages — Lead with the intro</p>
        <div className="space-y-2">
          {sortedPackages.map((pkg, i) => (
            <div key={pkg.id} className={`flex items-center justify-between rounded-lg px-3 py-2.5 ${i === 0 ? "bg-violet-50 border border-violet-100" : "bg-gray-50"}`}>
              <div>
                <p className="text-sm font-medium text-gray-900">{pkg.name}</p>
                {i === 0 && <p className="text-xs text-violet-600 font-medium">Lead with this →</p>}
              </div>
              <p className="text-sm font-bold text-gray-900">₹{pkg.price_inr.toLocaleString("en-IN")}</p>
            </div>
          ))}
        </div>
      </div>

      <div className="text-center mb-6">
        <div className="inline-flex items-center gap-3 bg-amber-50 border border-amber-100 rounded-full px-5 py-2.5">
          <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${countdown === 0 ? "bg-emerald-100 text-emerald-600" : "bg-amber-100 text-amber-700"}`}>
            {countdown === 0 ? "✓" : countdown}
          </div>
          <p className="text-sm text-amber-700">Take a moment to prepare — it makes a real difference</p>
        </div>
      </div>

      <Button
        size="lg"
        className={`w-full ${ready ? "animate-pulse shadow-violet-200 shadow-lg" : ""}`}
        onClick={() => router.push(`/session/${id}/cockpit`)}
      >
        I&apos;m Ready — Join Call →
      </Button>
    </div>
  );
}
