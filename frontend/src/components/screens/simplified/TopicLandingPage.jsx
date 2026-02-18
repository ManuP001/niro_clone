import React, { useState, useEffect, useMemo } from 'react';
import { colors, shadows } from './theme';
import { 
  CheckIcon, 
  ChevronRightIcon,
  ClockIcon,
  CalendarIcon,
  ChatIcon,
  GiftIcon,
  PhoneIcon
} from './icons';
import { trackEvent } from './utils';
import ResponsiveHeader from './ResponsiveHeader';

// Import V6 content
import { 
  getV6SubtopicBySlug,
  V6_TILE_TO_SUBTOPIC_MAP,
  V6_TIER_CONFIG,
  V6_EXPERTS
} from './v6Data/landingPageContentV6';

/**
 * TopicLandingPage V7 - Redesigned to match homepage aesthetic
 * 
 * Key Changes:
 * - ResponsiveHeader integration
 * - Cream background with white cards
 * - Pill-shaped tier selector tabs
 * - Card-based sections with shadows
 * - Better responsive typography
 * - Consistent spacing and borders
 */

// Tier levels
const TIER_LEVELS = ['Focussed', 'Supported', 'Comprehensive'];
const DEFAULT_TIER = 'Supported';

export default function TopicLandingPage({ token, topicId, onCheckout, onBack, onNavigate, hasBottomNav, userName, onTabChange }) {
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
      version: 'v7'
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

  // If no content found
  if (!content) {
    return (
      <div 
        className="min-h-screen flex items-center justify-center p-6"
        style={{ backgroundColor: colors.background.primary }}
      >
        <div className="text-center">
          <p style={{ color: colors.ui.error }} className="mb-4">Content not found for this topic</p>
          <button onClick={onBack} style={{ color: colors.teal.primary }} className="font-medium">
            Go back
          </button>
        </div>
      </div>
    );
  }

  // Get experts list
  const experts = V6_EXPERTS;

  return (
    <div 
      className={`min-h-screen ${hasBottomNav ? 'pb-32 md:pb-28' : 'pb-28'}`}
      style={{ backgroundColor: colors.background.primary }}
    >
      {/* Responsive Header */}
      <ResponsiveHeader
        title={content.headerTitle || content.topicKey}
        showBackButton={true}
        onBack={onBack}
        onNavigate={onNavigate}
        onTabChange={onTabChange}
        ctaText="📞 Get a free 10 mins consultation"
      />

      {/* Main Content Container */}
      <div className="max-w-4xl mx-auto">
        {/* Hero Section */}
        <section className="px-4 md:px-8 pt-6 pb-4 text-center">
          <p 
            className="text-base md:text-lg leading-relaxed max-w-2xl mx-auto"
            style={{ color: colors.text.secondary }}
          >
            {content.heroOneLinePromise}
          </p>
        </section>

        {/* Personalized Greeting */}
        <section className="px-4 md:px-8 py-4 text-center">
          <h1 
            className="text-xl md:text-2xl lg:text-3xl font-bold"
            style={{ color: colors.text.dark }}
          >
            Hi {displayName}, choose your <span style={{ color: colors.teal.primary }}>journey</span>
          </h1>
        </section>

        {/* Tier Selector Tabs */}
        <section className="px-4 md:px-8 py-4">
          <div 
            className="flex gap-2 md:gap-3 p-1.5 rounded-full"
            style={{ backgroundColor: '#ffffff', boxShadow: shadows.card }}
            data-testid="tier-selector-tabs"
          >
            {TIER_LEVELS.map((tier) => {
              const isSelected = selectedTier === tier;
              const isRecommended = tier === 'Supported';
              const config = V6_TIER_CONFIG[tier];
              return (
                <button
                  key={tier}
                  onClick={() => setSelectedTier(tier)}
                  className={`flex-1 py-3 md:py-4 px-2 md:px-4 rounded-full transition-all relative flex flex-col items-center`}
                  style={{
                    backgroundColor: isSelected ? colors.teal.primary : 'transparent',
                    color: isSelected ? '#ffffff' : colors.text.secondary,
                  }}
                  data-testid={`tier-tab-${tier.toLowerCase()}`}
                >
                  {/* Recommended badge */}
                  {isRecommended && (
                    <span 
                      className="absolute -top-3 left-1/2 -translate-x-1/2 text-[9px] md:text-[10px] px-2.5 py-0.5 rounded-full font-semibold whitespace-nowrap"
                      style={{ 
                        backgroundColor: colors.peach.primary,
                        color: colors.text.dark,
                      }}
                    >
                      Recommended
                    </span>
                  )}
                  <span className="text-sm md:text-base font-semibold">{tier}</span>
                  <span className={`text-[10px] md:text-xs mt-0.5 ${isSelected ? 'opacity-80' : 'opacity-60'}`}>
                    {config.label}
                  </span>
                </button>
              );
            })}
          </div>
        </section>

        {/* Tier Summary Card */}
        <section className="px-4 md:px-8 py-4">
          <div 
            className="rounded-2xl p-5 md:p-6"
            style={{ 
              backgroundColor: '#ffffff',
              boxShadow: shadows.card,
              border: `1px solid ${colors.ui.borderDark}`,
            }}
            data-testid="tier-summary-card"
          >
            {/* Tier Header */}
            <div className="flex items-start justify-between mb-5">
              <div>
                <h2 className="text-xl md:text-2xl font-bold" style={{ color: colors.text.dark }}>
                  {selectedTier}
                </h2>
                <p className="text-sm md:text-base" style={{ color: colors.text.secondary }}>
                  {tierData?.durationWeeks} weeks package
                </p>
              </div>
              <div className="text-right">
                <p className="text-2xl md:text-3xl font-bold" style={{ color: colors.teal.primary }}>
                  {formatPrice(tierData?.price || 0)}
                </p>
              </div>
            </div>

            {/* 2x2 Package Summary Grid */}
            <div className="grid grid-cols-2 gap-4 pt-5 border-t" style={{ borderColor: colors.ui.borderDark }}>
              <div className="flex items-center gap-3">
                <div 
                  className="w-10 h-10 md:w-12 md:h-12 rounded-xl flex items-center justify-center"
                  style={{ backgroundColor: `${colors.teal.primary}10` }}
                >
                  <CalendarIcon className="w-5 h-5 md:w-6 md:h-6" style={{ color: colors.teal.primary }} />
                </div>
                <div>
                  <p className="text-[10px] md:text-xs uppercase tracking-wide font-medium" style={{ color: colors.text.muted }}>Duration</p>
                  <p className="text-sm md:text-base font-semibold" style={{ color: colors.text.dark }}>
                    {tierData?.durationWeeks} weeks
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <div 
                  className="w-10 h-10 md:w-12 md:h-12 rounded-xl flex items-center justify-center"
                  style={{ backgroundColor: `${colors.teal.primary}10` }}
                >
                  <PhoneIcon className="w-5 h-5 md:w-6 md:h-6" style={{ color: colors.teal.primary }} />
                </div>
                <div>
                  <p className="text-[10px] md:text-xs uppercase tracking-wide font-medium" style={{ color: colors.text.muted }}>Consultation</p>
                  <p className="text-sm md:text-base font-semibold" style={{ color: colors.text.dark }}>
                    {selectedTier === 'Comprehensive' ? '2 sessions' : '1 session'}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <div 
                  className="w-10 h-10 md:w-12 md:h-12 rounded-xl flex items-center justify-center"
                  style={{ backgroundColor: `${colors.teal.primary}10` }}
                >
                  <ClockIcon className="w-5 h-5 md:w-6 md:h-6" style={{ color: colors.teal.primary }} />
                </div>
                <div>
                  <p className="text-[10px] md:text-xs uppercase tracking-wide font-medium" style={{ color: colors.text.muted }}>Follow-ups</p>
                  <p className="text-sm md:text-base font-semibold" style={{ color: colors.text.dark }}>
                    {selectedTier === 'Focussed' ? '1 call' : selectedTier === 'Supported' ? '2 calls' : '3 calls'}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <div 
                  className="w-10 h-10 md:w-12 md:h-12 rounded-xl flex items-center justify-center"
                  style={{ backgroundColor: `${colors.teal.primary}10` }}
                >
                  <ChatIcon className="w-5 h-5 md:w-6 md:h-6" style={{ color: colors.teal.primary }} />
                </div>
                <div>
                  <p className="text-[10px] md:text-xs uppercase tracking-wide font-medium" style={{ color: colors.text.muted }}>Chat</p>
                  <p className="text-sm md:text-base font-semibold" style={{ color: colors.text.dark }}>
                    Unlimited
                  </p>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Satisfaction Guarantee */}
        <section className="px-4 md:px-8 py-3">
          <div 
            className="flex items-center justify-center gap-2 py-3 rounded-full"
            style={{ backgroundColor: `${colors.teal.primary}08` }}
          >
            <CheckIcon className="w-5 h-5" style={{ color: colors.teal.primary }} />
            <span className="text-sm md:text-base font-medium" style={{ color: colors.teal.primary }}>
              100% satisfaction guaranteed
            </span>
          </div>
        </section>

        {/* Outcomes Section */}
        <section className="px-4 md:px-8 py-6">
          <h2 className="text-lg md:text-xl font-bold mb-5" style={{ color: colors.text.dark }}>
            What will this journey help you with?
          </h2>
          
          {/* Grouped outcomes: Clarity, Timeline, Support */}
          <div className="grid md:grid-cols-3 gap-4 md:gap-6">
            {/* Clarity Block */}
            <div 
              className="rounded-xl p-5"
              style={{ backgroundColor: '#ffffff', boxShadow: shadows.card }}
            >
              <p 
                className="text-xs font-semibold uppercase tracking-wider mb-3 pb-2 border-b"
                style={{ color: colors.teal.primary, borderColor: colors.ui.borderDark }}
              >
                Clarity
              </p>
              <div className="space-y-3">
                {tierData?.outcomes?.clarity?.map((outcome, idx) => (
                  <div key={idx} className="flex items-start gap-2.5">
                    <CheckIcon className="w-4 h-4 flex-shrink-0 mt-0.5" style={{ color: colors.teal.primary }} />
                    <p className="text-sm" style={{ color: colors.text.secondary }}>{outcome}</p>
                  </div>
                ))}
              </div>
            </div>
            
            {/* Timeline Block */}
            <div 
              className="rounded-xl p-5"
              style={{ backgroundColor: '#ffffff', boxShadow: shadows.card }}
            >
              <p 
                className="text-xs font-semibold uppercase tracking-wider mb-3 pb-2 border-b"
                style={{ color: colors.teal.primary, borderColor: colors.ui.borderDark }}
              >
                Timeline
              </p>
              <div className="space-y-3">
                {tierData?.outcomes?.timeline?.map((outcome, idx) => (
                  <div key={idx} className="flex items-start gap-2.5">
                    <CheckIcon className="w-4 h-4 flex-shrink-0 mt-0.5" style={{ color: colors.teal.primary }} />
                    <p className="text-sm" style={{ color: colors.text.secondary }}>{outcome}</p>
                  </div>
                ))}
              </div>
            </div>
            
            {/* Support Block */}
            <div 
              className="rounded-xl p-5"
              style={{ backgroundColor: '#ffffff', boxShadow: shadows.card }}
            >
              <p 
                className="text-xs font-semibold uppercase tracking-wider mb-3 pb-2 border-b"
                style={{ color: colors.teal.primary, borderColor: colors.ui.borderDark }}
              >
                Support
              </p>
              <div className="space-y-3">
                {tierData?.outcomes?.support?.map((outcome, idx) => (
                  <div key={idx} className="flex items-start gap-2.5">
                    <CheckIcon className="w-4 h-4 flex-shrink-0 mt-0.5" style={{ color: colors.teal.primary }} />
                    <p className="text-sm" style={{ color: colors.text.secondary }}>{outcome}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>

        {/* How Will Your Journey Unfold */}
        <section className="px-4 md:px-8 py-6">
          <h2 className="text-lg md:text-xl font-bold mb-5" style={{ color: colors.text.dark }}>
            How will your journey unfold
          </h2>
          <div 
            className="rounded-xl p-5 md:p-6"
            style={{ backgroundColor: '#ffffff', boxShadow: shadows.card }}
          >
            <div className="space-y-4">
              {tierData?.howUnfolds?.map((step, idx) => (
                <div key={idx} className="flex items-start gap-4">
                  <div 
                    className="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 text-sm font-bold"
                    style={{ backgroundColor: `${colors.teal.primary}15`, color: colors.teal.primary }}
                  >
                    {idx + 1}
                  </div>
                  <p className="text-sm md:text-base pt-1" style={{ color: colors.text.secondary }}>{step}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Experts Widget */}
        <section className="py-6" data-testid="experts-widget">
          <div className="px-4 md:px-8 mb-4">
            <h2 className="text-lg md:text-xl font-bold mb-1" style={{ color: colors.text.dark }}>
              {content.expertsWidgetTitle || 'Choose from Niro experts'}
            </h2>
            <p className="text-sm md:text-base" style={{ color: colors.text.secondary }}>
              {content.expertsWidgetSubtitle || 'Verified specialists for this journey. Choose one to start — you can switch later.'}
            </p>
          </div>
          <div className="flex gap-4 overflow-x-auto px-4 md:px-8 pb-2 scrollbar-hide">
            {experts.map((expert, idx) => (
              <div 
                key={idx}
                className="flex-shrink-0 w-48 md:w-56 rounded-xl p-4"
                style={{ 
                  backgroundColor: '#ffffff',
                  boxShadow: shadows.card,
                }}
                data-testid={`expert-card-${idx}`}
              >
                {/* Photo placeholder */}
                <div 
                  className="w-14 h-14 md:w-16 md:h-16 rounded-full mb-3 flex items-center justify-center"
                  style={{ backgroundColor: `${colors.teal.primary}15` }}
                >
                  <span className="text-xl md:text-2xl font-bold" style={{ color: colors.teal.primary }}>
                    {expert.role.charAt(0)}
                  </span>
                </div>
                <h4 className="font-semibold text-sm md:text-base mb-1" style={{ color: colors.text.dark }}>
                  {expert.role}
                </h4>
                <p className="text-xs mb-2" style={{ color: colors.teal.primary }}>
                  {expert.badge}
                </p>
                <p className="text-xs md:text-sm mb-3 line-clamp-2" style={{ color: colors.text.secondary }}>
                  {expert.focus}
                </p>
                <button 
                  className="text-xs md:text-sm font-medium px-4 py-2 rounded-full transition-all hover:shadow-sm"
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

        {/* Optional Add-ons (Coming Soon) */}
        <section className="px-4 md:px-8 py-6" data-testid="remedies-section">
          <h2 className="text-lg md:text-xl font-bold mb-4" style={{ color: colors.text.dark }}>
            {content.remediesTitle || 'Optional add-ons'}
          </h2>
          <div 
            className="rounded-xl p-6 md:p-8 flex flex-col items-center justify-center"
            style={{ 
              backgroundColor: '#ffffff',
              boxShadow: shadows.card,
              border: `2px dashed ${colors.ui.borderDark}`,
            }}
          >
            <div 
              className="w-12 h-12 md:w-14 md:h-14 rounded-full mb-3 flex items-center justify-center"
              style={{ backgroundColor: `${colors.text.muted}10` }}
            >
              <GiftIcon className="w-6 h-6 md:w-7 md:h-7" style={{ color: colors.text.muted }} />
            </div>
            <p className="text-sm md:text-base mb-3 text-center" style={{ color: colors.text.secondary }}>
              Topic-specific remedies and add-ons
            </p>
            <span 
              className="text-xs md:text-sm px-4 py-1.5 rounded-full font-medium"
              style={{ 
                backgroundColor: colors.peach.soft,
                color: colors.text.dark,
              }}
              data-testid="remedies-coming-soon"
            >
              Coming soon
            </span>
          </div>
        </section>

        {/* Why Niro */}
        <section className="px-4 md:px-8 py-6">
          <h2 className="text-lg md:text-xl font-bold mb-5" style={{ color: colors.text.dark }}>
            Why Niro?
          </h2>
          <div 
            className="rounded-xl p-5 md:p-6"
            style={{ backgroundColor: '#ffffff', boxShadow: shadows.card }}
          >
            <div className="space-y-4">
              {(content.whyNiroBullets || [
                'Real astrologers (not generic reports) — across Vedic, Tarot, Numerology & more',
                'Unlimited follow-ups in Supported & Comprehensive packs',
                'Clear outcomes: patterns, timing, and what to expect next (no jargon)',
                'Private, secure, and designed for a judgement-free experience',
                '100% satisfaction guaranteed'
              ]).map((bullet, idx) => (
                <div key={idx} className="flex items-start gap-3">
                  <CheckIcon className="w-5 h-5 flex-shrink-0 mt-0.5" style={{ color: colors.teal.primary }} />
                  <p className="text-sm md:text-base" style={{ color: colors.text.secondary }}>{bullet}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* FAQs */}
        <section className="px-4 md:px-8 py-6 mb-6">
          <h2 className="text-lg md:text-xl font-bold mb-5" style={{ color: colors.text.dark }}>
            Frequently Asked Questions
          </h2>
          <div className="grid md:grid-cols-2 gap-3 md:gap-4">
            {(content.faqs || []).slice(0, 6).map((faq, idx) => (
              <div 
                key={idx}
                className="rounded-xl overflow-hidden"
                style={{ 
                  backgroundColor: '#ffffff', 
                  boxShadow: shadows.card,
                }}
              >
                <button
                  onClick={() => setExpandedFaq(expandedFaq === idx ? null : idx)}
                  className="w-full p-4 flex items-center justify-between text-left hover:bg-black/[0.02] transition-colors"
                  data-testid={`faq-item-${idx}`}
                >
                  <span className="font-medium text-sm md:text-base pr-4" style={{ color: colors.text.dark }}>
                    {faq.q}
                  </span>
                  <ChevronRightIcon 
                    className={`w-5 h-5 flex-shrink-0 transition-transform duration-200 ${expandedFaq === idx ? 'rotate-90' : ''}`} 
                    style={{ color: colors.text.muted }} 
                  />
                </button>
                {expandedFaq === idx && (
                  <div className="px-4 pb-4">
                    <p className="text-sm md:text-base leading-relaxed" style={{ color: colors.text.secondary }}>
                      {faq.a}
                    </p>
                  </div>
                )}
              </div>
            ))}
          </div>
        </section>
      </div>

      {/* Sticky CTA Bar */}
      <div 
        className={`fixed ${hasBottomNav ? 'bottom-16 md:bottom-0' : 'bottom-0'} left-0 right-0 z-50`}
        style={{ 
          backgroundColor: 'rgba(251, 248, 243, 0.95)',
          backdropFilter: 'blur(12px)',
          borderTop: `1px solid ${colors.ui.borderDark}`,
          boxShadow: '0 -4px 20px rgba(0, 0, 0, 0.08)',
        }}
        data-testid="sticky-cta-bar"
      >
        <div className="max-w-4xl mx-auto px-4 md:px-8 py-4 flex items-center justify-between gap-4">
          {/* Price */}
          <div>
            <p className="text-xl md:text-2xl font-bold" style={{ color: colors.text.dark }}>
              {formatPrice(tierData?.price || 0)}
            </p>
            <p className="text-xs md:text-sm" style={{ color: colors.text.muted }}>
              {tierData?.durationWeeks} weeks package
            </p>
          </div>
          
          {/* CTA */}
          <button
            onClick={handleCheckout}
            className="px-6 md:px-10 py-3 md:py-4 rounded-full font-semibold text-base transition-all active:scale-[0.98] hover:shadow-lg hover:-translate-y-0.5"
            style={{ 
              backgroundColor: colors.peach.primary,
              color: colors.text.dark,
              boxShadow: shadows.peach,
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
