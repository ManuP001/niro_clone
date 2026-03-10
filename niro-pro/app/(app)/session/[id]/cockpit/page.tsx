"use client";
import { useParams } from "next/navigation";
import { useState, useCallback } from "react";
import { MOCK_SESSION } from "@/lib/mock-data";
import Badge from "@/components/ui/Badge";
import CountdownTimer from "@/components/session/CountdownTimer";
import SimulatedVideo from "@/components/session/SimulatedVideo";
import SessionCard from "@/components/session/SessionCard";
import OfferPanel from "@/components/session/OfferPanel";
import DebriefForm from "@/components/session/DebriefForm";

export default function CockpitPage() {
  useParams<{ id: string }>();
  const session = MOCK_SESSION;
  const [notes, setNotes] = useState(() => {
    if (typeof window !== "undefined") return localStorage.getItem(`niro_session_notes_${session.id}`) ?? "";
    return "";
  });
  const [phaseDots, setPhaseDots] = useState<Record<number, boolean>>({});
  const [showOffer, setShowOffer] = useState(false);
  const [offerSent, setOfferSent] = useState(false);
  const [callEnded, setCallEnded] = useState(false);

  const handleMilestone = useCallback((secondsLeft: number) => {
    // 1:00 left (240s) → Phase 02 dot
    if (secondsLeft === 240) setPhaseDots(p => ({ ...p, 1: true }));
    // 1:30 left (90s) → Phase 03 dot
    if (secondsLeft === 90) setPhaseDots(p => ({ ...p, 2: true }));
    // 0:30 left (30s) → show offer panel
    if (secondsLeft === 30) setShowOffer(true);
  }, []);

  function saveNotes(val: string) {
    setNotes(val);
    localStorage.setItem(`niro_session_notes_${session.id}`, val);
  }

  return (
    <div className="max-w-6xl mx-auto">
      <div className="flex items-center gap-3 mb-4">
        <Badge topic={session.life_area} />
        <p className="text-sm font-semibold text-gray-700">{session.client_name}</p>
        <div className="ml-auto">
          <CountdownTimer totalSeconds={300} onMilestone={handleMilestone} />
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        {/* Left — client brief + notes */}
        <div className="lg:col-span-1 space-y-4">
          <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-4">
            <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-2">Her Question</p>
            <p className="text-base font-medium text-gray-900 leading-relaxed">&ldquo;{session.question}&rdquo;</p>
            <p className="text-xs text-gray-400 italic mt-2">{session.niro_ai_context}</p>
            {session.chart && (
              <div className="mt-3 bg-gray-50 rounded-lg p-3 text-xs text-gray-500 space-y-1">
                <p><strong>Asc:</strong> {session.chart.ascendant} · <strong>Moon:</strong> {session.chart.moon_sign} · <strong>Dasha:</strong> {session.chart.current_mahadasha}</p>
                {session.top_transits.map((t, i) => <p key={i}>• {t}</p>)}
              </div>
            )}
          </div>

          <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-4">
            <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-2">Private Notes</p>
            <textarea
              value={notes}
              onChange={e => saveNotes(e.target.value)}
              rows={5}
              placeholder="Notes only you can see..."
              className="w-full text-sm text-gray-700 resize-none border-0 focus:outline-none bg-transparent"
            />
          </div>
        </div>

        {/* Right — video + session card */}
        <div className="lg:col-span-2 space-y-4">
          <SimulatedVideo clientName={session.client_name} onEnd={() => setCallEnded(true)} />

          <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-4">
            <SessionCard phaseDots={phaseDots} />
          </div>

          {(showOffer || callEnded) && !offerSent && (
            <div className={`transition-all duration-500 ${showOffer || callEnded ? "opacity-100 translate-y-0" : "opacity-0 translate-y-4"}`}>
              <OfferPanel clientName={session.client_name} onOfferSent={() => setOfferSent(true)} />
            </div>
          )}

          {offerSent && <DebriefForm />}

          {!showOffer && !callEnded && (
            <button
              onClick={() => { setCallEnded(true); setShowOffer(true); }}
              className="text-xs text-gray-400 hover:text-gray-600 underline"
            >
              Skip to offer panel
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
