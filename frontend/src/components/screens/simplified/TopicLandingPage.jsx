import React, { useState, useEffect, useMemo } from 'react';
import { colors } from './theme';
import { 
  ArrowLeftIcon, 
  CheckIcon, 
  ShieldIcon, 
  ChevronRightIcon,
  ClockIcon,
  CalendarIcon,
  ChatIcon,
  GiftIcon,
  PhoneIcon
} from './icons';
import { trackEvent } from './utils';

// Import V6 content
import { 
  getV6SubtopicBySlug,
  V6_TILE_TO_SUBTOPIC_MAP,
  V6_TIER_CONFIG,
  V6_EXPERTS
} from './v6Data/landingPageContentV6';

/**
 * TopicLandingPage V6 - Frame 27 Layout + Premium UI
 * 
 * Key Changes:
 * - Gradient background (same as onboarding + home)
 * - Subtle highlight style (boxes, dividers, shade differences - no rainbow blocks)
 * - Topic explainer 1-liner at top
 * - Recommended badge ONLY on tier selector tabs
 * - "Unlimited chat" wording (exact)
 * - "How will your journey unfold" copy
 * - Refund appears ONLY after tier summary
 * - Simplified sticky bar: Price + Start my journey only
 * - Remedies CTA = "Coming soon"
 */

// Tier levels
const TIER_LEVELS = ['Focussed', 'Supported', 'Comprehensive'];
const DEFAULT_TIER = 'Supported';

// Light pastel green background for better text visibility
const GRADIENT_BG = 'linear-gradient(180deg, #E8F5F3 0%, #F5FBF9 50%, #FFFEF5 100%)';
const CARD_BG = 'rgba(255, 255, 255, 0.85)';
const CARD_BORDER = 'rgba(0,0,0,0.06)';
const DIVIDER_COLOR = 'rgba(0,0,0,0.06)';

