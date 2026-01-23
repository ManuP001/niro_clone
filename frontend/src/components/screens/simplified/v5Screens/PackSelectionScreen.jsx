/**
 * NIRO V5 Pack Selection Screen
 * Step 6 in the 8-step onboarding flow
 * Shows 3 tiers: Focussed, Supported (Recommended), Comprehensive
 */

import React, { useMemo } from 'react';
import { colors, shadows } from '../theme';
import { getLandingPageContent, formatPriceInr } from '../v5Data/landingPageContent';

// Tier card component
const TierCard = ({ tier, tierName, isSelected, isRecommended, onSelect }) => {
  const priceInfo = tier;
  
  return (
    <button
      onClick={() => onSelect(tierName)}
      className="w-full p-4 rounded-2xl text-left transition-all active:scale-[0.98] relative"
      style={{
        background: isSelected 
          ? `linear-gradient(135deg, ${colors.teal.primary}15 0%, ${colors.gold.primary}25 100%)`
          : colors.background.card,
        border: `2px solid ${isSelected ? colors.gold.primary : isRecommended ? colors.teal.primary : colors.ui.borderDark}`,
        boxShadow: isSelected ? shadows.md : isRecommended ? shadows.sm : 'none'
      }}
      data-testid={`tier-card-${tierName.toLowerCase()}`}
    >
      {/* Recommended badge - ALWAYS on Supported tier */}
      {isRecommended && (
        <div 
          className="absolute -top-3 left-1/2 transform -translate-x-1/2 px-3 py-1 rounded-full text-xs font-bold"
          style={{ 
            background: `linear-gradient(135deg, ${colors.gold.primary} 0%, ${colors.gold.light} 100%)`,
            color: colors.teal.dark,
            boxShadow: shadows.sm
          }}
        >
          Recommended
        </div>
      )}

      <div className="flex items-start justify-between mb-3 mt-1">
        <div>
          <h3 
            className="text-lg font-bold"
            style={{ color: colors.text.dark }}
          >
            {tierName}
          </h3>
          <p 
            className="text-xs"
            style={{ color: colors.text.secondary }}
          >
            {priceInfo.durationWeeks} weeks
          </p>
        </div>
        
        {/* Selection indicator */}
        <div 
          className="w-6 h-6 rounded-full flex items-center justify-center"
          style={{ 
            background: isSelected ? colors.ui.success : 'transparent',
            border: `2px solid ${isSelected ? colors.ui.success : colors.ui.borderDark}`
          }}
        >
          {isSelected && (
            <svg className="w-3.5 h-3.5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
            </svg>
          )}
        </div>
      </div>

      {/* Price */}
      <div className="mb-3">
        <span 
          className="text-2xl font-bold"
          style={{ color: colors.teal.dark }}
        >
          {formatPriceInr(priceInfo.priceInr)}
        </span>
      </div>

      {/* Features preview */}
      <div 
        className="p-3 rounded-xl space-y-2"
        style={{ background: `${colors.teal.primary}05` }}
      >
        {tierName === 'Focussed' && (
          <>
            <FeatureItem text="1× 60-min video call" />
            <FeatureItem text="7 days async chat" />
            <FeatureItem text="1 follow-up check-in" />
          </>
        )}
        {tierName === 'Supported' && (
          <>
            <FeatureItem text="3 sessions (1×60-min + 2×30-min)" highlight />
            <FeatureItem text="Unlimited chat for full duration" highlight />
            <FeatureItem text="2 follow-ups included" />
          </>
        )}
        {tierName === 'Comprehensive' && (
          <>
            <FeatureItem text="5 sessions (2×60-min + 3×30-min)" highlight />
            <FeatureItem text="Unlimited chat + priority response" highlight />
            <FeatureItem text="Multiple expert perspectives" highlight />
          </>
        )}
      </div>
    </button>
  );
};

