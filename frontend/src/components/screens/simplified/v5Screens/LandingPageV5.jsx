/**
 * NIRO V5 Landing Page
 * Displays detailed content for each sub-topic
 * Layout based on Frame 27 wireframe with V5 theme styling
 * 
 * Sections:
 * 1. Hero with tier selector
 * 2. Journey outcomes
 * 3. Included consultations/features
 * 4. Optional remedies
 * 5. What happens after purchase
 * 6. Why NIRO
 * 7. FAQs
 * 8. Sticky CTA bar
 */

import React, { useState, useMemo, useCallback } from 'react';
import { colors, shadows, borderRadius } from '../theme';
import { getLandingPageContent, formatPriceInr } from '../v5Data/landingPageContent';

// ==========================================
// TIER SELECTOR COMPONENT
// ==========================================
const TierSelector = ({ tiers, selectedTier, onSelectTier }) => {
  const tierNames = ['Focussed', 'Supported', 'Comprehensive'];
  const durationMap = {
    'Focussed': '4-8 weeks',
    'Supported': '8 weeks',
    'Comprehensive': '8-12 weeks'
  };

  return (
    <div className="flex gap-2 overflow-x-auto pb-2 scrollbar-hide">
      {tierNames.map((name) => {
        const isSelected = selectedTier === name;
        const isRecommended = name === 'Supported';
        const tier = tiers[name];
        
        return (
          <button
            key={name}
            onClick={() => onSelectTier(name)}
            className="flex-shrink-0 px-4 py-3 rounded-xl text-left transition-all relative"
            style={{
              background: isSelected ? colors.text.dark : colors.background.card,
              minWidth: '100px'
            }}
            data-testid={`landing-tier-${name.toLowerCase()}`}
          >
            {isRecommended && !isSelected && (
              <span 
                className="absolute -top-2 left-1/2 transform -translate-x-1/2 text-[10px] px-2 py-0.5 rounded-full font-medium"
                style={{ background: colors.gold.primary, color: colors.teal.dark }}
              >
                Best Value
              </span>
            )}
            <p 
              className="text-sm font-semibold"
              style={{ color: isSelected ? colors.text.primary : colors.text.dark }}
            >
              {name}
            </p>
            <p 
              className="text-xs"
              style={{ color: isSelected ? colors.text.muted : colors.text.secondary }}
            >
              {tier?.durationWeeks} weeks
            </p>
          </button>
        );
      })}
    </div>
  );
};

// ==========================================
// OUTCOME CARD COMPONENT
// ==========================================
const OutcomeCard = ({ text, index }) => (
  <div 
    className="flex items-start gap-3 p-3 rounded-xl"
    style={{ background: `${colors.teal.primary}05` }}
  >
    <div 
      className="w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0 text-xs font-bold"
      style={{ 
        background: colors.gold.primary,
        color: colors.teal.dark
      }}
    >
      {index + 1}
    </div>
    <p 
      className="text-sm flex-1"
      style={{ color: colors.text.dark }}
    >
      {text}
    </p>
  </div>
);

// ==========================================
// FEATURE ITEM COMPONENT
// ==========================================
const FeatureItem = ({ icon, text, subtext }) => (
  <div className="flex items-start gap-3">
    <div 
      className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0"
      style={{ background: `${colors.gold.primary}20` }}
    >
      {icon}
    </div>
    <div>
      <p 
        className="text-sm font-medium"
        style={{ color: colors.text.dark }}
      >
        {text}
      </p>
      {subtext && (
        <p 
          className="text-xs mt-0.5"
          style={{ color: colors.text.secondary }}
        >
          {subtext}
        </p>
      )}
    </div>
  </div>
);