export default function TopicLandingPage({ token, topicId, onCheckout, onBack, onNavigate, hasBottomNav, userName }) {
  const [selectedTier, setSelectedTier] = useState(DEFAULT_TIER);
  const [expandedFaq, setExpandedFaq] = useState(null);

  // Get subtopic slug from topicId
  const subtopicSlug = useMemo(() => {
    return V6_TILE_TO_SUBTOPIC_MAP[topicId] || topicId;
  }, [topicId]);

  // Get V6 content for this subtopic
  const content = useMemo(() => {
    return getV6SubtopicBySlug(subtopicSlug);
  }, [subtopicSlug]);

  useEffect(() => {
    trackEvent('landing_viewed', { 
      tile_id: topicId, 
      subtopic_slug: subtopicSlug,
      selected_tier: selectedTier,
      version: 'v6'
    }, token);
  }, [topicId, subtopicSlug, selectedTier, token]);

  // Get tier-specific data
  const tierData = useMemo(() => {
    if (!content) return null;
    const tierCard = content.tierCards?.[selectedTier];
    const outcomes = content.outcomesByTier?.[selectedTier];
    const howUnfolds = content.howUnfoldsByTier?.[selectedTier];
    const tierSummary = content.tierSummaryDetails?.[selectedTier];
    return {
      price: tierCard?.priceInr || 0,
      durationWeeks: tierCard?.durationWeeks || 8,
      outcomes,
      howUnfolds,
      tierSummary,
    };
  }, [content, selectedTier]);

  // Handle checkout
  const handleCheckout = () => {
    const tierId = `${subtopicSlug}_${selectedTier.toLowerCase()}`;
    trackEvent('checkout_initiated', { 
      tile_id: topicId,
      tier_id: tierId,
      tier_name: selectedTier,
      price: tierData?.price,
    }, token);
    onCheckout(tierId, []);
  };

  // Format price
  const formatPrice = (price) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(price);
  };

  // Get display name
  const displayName = userName || 'there';

  // Get chat display text - ensure "Unlimited chat" exact wording
  const getChatDisplay = (followUps) => {
    if (!followUps) return 'Chat included';
    if (followUps.toLowerCase().includes('unlimited')) {
      return 'Unlimited chat';
    }
    return followUps;
  };

  // If no content found
  if (!content) {
    return (
      <div className="min-h-screen flex items-center justify-center p-6" style={{ background: GRADIENT_BG }}>
        <div className="text-center">
          <p style={{ color: colors.ui.error }} className="mb-4">Content not found for this topic</p>
          <button onClick={onBack} style={{ color: colors.teal.primary }} className="font-medium">
            Go back
          </button>
        </div>
      </div>
    );
  }

  // Get experts list from content or use default
  const experts = V6_EXPERTS;

  return (
    <div 
      className={`min-h-screen ${hasBottomNav ? 'pb-28' : 'pb-24'}`}
      style={{ background: GRADIENT_BG }}
    >
      {/* ===== HEADER ===== */}
      <header 
        className="sticky top-0 z-50 px-4 py-3 flex items-center gap-3"
        style={{ 
          background: 'linear-gradient(180deg, #F8FAF9 0%, rgba(248,250,249,0.98) 100%)',
          borderBottom: `1px solid ${DIVIDER_COLOR}`,
        }}
      >
        <button 
          onClick={onBack}
          className="p-2 -ml-2 rounded-full hover:bg-black/5 transition-colors"
          data-testid="landing-back-btn"
        >
          <ArrowLeftIcon className="w-5 h-5" style={{ color: colors.text.dark }} />
        </button>
        <h1 className="text-lg font-semibold flex-1 truncate" style={{ color: colors.text.dark }}>
          {content.headerTitle || content.topicKey}
        </h1>
      </header>

      {/* ===== HERO - One Line Promise ===== */}
      <section className="px-5 pt-4 pb-2">
        <p 
          className="text-sm text-center leading-relaxed"
          style={{ color: colors.text.dark }}
        >
          {content.heroOneLinePromise}
        </p>
      </section>

      {/* ===== PERSONALIZED GREETING ===== */}
      <section className="px-5 pt-2 pb-4">
        <h2 className="text-lg font-semibold text-center leading-relaxed" style={{ color: colors.text.dark }}>
          Hi {displayName}, here are the paths you can choose for your journey
        </h2>
      </section>

      {/* ===== TIER SELECTOR TABS ===== */}
      <section className="px-5 py-3">
        <div className="flex gap-2" data-testid="tier-selector-tabs">
          {TIER_LEVELS.map((tier) => {
            const isSelected = selectedTier === tier;
            const isRecommended = tier === 'Supported';
            const config = V6_TIER_CONFIG[tier];
            return (
              <button
                key={tier}
                onClick={() => setSelectedTier(tier)}
                className={`flex-1 py-3 px-2 rounded-xl transition-all relative flex flex-col items-center ${
                  isSelected ? 'shadow-sm' : ''
                }`}
                style={{
                  backgroundColor: isSelected ? colors.teal.primary : CARD_BG,
                  color: isSelected ? '#ffffff' : colors.text.secondary,
                  border: isSelected ? 'none' : `1px solid ${CARD_BORDER}`,
                }}
                data-testid={`tier-tab-${tier.toLowerCase()}`}
              >
                {/* Recommended badge ONLY on tier selector tabs */}
                {isRecommended && (
                  <span 
                    className="absolute -top-2.5 left-1/2 -translate-x-1/2 text-[9px] px-2 py-0.5 rounded-full font-semibold whitespace-nowrap"
                    style={{ 
                      backgroundColor: colors.gold.primary,
                      color: colors.text.dark,
                    }}
                  >
                    Recommended
                  </span>
                )}
                <span className="text-sm font-semibold">{tier}</span>
                <span className={`text-[10px] mt-0.5 ${isSelected ? 'opacity-80' : 'opacity-60'}`}>
                  {config.label}
                </span>
              </button>
            );
          })}
        </div>
      </section>

      {/* ===== TIER SUMMARY CARD (2x2 Grid Design) ===== */}
      <section className="px-5 py-2">
        <div 
          className="rounded-2xl p-5"
          style={{ 
            backgroundColor: CARD_BG,
            border: `1px solid ${CARD_BORDER}`,
            boxShadow: '0 2px 12px rgba(0,0,0,0.04)',
          }}
          data-testid="tier-summary-card"
        >
          {/* Tier Header - NO price shown here */}
          <div className="flex items-start justify-between mb-4">
            <div>
              <h3 className="text-lg font-bold" style={{ color: colors.text.dark }}>
                {selectedTier}
              </h3>
              <p className="text-sm" style={{ color: colors.text.secondary }}>
                {tierData?.durationWeeks} weeks package
              </p>
            </div>
          </div>

          {/* 2x2 Package Summary Grid */}
          <div className="grid grid-cols-2 gap-3 pt-4 border-t" style={{ borderColor: DIVIDER_COLOR }}>
            <div className="flex items-center gap-2.5">
              <div className="w-9 h-9 rounded-lg flex items-center justify-center" style={{ backgroundColor: `${colors.teal.primary}10` }}>
                <CalendarIcon className="w-4 h-4" style={{ color: colors.teal.primary }} />
              </div>
              <div>
                <p className="text-[11px] uppercase tracking-wide" style={{ color: colors.text.mutedDark }}>Duration</p>
                <p className="text-sm font-medium" style={{ color: colors.text.dark }}>
                  {tierData?.durationWeeks} weeks
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2.5">
              <div className="w-9 h-9 rounded-lg flex items-center justify-center" style={{ backgroundColor: `${colors.teal.primary}10` }}>
                <PhoneIcon className="w-4 h-4" style={{ color: colors.teal.primary }} />
              </div>
              <div>
                <p className="text-[11px] uppercase tracking-wide" style={{ color: colors.text.mutedDark }}>Consultation</p>
                <p className="text-sm font-medium" style={{ color: colors.text.dark }}>
                  {selectedTier === 'Comprehensive' ? '2 sessions' : '1 session'}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2.5">
              <div className="w-9 h-9 rounded-lg flex items-center justify-center" style={{ backgroundColor: `${colors.teal.primary}10` }}>
                <ClockIcon className="w-4 h-4" style={{ color: colors.teal.primary }} />
              </div>
              <div>
                <p className="text-[11px] uppercase tracking-wide" style={{ color: colors.text.mutedDark }}>Follow-ups</p>
                <p className="text-sm font-medium" style={{ color: colors.text.dark }}>
                  {selectedTier === 'Focussed' ? '1 call' : selectedTier === 'Supported' ? '2 calls' : '3 calls'}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2.5">
              <div className="w-9 h-9 rounded-lg flex items-center justify-center" style={{ backgroundColor: `${colors.teal.primary}10` }}>
                <ChatIcon className="w-4 h-4" style={{ color: colors.teal.primary }} />
              </div>
              <div>
                <p className="text-[11px] uppercase tracking-wide" style={{ color: colors.text.mutedDark }}>Chat</p>
                <p className="text-sm font-medium" style={{ color: colors.text.dark }}>
                  Unlimited
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ===== SATISFACTION GUARANTEE ===== */}
      <section className="px-5 py-3">
        <div 
          className="flex items-center justify-center gap-2 py-2.5 rounded-lg"
          style={{ backgroundColor: `${colors.teal.primary}08` }}
        >
          <CheckIcon className="w-4 h-4" style={{ color: colors.teal.primary }} />
          <span className="text-sm" style={{ color: colors.teal.primary }}>
            100% satisfaction guaranteed
          </span>
        </div>
      </section>

      {/* ===== DIVIDER ===== */}
      <div className="mx-5 my-3" style={{ borderBottom: `1px solid ${DIVIDER_COLOR}` }} />

      {/* ===== OUTCOMES SECTION ===== */}
      <section className="px-5 py-4">
        <h3 className="text-base font-semibold mb-4" style={{ color: colors.text.dark }}>
          What will this journey help you with?
        </h3>
        
        {/* Grouped outcomes: Clarity, Timeline, Support */}
        <div className="space-y-4">
          {/* Clarity Block */}
          <div>
            <p className="text-xs font-medium uppercase tracking-wide mb-2" style={{ color: colors.teal.primary }}>
              Clarity
            </p>
            <div className="space-y-2">
              {tierData?.outcomes?.clarity?.map((outcome, idx) => (
                <div key={idx} className="flex items-start gap-2.5">
                  <CheckIcon className="w-4 h-4 flex-shrink-0 mt-0.5" style={{ color: colors.teal.primary }} />
                  <p className="text-sm" style={{ color: colors.text.dark }}>{outcome}</p>
                </div>
              ))}
            </div>
          </div>
          
          {/* Timeline Block */}
          <div>
            <p className="text-xs font-medium uppercase tracking-wide mb-2" style={{ color: colors.teal.primary }}>
              Timeline
            </p>
            <div className="space-y-2">
              {tierData?.outcomes?.timeline?.map((outcome, idx) => (
                <div key={idx} className="flex items-start gap-2.5">
                  <CheckIcon className="w-4 h-4 flex-shrink-0 mt-0.5" style={{ color: colors.teal.primary }} />
                  <p className="text-sm" style={{ color: colors.text.dark }}>{outcome}</p>
                </div>
              ))}
            </div>
          </div>
          
          {/* Support Block */}
          <div>
            <p className="text-xs font-medium uppercase tracking-wide mb-2" style={{ color: colors.teal.primary }}>
              Support
            </p>
            <div className="space-y-2">
              {tierData?.outcomes?.support?.map((outcome, idx) => (
                <div key={idx} className="flex items-start gap-2.5">
                  <CheckIcon className="w-4 h-4 flex-shrink-0 mt-0.5" style={{ color: colors.teal.primary }} />
                  <p className="text-sm" style={{ color: colors.text.dark }}>{outcome}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* ===== DIVIDER ===== */}
      <div className="mx-5 my-3" style={{ borderBottom: `1px solid ${DIVIDER_COLOR}` }} />

      {/* ===== HOW WILL YOUR JOURNEY UNFOLD ===== */}
      <section className="px-5 py-4">
        <h3 className="text-base font-semibold mb-4" style={{ color: colors.text.dark }}>
          How will your journey unfold
        </h3>
        <div className="space-y-2">
          {tierData?.howUnfolds?.map((step, idx) => (
            <div key={idx} className="flex items-start gap-2.5">
              <CheckIcon className="w-4 h-4 flex-shrink-0 mt-0.5" style={{ color: colors.teal.primary }} />
              <p className="text-sm" style={{ color: colors.text.dark }}>{step}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ===== DIVIDER ===== */}
      <div className="mx-5 my-3" style={{ borderBottom: `1px solid ${DIVIDER_COLOR}` }} />

      {/* ===== EXPERTS WIDGET ===== */}
      <section className="py-4" data-testid="experts-widget">
        <h3 className="text-base font-semibold mb-1 px-5" style={{ color: colors.text.dark }}>
          {content.expertsWidgetTitle || 'Choose from Niro experts'}
        </h3>
        <p className="text-xs mb-4 px-5" style={{ color: colors.text.secondary }}>
          {content.expertsWidgetSubtitle || 'Verified specialists for this journey. Choose one to start — you can switch later.'}
        </p>
        <div className="flex gap-3 overflow-x-auto px-5 pb-2 scrollbar-hide">
          {experts.map((expert, idx) => (
            <div 
              key={idx}
              className="flex-shrink-0 w-44 rounded-xl p-4"
              style={{ 
                backgroundColor: CARD_BG,
                border: `1px solid ${CARD_BORDER}`,
              }}
              data-testid={`expert-card-${idx}`}
            >
              {/* Photo placeholder */}
              <div 
                className="w-12 h-12 rounded-full mb-3 flex items-center justify-center"
                style={{ backgroundColor: `${colors.teal.primary}15` }}
              >
                <span className="text-lg" style={{ color: colors.teal.primary }}>
                  {expert.role.charAt(0)}
                </span>
              </div>
              <h4 className="font-medium text-sm mb-1" style={{ color: colors.text.dark }}>
                {expert.role}
              </h4>
              <p className="text-[10px] mb-2" style={{ color: colors.teal.primary }}>
                {expert.badge}
              </p>
              <p className="text-xs mb-3" style={{ color: colors.text.secondary }}>
                {expert.focus}
              </p>
              <button 
                className="text-xs font-medium px-3 py-1.5 rounded-lg"
                style={{ 
                  backgroundColor: `${colors.teal.primary}10`,
                  color: colors.teal.primary,
                }}
              >
                View profile
              </button>
            </div>
          ))}
        </div>
      </section>

      {/* ===== DIVIDER ===== */}
      <div className="mx-5 my-3" style={{ borderBottom: `1px solid ${DIVIDER_COLOR}` }} />

      {/* ===== OPTIONAL ADD-ONS (Coming Soon) ===== */}
      <section className="py-4" data-testid="remedies-section">
        <h3 className="text-base font-semibold mb-3 px-5" style={{ color: colors.text.dark }}>
          {content.remediesTitle || 'Optional add-ons (Coming soon)'}
        </h3>
        <div className="px-5">
          <div 
            className="rounded-xl p-4 flex items-center justify-center"
            style={{ 
              backgroundColor: CARD_BG,
              border: `1px solid ${CARD_BORDER}`,
            }}
          >
            <div className="text-center">
              <div className="w-10 h-10 rounded-full mx-auto mb-2 flex items-center justify-center" style={{ backgroundColor: `${colors.text.mutedDark}10` }}>
                <GiftIcon className="w-5 h-5" style={{ color: colors.text.mutedDark }} />
              </div>
              <p className="text-sm mb-2" style={{ color: colors.text.secondary }}>
                Topic-specific remedies and add-ons
              </p>
              {/* Remedy CTA = "Coming soon" - strict */}
              <span 
                className="inline-block text-xs px-3 py-1.5 rounded-full font-medium"
                style={{ 
                  backgroundColor: `${colors.text.mutedDark}15`,
                  color: colors.text.mutedDark,
                }}
                data-testid="remedies-coming-soon"
              >
                Coming soon
              </span>
            </div>
          </div>
        </div>
      </section>

      {/* ===== DIVIDER ===== */}
      <div className="mx-5 my-3" style={{ borderBottom: `1px solid ${DIVIDER_COLOR}` }} />

      {/* ===== WHY NIRO (Trust Section) ===== */}
      <section className="px-5 py-4">
        <h3 className="text-base font-semibold mb-4" style={{ color: colors.text.dark }}>
          Why Niro?
        </h3>
        <div className="space-y-3">
          {(content.whyNiroBullets || [
            'Real astrologers (not generic reports) — across Vedic, Tarot, Numerology & more',
            'Unlimited follow-ups in Supported & Comprehensive packs',
            'Clear outcomes: patterns, timing, and what to expect next (no jargon)',
            'Private, secure, and designed for a judgement-free experience',
            '100% satisfaction guaranteed'
          ]).map((bullet, idx) => (
            <div key={idx} className="flex items-start gap-3">
              <CheckIcon className="w-4 h-4 flex-shrink-0 mt-0.5" style={{ color: colors.teal.primary }} />
              <p className="text-sm" style={{ color: colors.text.dark }}>{bullet}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ===== DIVIDER ===== */}
      <div className="mx-5 my-3" style={{ borderBottom: `1px solid ${DIVIDER_COLOR}` }} />

      {/* ===== FAQs ===== */}
      <section className="px-5 py-4 mb-6">
        <h3 className="text-base font-semibold mb-4" style={{ color: colors.text.dark }}>
          Frequently Asked Questions
        </h3>
        <div className="space-y-2">
          {(content.faqs || []).slice(0, 6).map((faq, idx) => (
            <div 
              key={idx}
              className="rounded-xl overflow-hidden"
              style={{ 
                backgroundColor: CARD_BG, 
                border: `1px solid ${CARD_BORDER}`,
              }}
            >
              <button
                onClick={() => setExpandedFaq(expandedFaq === idx ? null : idx)}
                className="w-full p-4 flex items-center justify-between text-left"
                data-testid={`faq-item-${idx}`}
              >
                <span className="font-medium text-sm pr-4" style={{ color: colors.text.dark }}>
                  {faq.q}
                </span>
                <ChevronRightIcon 
                  className={`w-5 h-5 flex-shrink-0 transition-transform ${expandedFaq === idx ? 'rotate-90' : ''}`} 
                  style={{ color: colors.text.mutedDark }} 
                />
              </button>
              {expandedFaq === idx && (
                <div className="px-4 pb-4">
                  <p className="text-sm leading-relaxed" style={{ color: colors.text.secondary }}>{faq.a}</p>
                </div>
              )}
            </div>
          ))}
        </div>
      </section>

      {/* ===== STICKY CTA BAR (Simplified - Price + Start my journey ONLY) ===== */}
      <div 
        className={`fixed ${hasBottomNav ? 'bottom-16' : 'bottom-0'} left-0 right-0 z-50`}
        style={{ 
          backgroundColor: CARD_BG,
          borderTop: `1px solid ${CARD_BORDER}`,
          boxShadow: '0 -2px 16px rgba(0,0,0,0.06)',
          backdropFilter: 'blur(12px)',
        }}
        data-testid="sticky-cta-bar"
      >
        <div className="px-5 py-4 flex items-center justify-between">
          {/* Left: Price only */}
          <span className="text-xl font-bold" style={{ color: colors.text.dark }}>
            {formatPrice(tierData?.price || 0)}
          </span>
          
          {/* Right: Start my journey CTA only */}
          <button
            onClick={handleCheckout}
            className="px-8 py-3 rounded-xl font-semibold text-base transition-all active:scale-[0.98]"
            style={{ 
              backgroundColor: colors.teal.primary,
              color: '#ffffff',
            }}
            data-testid="start-journey-btn"
          >
            Start my journey
          </button>
        </div>
      </div>
    </div>
  );
}
