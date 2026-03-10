"use client";
import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { MOCK_LEADS } from "@/lib/mock-data";
import Badge from "@/components/ui/Badge";
import Button from "@/components/ui/Button";
import { simulatePayment } from "@/lib/simulate";
import { useToast } from "@/components/ui/Toast";
import { formatSeconds } from "@/lib/utils";
import { clsx } from "clsx";

export default function LeadDetailPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const { showToast } = useToast();
  const lead = MOCK_LEADS.find(l => l.id === id);

  const [seconds, setSeconds] = useState(lead?.expires_in_seconds ?? 0);
  const [expired, setExpired] = useState(false);
  const [accepting, setAccepting] = useState(false);
  const [payStep, setPayStep] = useState<string | null>(null);
  const [declining, setDeclining] = useState(false);

  useEffect(() => {
    if (!lead) return;
    const t = setInterval(() => {
      setSeconds(s => {
        if (s <= 1) { clearInterval(t); setExpired(true); return 0; }
        return s - 1;
      });
    }, 1000);
    return () => clearInterval(t);
  }, [lead]);

  if (!lead) return <div className="p-8 text-gray-400">Lead not found.</div>;

  if (expired) {
    return (
      <div className="max-w-xl mx-auto pt-20 text-center px-4">
        <div className="text-5xl mb-4">⏰</div>
        <h2 className="text-xl font-bold text-gray-900 mb-2">This lead has expired</h2>
        <p className="text-gray-400 mb-8">No charge was applied.</p>
        <Button onClick={() => router.push("/leads")}>← Back to Leads</Button>
      </div>
    );
  }

  async function handleAccept() {
    setAccepting(true);
    await simulatePayment(step => setPayStep(step));
    showToast("Lead accepted ✓");
    router.push(`/session/${lead!.id}/prep`);
  }

  function handleDecline() {
    setDeclining(true);
  }

  return (
    <div className="max-w-2xl mx-auto">
      <button onClick={() => router.push("/leads")} className="text-sm text-gray-400 hover:text-gray-600 mb-6 flex items-center gap-1">
        ← Back to leads
      </button>

      <div className="flex items-center justify-between mb-4">
        <Badge topic={lead.life_area} size="md" />
        <span className={clsx("text-sm font-mono font-bold px-3 py-1.5 rounded-full",
          seconds > 300 ? "bg-emerald-100 text-emerald-700" :
          seconds > 60  ? "bg-amber-100 text-amber-700 animate-pulse" :
                          "bg-red-100 text-red-700 animate-pulse"
        )}>
          {formatSeconds(seconds)}
        </span>
      </div>

      <p className="text-xl font-medium text-gray-900 leading-relaxed mb-3">&ldquo;{lead.question}&rdquo;</p>

      <p className="text-sm text-gray-500 italic mb-6">{lead.niro_ai_context}</p>

      <div className="bg-gray-50 rounded-xl p-4 mb-6">
        <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-3">Chart snapshot</h3>
        {lead.chart ? (
          <div className="space-y-2">
            <div className="flex gap-4 text-sm text-gray-700">
              <span>Asc: <strong>{lead.chart.ascendant}</strong></span>
              <span>Moon: <strong>{lead.chart.moon_sign}</strong></span>
              <span>Dasha: <strong>{lead.chart.current_mahadasha}</strong> until {lead.chart.mahadasha_end}</span>
            </div>
            {lead.top_transits.length > 0 && (
              <ul className="text-sm text-gray-600 space-y-1 mt-2">
                {lead.top_transits.map((t, i) => <li key={i} className="flex items-start gap-2"><span className="text-gray-300 mt-1">•</span>{t}</li>)}
              </ul>
            )}
            {lead.focus_factors.length > 0 && (
              <div className="mt-2 space-y-1">
                {lead.focus_factors.map((f, i) => (
                  <div key={i} className="bg-violet-50 rounded-lg px-3 py-2 text-xs text-violet-700">{f.summary}</div>
                ))}
              </div>
            )}
          </div>
        ) : (
          <p className="text-sm text-gray-400">Birth details not provided — focus on the question above.</p>
        )}
      </div>

      <div className="bg-amber-50 border border-amber-100 rounded-xl p-4 mb-6 flex items-center justify-between">
        <div>
          <p className="text-sm font-semibold text-gray-900">Platform fee</p>
          <p className="text-xs text-gray-400">One-time flat fee to accept this lead</p>
        </div>
        <p className="text-xl font-bold text-gray-900">₹{lead.flat_fee_inr}</p>
      </div>

      {payStep && (
        <div className="bg-violet-50 border border-violet-100 rounded-xl p-4 mb-4 text-sm text-violet-700 font-medium text-center">
          {payStep}
        </div>
      )}

      <Button
        size="lg"
        className="w-full mb-3"
        loading={accepting}
        onClick={handleAccept}
        disabled={accepting}
      >
        Accept Lead →
      </Button>

      <div className="text-center">
        <button
          onClick={handleDecline}
          className="text-sm text-gray-400 hover:text-gray-600 underline"
        >
          Decline this lead
        </button>
      </div>

      {declining && (
        <div className="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-xl p-6 max-w-sm w-full shadow-xl">
            <h3 className="font-semibold text-gray-900 mb-2">Pass on this lead?</h3>
            <p className="text-sm text-gray-400 mb-5">No charge will be applied.</p>
            <div className="flex gap-3">
              <Button variant="secondary" className="flex-1" onClick={() => setDeclining(false)}>Cancel</Button>
              <Button variant="danger" className="flex-1" onClick={() => { showToast("Lead passed — no charge applied", "info"); router.push("/leads"); }}>
                Yes, Decline
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