// ==========================================
// REMEDY CARD COMPONENT
// ==========================================
const RemedyCard = ({ remedy }) => (
  <div 
    className="flex-shrink-0 w-48 p-4 rounded-xl"
    style={{ 
      background: colors.background.card,
      border: `1px solid ${colors.ui.borderDark}`
    }}
  >
    <div 
      className="w-10 h-10 rounded-lg flex items-center justify-center mb-3"
      style={{ background: `${colors.teal.primary}10` }}
    >
      {remedy.type === 'pooja' && (
        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke={colors.teal.primary}>
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 18.657A8 8 0 016.343 7.343S7 9 9 10c0-2 .5-5 2.986-7C14 5 16.09 5.777 17.656 7.343A7.975 7.975 0 0120 13a7.975 7.975 0 01-2.343 5.657z" />
        </svg>
      )}
      {remedy.type === 'gemstone' && (
        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke={colors.teal.primary}>
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
        </svg>
      )}
      {remedy.type === 'kit' && (
        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke={colors.teal.primary}>
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
        </svg>
      )}
      {remedy.type === 'session' && (
        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke={colors.teal.primary}>
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
        </svg>
      )}
    </div>
    <h4 
      className="text-sm font-semibold mb-1"
      style={{ color: colors.text.dark }}
    >
      {remedy.name}
    </h4>
    <p 
      className="text-xs mb-3"
      style={{ color: colors.text.secondary }}
    >
      {remedy.description}
    </p>
    <button
      className="text-xs font-medium"
      style={{ color: colors.teal.primary }}
    >
      Add to pack →
    </button>
  </div>
);

// ==========================================
// FAQ ITEM COMPONENT
// ==========================================
const FAQItem = ({ faq, isOpen, onToggle }) => (
  <div 
    className="border-b py-4"
    style={{ borderColor: colors.ui.borderDark }}
  >
    <button
      onClick={onToggle}
      className="w-full flex items-center justify-between text-left"
    >
      <span 
        className="text-sm font-medium pr-4"
        style={{ color: colors.text.dark }}
      >
        {faq.q}
      </span>
      <svg 
        className={`w-5 h-5 flex-shrink-0 transition-transform ${isOpen ? 'rotate-180' : ''}`}
        fill="none" 
        viewBox="0 0 24 24" 
        stroke={colors.teal.primary}
      >
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
      </svg>
    </button>
    {isOpen && (
      <p 
        className="text-sm mt-3 pr-8"
        style={{ color: colors.text.secondary }}
      >
        {faq.a}
      </p>
    )}
  </div>
);

