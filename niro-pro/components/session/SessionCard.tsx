"use client";
import { useState } from "react";
import { SESSION_CARDS, MOCK_PRACTITIONER } from "@/lib/mock-data";
import { clsx } from "clsx";

const PHASE_COLORS = ["border-teal-400", "border-indigo-400", "border-emerald-400"];

export default function SessionCard({ phaseDots }: { phaseDots: Record<number, boolean> }) {
  const [activePhase, setActivePhase] = useState(0);
  const tradition = MOCK_PRACTITIONER.primary_tradition;
  const card = SESSION_CARDS[tradition] ?? SESSION_CARDS["Vedic Astrology"];
  const phases = [card.phase01, card.phase02, card.phase03];
  const phase = phases[activePhase];

  return (
    <div>
      {/* Tabs */}
      <div className="flex gap-1 mb-4">
        {phases.map((p, i) => (
          <button
            key={i}
            onClick={() => setActivePhase(i)}
            className={clsx(
              "flex-1 py-2 text-xs font-semibold rounded-lg transition-colors relative",
              activePhase === i
                ? `bg-white border-b-2 ${PHASE_COLORS[i]} text-gray-900 shadow-sm`
                : "text-gray-400 hover:text-gray-600 hover:bg-gray-50"
            )}
          >
            Phase 0{i + 1}
            {phaseDots[i] && (
              <span className="absolute top-1 right-1 w-2 h-2 rounded-full bg-amber-400 animate-pulse" />
            )}
          </button>
        ))}
      </div>

      {/* Phase content */}
      <div className={clsx("border-l-4 pl-4 py-1 mb-4", PHASE_COLORS[activePhase])}>
        <p className="text-xs font-bold text-gray-900 mb-0.5">{phase.title}</p>
        <p className="text-xs text-gray-400 italic">{phase.guide}</p>
      </div>

      {"opening" in phase && (
        <div className="space-y-3 text-sm text-gray-700 leading-relaxed">
          <p className="bg-gray-50 rounded-lg p-3">{(phase as typeof card.phase01).opening}</p>
          <p className="bg-gray-50 rounded-lg p-3">{(phase as typeof card.phase01).past_obs}</p>
        </div>
      )}
      {"script" in phase && (
        <div className="space-y-3 text-sm text-gray-700 leading-relaxed">
          <p className="bg-gray-50 rounded-lg p-3">{(phase as typeof card.phase02).script}</p>
          <p className="text-xs text-gray-400 italic">{(phase as typeof card.phase02).resonance_check}</p>
        </div>
      )}

      {/* Never/Always rules */}
      <div className="mt-4 bg-gray-50 rounded-lg p-3">
        <div className="grid grid-cols-2 gap-3 text-xs">
          <div>
            <p className="font-semibold text-red-500 mb-1.5">❌ Never</p>
            {["Say a house/degree/card name", "Use fear-based framing", "Ask 'Would you like to book?'", "Give a full reading"].map(r => (
              <p key={r} className="text-gray-400 mb-1">{r}</p>
            ))}
          </div>
          <div>
            <p className="font-semibold text-emerald-600 mb-1.5">✓ Always</p>
            {["Speak in feelings + archetypes", "Use a past observation in Phase 01", "Read their question back verbatim", "Offer once — as a door, not a close"].map(r => (
              <p key={r} className="text-gray-400 mb-1">{r}</p>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
