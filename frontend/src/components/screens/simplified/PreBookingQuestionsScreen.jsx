import React, { useState } from 'react';
import { colors, shadows } from './theme';

/**
 * PreBookingQuestionsScreen
 * Collects 2 questions the user wants clarity on before the call.
 * Shown right before the time-slot picker in every booking path.
 */
export default function PreBookingQuestionsScreen({ expertName, onSubmit, onBack }) {
  const [q1, setQ1] = useState('');
  const [q2, setQ2] = useState('');
  const canContinue = q1.trim().length > 0 && q2.trim().length > 0;

  const handleSubmit = () => {
    if (!canContinue) return;
    onSubmit([q1.trim(), q2.trim()]);
  };

  return (
    <div className="min-h-screen flex flex-col" style={{ backgroundColor: colors.background.primary }}>
      {/* Header */}
      <header
        className="sticky top-0 z-40 px-4 py-4 flex items-center gap-4"
        style={{ backgroundColor: colors.background.primary }}
      >
        <button
          onClick={onBack}
          className="w-10 h-10 rounded-full flex items-center justify-center transition-all hover:bg-gray-100"
          style={{ backgroundColor: '#FFFFFF', boxShadow: shadows.card }}
        >
          <svg className="w-5 h-5" style={{ color: colors.text.dark }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
        </button>
        <div>
          <h1 className="text-lg font-semibold" style={{ color: colors.text.dark }}>
            Before we schedule…
          </h1>
          {expertName && (
            <p className="text-sm" style={{ color: colors.teal.primary }}>with {expertName}</p>
          )}
        </div>
      </header>

      {/* Content */}
      <div className="flex-1 px-4 py-6">
        <div className="max-w-lg mx-auto">
          {/* Intro card */}
          <div
            className="rounded-2xl p-5 mb-8"
            style={{ backgroundColor: colors.cream.warm }}
          >
            <h2 className="font-semibold text-base mb-1" style={{ color: colors.text.dark }}>
              Help {expertName || 'your astrologer'} prepare for your call
            </h2>
            <p className="text-sm" style={{ color: colors.text.secondary }}>
              Share the 2 things you most want clarity on. This helps your astrologer focus the session on what matters most to you.
            </p>
          </div>

          {/* Question 1 */}
          <div className="mb-5">
            <label className="block text-sm font-medium mb-2" style={{ color: colors.text.dark }}>
              Question 1 <span style={{ color: colors.teal.primary }}>*</span>
            </label>
            <textarea
              value={q1}
              onChange={(e) => setQ1(e.target.value.slice(0, 200))}
              rows={3}
              placeholder="e.g. Will I get a promotion this year?"
              className="w-full rounded-xl px-4 py-3 text-sm resize-none outline-none transition-all"
              style={{
                backgroundColor: '#FFFFFF',
                border: `1.5px solid ${q1.trim() ? colors.teal.primary : colors.ui.border || '#e5e7eb'}`,
                color: colors.text.dark,
                boxShadow: q1.trim() ? `0 0 0 3px ${colors.teal.primary}15` : 'none',
              }}
            />
            <p className="text-xs mt-1 text-right" style={{ color: colors.text.muted }}>
              {q1.length}/200
            </p>
          </div>

          {/* Question 2 */}
          <div className="mb-8">
            <label className="block text-sm font-medium mb-2" style={{ color: colors.text.dark }}>
              Question 2 <span style={{ color: colors.teal.primary }}>*</span>
            </label>
            <textarea
              value={q2}
              onChange={(e) => setQ2(e.target.value.slice(0, 200))}
              rows={3}
              placeholder="e.g. When is the right time to start my own business?"
              className="w-full rounded-xl px-4 py-3 text-sm resize-none outline-none transition-all"
              style={{
                backgroundColor: '#FFFFFF',
                border: `1.5px solid ${q2.trim() ? colors.teal.primary : colors.ui.border || '#e5e7eb'}`,
                color: colors.text.dark,
                boxShadow: q2.trim() ? `0 0 0 3px ${colors.teal.primary}15` : 'none',
              }}
            />
            <p className="text-xs mt-1 text-right" style={{ color: colors.text.muted }}>
              {q2.length}/200
            </p>
          </div>

          {/* CTA */}
          <button
            onClick={handleSubmit}
            disabled={!canContinue}
            className={`w-full py-4 rounded-full font-semibold text-base transition-all ${
              canContinue ? 'hover:shadow-lg hover:-translate-y-0.5' : 'opacity-40 cursor-not-allowed'
            }`}
            style={{
              backgroundColor: colors.teal.primary,
              color: '#FFFFFF',
            }}
          >
            Continue to scheduling →
          </button>

          <p className="text-xs text-center mt-3" style={{ color: colors.text.muted }}>
            Your questions are shared only with your astrologer
          </p>
        </div>
      </div>
    </div>
  );
}
