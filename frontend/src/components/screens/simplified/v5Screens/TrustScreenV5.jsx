/**
 * NIRO V5 Trust Screen
 * Step 5 in the 8-step onboarding flow
 * Shows WHY NIRO section and trust pillars
 */

import React from 'react';
import { colors, shadows } from '../theme';

// Trust pillar component
const TrustPillar = ({ icon, title, description }) => (
  <div 
    className="flex items-start gap-4 p-4 rounded-xl"
    style={{ background: `${colors.teal.primary}08` }}
  >
    <div 
      className="w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0"
      style={{ 
        background: `linear-gradient(135deg, ${colors.gold.primary}30 0%, ${colors.gold.light}30 100%)` 
      }}
    >
      {icon}
    </div>
    <div>
      <h3 
        className="text-base font-semibold mb-1"
        style={{ color: colors.text.dark }}
      >
        {title}
      </h3>
      <p 
        className="text-sm"
        style={{ color: colors.text.secondary }}
      >
        {description}
      </p>
    </div>
  </div>
);

// Trust chip component
const TrustChip = ({ text }) => (
  <div 
    className="flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium"
    style={{ 
      background: colors.background.card,
      border: `1px solid ${colors.ui.borderDark}`,
      color: colors.text.dark
    }}
  >
    <svg 
      className="w-3.5 h-3.5" 
      fill="none" 
      viewBox="0 0 24 24" 
      stroke={colors.ui.success}
    >
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
    </svg>
    {text}
  </div>
);

export default function TrustScreenV5({ onContinue, onBack }) {
  const pillars = [
    {
      icon: (
        <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke={colors.gold.dark}>
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.828 14.828a4 4 0 01-5.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      ),
      title: 'Calm guidance, not fear-based predictions',
      description: 'We focus on clarity and solutions, never on creating anxiety about your future.'
    },
    {
      icon: (
        <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke={colors.gold.dark}>
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
        </svg>
      ),
      title: 'Clear "why" behind suggestions',
      description: "We explain our reasoning so you understand and can make informed decisions."
    },
    {
      icon: (
        <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke={colors.gold.dark}>
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
        </svg>
      ),
      title: 'Support across the full situation',
      description: "Not just one call — we're with you through your entire journey until clarity."
    }
  ];

  const trustChips = [
    'Verified Experts',
    'Clear + Practical Guidance',
    'Satisfaction Guaranteed'
  ];

  return (
    <div 
      className="min-h-screen flex flex-col"
      style={{ background: colors.background.gradient }}
    >
      {/* Header */}
      <div className="px-5 pt-12 pb-6">
        <button 
          onClick={onBack}
          className="flex items-center gap-2 text-sm font-medium mb-6 transition-opacity hover:opacity-70"
          style={{ color: colors.gold.primary }}
          data-testid="trust-back-btn"
        >
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          Back
        </button>
        
        <h1 
          className="text-2xl font-bold mb-2"
          style={{ color: colors.text.primary }}
        >
          Why NIRO?
        </h1>
        <p 
          className="text-sm"
          style={{ color: colors.text.muted }}
        >
          Here's what makes us different
        </p>
      </div>

      {/* Content Card */}
      <div 
        className="flex-1 px-5 pb-safe"
        style={{ paddingBottom: 'calc(env(safe-area-inset-bottom) + 100px)' }}
      >
        <div 
          className="rounded-2xl p-5"
          style={{ 
            background: `rgba(255, 255, 255, 0.95)`,
            boxShadow: shadows.lg
          }}
        >
          {/* Trust Pillars */}
          <div className="space-y-4 mb-6">
            {pillars.map((pillar, idx) => (
              <TrustPillar key={idx} {...pillar} />
            ))}
          </div>

          {/* Divider */}
          <div 
            className="h-px my-6"
            style={{ background: colors.ui.borderDark }}
          />

          {/* Trust Chips */}
          <div className="flex flex-wrap gap-2 justify-center">
            {trustChips.map((chip, idx) => (
              <TrustChip key={idx} text={chip} />
            ))}
          </div>

          {/* Expert stats */}
          <div 
            className="mt-6 p-4 rounded-xl text-center"
            style={{ background: `${colors.teal.primary}08` }}
          >
            <div className="flex items-center justify-center gap-6">
              <div>
                <p 
                  className="text-2xl font-bold"
                  style={{ color: colors.teal.primary }}
                >
                  50+
                </p>
                <p 
                  className="text-xs"
                  style={{ color: colors.text.secondary }}
                >
                  Verified Experts
                </p>
              </div>
              <div 
                className="w-px h-10"
                style={{ background: colors.ui.borderDark }}
              />
              <div>
                <p 
                  className="text-2xl font-bold"
                  style={{ color: colors.teal.primary }}
                >
                  50k+
                </p>
                <p 
                  className="text-xs"
                  style={{ color: colors.text.secondary }}
                >
                  Users Helped
                </p>
              </div>
              <div 
                className="w-px h-10"
                style={{ background: colors.ui.borderDark }}
              />
              <div>
                <p 
                  className="text-2xl font-bold"
                  style={{ color: colors.teal.primary }}
                >
                  4.9★
                </p>
                <p 
                  className="text-xs"
                  style={{ color: colors.text.secondary }}
                >
                  Rating
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Fixed CTA */}
      <div 
        className="fixed bottom-0 left-0 right-0 p-5 border-t"
        style={{ 
          background: `linear-gradient(to top, ${colors.teal.dark} 0%, ${colors.teal.primary} 100%)`,
          borderColor: colors.ui.border,
          paddingBottom: 'calc(env(safe-area-inset-bottom) + 20px)'
        }}
      >
        <button
          onClick={onContinue}
          className="w-full py-4 rounded-xl font-semibold text-base transition-all active:scale-[0.98]"
          style={{
            background: colors.gold.primary,
            color: colors.text.dark,
            boxShadow: shadows.md
          }}
          data-testid="trust-continue-btn"
        >
          Choose Your Pack
        </button>
      </div>
    </div>
  );
}