// Feature item component
const FeatureItem = ({ text, highlight = false }) => (
  <div className="flex items-center gap-2">
    <svg 
      className="w-4 h-4 flex-shrink-0" 
      fill="none" 
      viewBox="0 0 24 24" 
      stroke={highlight ? colors.teal.primary : colors.ui.success}
    >
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
    </svg>
    <span 
      className="text-xs"
      style={{ color: highlight ? colors.teal.dark : colors.text.secondary }}
    >
      {text}
    </span>
  </div>
);

export default function PackSelectionScreen({ 
  selectedSubtopic,
  selectedTier, 
  onSelectTier, 
  onContinue, 
  onBack 
}) {
  // Get content for the selected subtopic
  const content = useMemo(() => {
    return getLandingPageContent(selectedSubtopic);
  }, [selectedSubtopic]);

  const tierCards = content?.tierCards || {
    Focussed: { priceInr: 4999, durationWeeks: 8 },
    Supported: { priceInr: 6999, durationWeeks: 8 },
    Comprehensive: { priceInr: 8999, durationWeeks: 8 }
  };

  const tiers = ['Focussed', 'Supported', 'Comprehensive'];

  return (
    <div 
      className="min-h-screen flex flex-col"
      style={{ background: colors.background.gradient }}
    >
      {/* Header */}
      <div className="px-5 pt-12 pb-4">
        <button 
          onClick={onBack}
          className="flex items-center gap-2 text-sm font-medium mb-6 transition-opacity hover:opacity-70"
          style={{ color: colors.gold.primary }}
          data-testid="pack-back-btn"
        >
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          Back
        </button>
        
        {/* Subtopic badge */}
        <div 
          className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium mb-3"
          style={{ 
            background: `${colors.gold.primary}20`,
            color: colors.gold.primary
          }}
        >
          {content?.subTopic}
        </div>
        
        <h1 
          className="text-2xl font-bold mb-2"
          style={{ color: colors.text.primary }}
        >
          Choose Your Pack
        </h1>
        <p 
          className="text-sm"
          style={{ color: colors.text.muted }}
        >
          Select the level of support you need
        </p>
      </div>

      {/* Tier Cards */}
      <div 
        className="flex-1 px-5 pb-safe overflow-y-auto space-y-4"
        style={{ paddingBottom: 'calc(env(safe-area-inset-bottom) + 120px)' }}
      >
        {tiers.map((tierName) => (
          <TierCard
            key={tierName}
            tier={tierCards[tierName]}
            tierName={tierName}
            isSelected={selectedTier === tierName}
            isRecommended={tierName === 'Supported'} // ALWAYS show Recommended on Supported
            onSelect={onSelectTier}
          />
        ))}

        {/* Refund guarantee */}
        <div 
          className="flex items-center justify-center gap-2 py-3 rounded-xl mt-4"
          style={{ 
            background: `${colors.ui.success}10`,
            border: `1px solid ${colors.ui.success}30`
          }}
        >
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke={colors.ui.success}>
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
          </svg>
          <span 
            className="text-sm font-medium"
            style={{ color: colors.ui.success }}
          >
            100% satisfaction guaranteed
          </span>
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
        <div className="flex items-center justify-between mb-3">
          <div>
            <p 
              className="text-xs"
              style={{ color: colors.text.muted }}
            >
              Selected Pack
            </p>
            <p 
              className="font-semibold"
              style={{ color: colors.text.primary }}
            >
              {selectedTier || 'None selected'}
            </p>
          </div>
          {selectedTier && tierCards[selectedTier] && (
            <p 
              className="text-xl font-bold"
              style={{ color: colors.gold.primary }}
            >
              {formatPriceInr(tierCards[selectedTier].priceInr)}
            </p>
          )}
        </div>
        
        <button
          onClick={onContinue}
          disabled={!selectedTier}
          className="w-full py-4 rounded-xl font-semibold text-base transition-all active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed"
          style={{
            background: selectedTier ? colors.gold.primary : `${colors.gold.primary}80`,
            color: colors.text.dark,
            boxShadow: selectedTier ? shadows.md : 'none'
          }}
          data-testid="pack-continue-btn"
        >
          Pick this pack
        </button>
      </div>
    </div>
  );
}