// ==========================================
// MAIN LANDING PAGE COMPONENT
// ==========================================
export default function LandingPageV5({ 
  slug, 
  onCheckout, 
  onBack,
  initialTier = 'Supported'
}) {
  const [selectedTier, setSelectedTier] = useState(initialTier);
  const [openFAQ, setOpenFAQ] = useState(null);

  // Get content for this slug
  const content = useMemo(() => {
    return getLandingPageContent(slug);
  }, [slug]);

  // Get features for selected tier
  const selectedTierFeatures = useMemo(() => {
    return content?.featuresByTier?.[selectedTier] || {};
  }, [content, selectedTier]);

  const handleCheckout = useCallback(() => {
    if (content && selectedTier) {
      const tierPrice = content.tierCards[selectedTier]?.priceInr;
      onCheckout({
        subtopicSlug: slug,
        tierName: selectedTier,
        price: tierPrice
      });
    }
  }, [content, selectedTier, slug, onCheckout]);

  if (!content) {
    return (
      <div 
        className="min-h-screen flex items-center justify-center"
        style={{ background: colors.background.gradient }}
      >
        <p style={{ color: colors.text.primary }}>Content not found</p>
      </div>
    );
  }

  const currentPrice = content.tierCards[selectedTier]?.priceInr;

  return (
    <div 
      className="min-h-screen pb-32"
      style={{ background: colors.background.gradient }}
    >
      {/* ==========================================
          HERO SECTION
          ========================================== */}
      <div className="px-5 pt-12 pb-6">
        {/* Back button */}
        <button 
          onClick={onBack}
          className="flex items-center gap-2 text-sm font-medium mb-6 transition-opacity hover:opacity-70"
          style={{ color: colors.gold.primary }}
          data-testid="landing-back-btn"
        >
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          Back
        </button>

        {/* Category badge */}
        <div 
          className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium mb-3"
          style={{ 
            background: `${colors.gold.primary}20`,
            color: colors.gold.primary
          }}
        >
          {content.category}
        </div>

        {/* Headline */}
        <h1 
          className="text-2xl font-bold mb-2"
          style={{ color: colors.text.primary }}
        >
          {content.headline}
        </h1>
        
        {/* Sub-headline */}
        <p 
          className="text-sm mb-6"
          style={{ color: colors.text.muted }}
        >
          {content.subHeadline}
        </p>

        {/* Trust chips */}
        <div className="flex flex-wrap gap-2 mb-6">
          {['Verified Experts', 'Clear + Practical Guidance', 'Satisfaction Guaranteed'].map((chip) => (
            <span 
              key={chip}
              className="flex items-center gap-1 text-xs px-2.5 py-1 rounded-full"
              style={{ 
                background: `rgba(255,255,255,0.15)`,
                color: colors.text.primary
              }}
            >
              <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              {chip}
            </span>
          ))}
        </div>

        {/* Tier selector */}
        <TierSelector 
          tiers={content.tierCards}
          selectedTier={selectedTier}
          onSelectTier={setSelectedTier}
        />
      </div>

      {/* ==========================================
          MAIN CONTENT (White card area)
          ========================================== */}
      <div 
        className="rounded-t-3xl pt-6 -mt-2"
        style={{ background: colors.background.card }}
      >
        {/* ---- WHAT YOU'RE PROBABLY FEELING ---- */}
        <section className="px-5 mb-8">
          <h2 
            className="text-lg font-bold mb-4 flex items-center gap-2"
            style={{ color: colors.text.dark }}
          >
            <span className="w-1 h-5 rounded-full" style={{ background: colors.teal.primary }} />
            What you&apos;re probably feeling
          </h2>
          <div className="space-y-2">
            {content.painPoints.map((point, idx) => (
              <div 
                key={idx}
                className="flex items-start gap-3 p-3 rounded-lg"
                style={{ background: `${colors.ui.warning}10` }}
              >
                <span style={{ color: colors.ui.warning }}>•</span>
                <p 
                  className="text-sm"
                  style={{ color: colors.text.dark }}
                >
                  {point}
                </p>
              </div>
            ))}
          </div>
        </section>

        {/* ---- JOURNEY OUTCOMES ---- */}
        <section className="px-5 mb-8">
          <h2 
            className="text-lg font-bold mb-4 flex items-center gap-2"
            style={{ color: colors.text.dark }}
          >
            <span className="w-1 h-5 rounded-full" style={{ background: colors.gold.primary }} />
            What will the journey unfold for you?
          </h2>
          <div className="space-y-3">
            {selectedTierFeatures.outcomes?.slice(0, 5).map((outcome, idx) => (
              <OutcomeCard key={idx} text={outcome} index={idx} />
            ))}
          </div>
        </section>

        {/* ---- HOW IT UNFOLDS ---- */}
        <section className="px-5 mb-8">
          <h2 
            className="text-lg font-bold mb-4 flex items-center gap-2"
            style={{ color: colors.text.dark }}
          >
            <span className="w-1 h-5 rounded-full" style={{ background: colors.teal.primary }} />
            How will it unfold?
          </h2>
          <div 
            className="p-4 rounded-xl space-y-4"
            style={{ background: `${colors.teal.primary}05` }}
          >
            <FeatureItem 
              icon={
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke={colors.gold.dark}>
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
              }
              text={selectedTierFeatures.consultations}
              subtext="With verified Niro experts"
            />
            <FeatureItem 
              icon={
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke={colors.gold.dark}>
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                </svg>
              }
              text={`${selectedTierFeatures.asyncChat} async support`}
              subtext="Message anytime, get responses within 24-48 hours"
            />
            <FeatureItem 
              icon={
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke={colors.gold.dark}>
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              }
              text={`${selectedTierFeatures.duration} access`}
              subtext="Full pack validity"
            />
          </div>
        </section>

        {/* ---- OPTIONAL REMEDIES ---- */}
        {content.optionalRemedies && content.optionalRemedies.length > 0 && (
          <section className="mb-8">
            <div className="px-5 mb-3">
              <h2 
                className="text-lg font-bold flex items-center gap-2"
                style={{ color: colors.text.dark }}
              >
                <span className="w-1 h-5 rounded-full" style={{ background: colors.gold.primary }} />
                Optional add-ons
              </h2>
              <p 
                className="text-xs mt-1"
                style={{ color: colors.text.secondary }}
              >
                Only if relevant. We arrange it end-to-end.
              </p>
            </div>
            <div 
              className="flex gap-3 overflow-x-auto px-5 pb-2 scrollbar-hide"
              style={{ scrollbarWidth: 'none' }}
            >
              {content.optionalRemedies.map((remedy, idx) => (
                <RemedyCard key={idx} remedy={remedy} />
              ))}
            </div>
          </section>
        )}

        {/* ---- WHAT HAPPENS AFTER PURCHASE ---- */}
        <section className="px-5 mb-8">
          <h2 
            className="text-lg font-bold mb-4 flex items-center gap-2"
            style={{ color: colors.text.dark }}
          >
            <span className="w-1 h-5 rounded-full" style={{ background: colors.teal.primary }} />
            What happens after purchase
          </h2>
          <div className="space-y-3">
            {[
              { step: 1, title: 'Answer quick questions', desc: 'Share your situation in detail' },
              { step: 2, title: 'Expert matching', desc: 'We connect you with the right expert' },
              { step: 3, title: 'Call + follow-ups', desc: 'Deep consultations and ongoing support' },
              { step: 4, title: 'Ongoing support', desc: 'Chat access + remedies if chosen' }
            ].map((item) => (
              <div 
                key={item.step}
                className="flex items-start gap-3"
              >
                <div 
                  className="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 text-sm font-bold"
                  style={{ 
                    background: `${colors.teal.primary}15`,
                    color: colors.teal.primary
                  }}
                >
                  {item.step}
                </div>
                <div>
                  <p 
                    className="text-sm font-medium"
                    style={{ color: colors.text.dark }}
                  >
                    {item.title}
                  </p>
                  <p 
                    className="text-xs"
                    style={{ color: colors.text.secondary }}
                  >
                    {item.desc}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* ---- WHY NIRO ---- */}
        <section className="px-5 mb-8">
          <h2 
            className="text-lg font-bold mb-4 flex items-center gap-2"
            style={{ color: colors.text.dark }}
          >
            <span className="w-1 h-5 rounded-full" style={{ background: colors.gold.primary }} />
            Why NIRO
          </h2>
          <div 
            className="p-4 rounded-xl space-y-4"
            style={{ background: `${colors.teal.primary}05` }}
          >
            {[
              'Calm guidance, not fear-based predictions',
              'Clear "why" behind every suggestion',
              'Support across your full situation'
            ].map((text, idx) => (
              <div key={idx} className="flex items-center gap-3">
                <svg className="w-5 h-5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke={colors.ui.success}>
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
                <p 
                  className="text-sm"
                  style={{ color: colors.text.dark }}
                >
                  {text}
                </p>
              </div>
            ))}
          </div>
        </section>

        {/* ---- FAQs ---- */}
        <section className="px-5 mb-8">
          <h2 
            className="text-lg font-bold mb-4 flex items-center gap-2"
            style={{ color: colors.text.dark }}
          >
            <span className="w-1 h-5 rounded-full" style={{ background: colors.teal.primary }} />
            Frequently asked questions
          </h2>
          <div>
            {content.faqs.map((faq, idx) => (
              <FAQItem 
                key={idx}
                faq={faq}
                isOpen={openFAQ === idx}
                onToggle={() => setOpenFAQ(openFAQ === idx ? null : idx)}
              />
            ))}
          </div>
        </section>
      </div>

      {/* ==========================================
          STICKY CTA BAR
          ========================================== */}
      <div 
        className="fixed bottom-0 left-0 right-0 p-4 border-t"
        style={{ 
          background: colors.background.card,
          borderColor: colors.ui.borderDark,
          boxShadow: '0 -4px 20px rgba(0,0,0,0.1)',
          paddingBottom: 'calc(env(safe-area-inset-bottom) + 16px)'
        }}
      >
        <div className="flex items-center justify-between mb-3">
          <div>
            <p 
              className="text-xs"
              style={{ color: colors.text.secondary }}
            >
              {selectedTier} • {content.tierCards[selectedTier]?.durationWeeks} weeks
            </p>
            <p 
              className="text-xl font-bold"
              style={{ color: colors.teal.dark }}
            >
              {formatPriceInr(currentPrice)}
            </p>
          </div>
          <button
            onClick={handleCheckout}
            className="px-8 py-3 rounded-xl font-semibold transition-all active:scale-[0.98]"
            style={{
              background: colors.gold.primary,
              color: colors.text.dark,
              boxShadow: shadows.md
            }}
            data-testid="landing-checkout-btn"
          >
            Start my journey
          </button>
        </div>
        <p 
          className="text-xs text-center"
          style={{ color: colors.text.secondary }}
        >
          {content.refundGuarantee}
        </p>
      </div>
    </div>
  );
}
