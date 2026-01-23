import React, { useState, useEffect, useMemo } from 'react';
import { colors, shadows } from './theme';
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

// Import content from v5Data
import { 
  getSubtopicBySlug,
} from './v5Data/landingPageContent';

/**
 * TopicLandingPage - V4 Landing Page (Premium Minimal Design)
 * 
 * Design Rules:
 * - ONE base background color across entire page
 * - TWO container styles: standard card + highlighted card
 * - Differentiate sections via spacing, dividers, typography
 * - No rainbow section backgrounds
 */

// Tier configuration with micro-labels
const TIER_CONFIG = {
  'Focussed': { label: 'Quick clarity', sessions: '1 call', followups: '1 follow-up', chat: '7 days' },
  'Supported': { label: 'Full support', sessions: '3 calls', followups: '2 follow-ups', chat: 'Unlimited' },
  'Comprehensive': { label: 'Deep confidence', sessions: '5 calls', followups: '3+ follow-ups', chat: 'Unlimited' },
};
const TIER_LEVELS = ['Focussed', 'Supported', 'Comprehensive'];
const DEFAULT_TIER = 'Supported';

// Map old tile IDs to new subtopic slugs
const TILE_TO_SUBTOPIC_MAP = {
  'relationship_healing': 'relationship-healing',
  'family_relationships': 'family-relationships',
  'dating_compatibility': 'dating-compatibility',
  'marriage_planning': 'marriage-planning',
  'communication_trust': 'communication-trust',
  'breakup_closure': 'breakup-closure',
  'career_clarity': 'career-clarity',
  'job_transition': 'job-transition',
  'money_stability': 'money-stability',
  'work_stress': 'work-stress',
  'office_politics': 'office-politics',
  'big_decision_timing': 'big-decision-timing',
  'healing_journey': 'healing-journey',
  'stress_management': 'stress-management',
  'energy_balance': 'energy-balance',
  'sleep_reset': 'sleep-reset',
  'emotional_recovery': 'emotional-recovery',
  'womens_wellness': 'womens-wellness',
};

// Objection-killer FAQs (conversion focused)
const CONVERSION_FAQS = [
  { q: 'When will my first consult happen?', a: 'Within 24 hours of purchase, you\'ll be matched with an expert and can schedule your first call at a time that works for you.' },
  { q: 'Is chat really unlimited?', a: 'Yes! For Supported and Comprehensive packs, you get unlimited chat access with your astrologer for the entire pack duration. Focussed includes 7 days of chat.' },
  { q: 'What happens after I pay?', a: 'You\'ll receive instant confirmation via WhatsApp/email with next steps. Your expert match happens within 24 hours, and you can start chatting right away.' },
  { q: 'What if I don\'t feel it helped?', a: 'We offer a no-questions-asked 7-day full refund guarantee. If you\'re not satisfied for any reason, just let us know.' },
  { q: 'How does the 7-day refund work?', a: 'Simply reach out within 7 days of purchase if you\'re not satisfied. We\'ll process a full refund—no questions asked, no hassle.' },
  { q: 'Are experts verified?', a: 'Absolutely. Every expert on Niro goes through a rigorous verification process. We check credentials, experience, and conduct multiple rounds of vetting.' },
];

// Base styling constants
const BASE_BG = '#FAFAFA';
const CARD_BG = '#FFFFFF';
const CARD_BORDER = 'rgba(0,0,0,0.06)';
const DIVIDER_COLOR = 'rgba(0,0,0,0.06)';

export default function TopicLandingPage({ token, topicId, onCheckout, onBack, onNavigate, hasBottomNav, userName }) {
  const [selectedTier, setSelectedTier] = useState(DEFAULT_TIER);
  const [expandedFaq, setExpandedFaq] = useState(null);

  // Get subtopic slug from topicId
  const subtopicSlug = useMemo(() => {
    return TILE_TO_SUBTOPIC_MAP[topicId] || topicId;
  }, [topicId]);

  // Get content for this subtopic
  const content = useMemo(() => {
    return getSubtopicBySlug(subtopicSlug);
  }, [subtopicSlug]);

  useEffect(() => {
    trackEvent('landing_viewed', { 
      tile_id: topicId, 
      subtopic_slug: subtopicSlug,
      selected_tier: selectedTier 
    }, token);
  }, [topicId, subtopicSlug, selectedTier, token]);

  // Get tier-specific data
  const tierData = useMemo(() => {
    if (!content) return null;
    const tierCard = content.tierCards?.[selectedTier];
    const tierFeatures = content.featuresByTier?.[selectedTier];
    return {
      price: tierCard?.priceInr || 0,
      duration: tierCard?.durationWeeks || 8,
      ...tierFeatures,
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

  // Get tier summary for sticky CTA
  const getTierSummary = () => {
    const config = TIER_CONFIG[selectedTier];
    return `${config.sessions} + follow-ups + ${config.chat.toLowerCase()} chat`;
  };

  // If no content found
  if (!content) {
    return (
      <div className="min-h-screen flex items-center justify-center p-6" style={{ backgroundColor: BASE_BG }}>
        <div className="text-center">
          <p style={{ color: colors.ui.error }} className="mb-4">Content not found for this topic</p>
          <button onClick={onBack} style={{ color: colors.teal.primary }} className="font-medium">
            Go back
          </button>
        </div>
      </div>
    );
  }

  const hasRemedies = content.optionalRemedies && content.optionalRemedies.length > 0;

  return (
    <div 
      className={`min-h-screen ${hasBottomNav ? 'pb-28' : 'pb-24'}`}
      style={{ backgroundColor: BASE_BG }}
    >
      {/* ===== HEADER ===== */}
      <header 
        className="sticky top-0 z-50 px-4 py-3 flex items-center gap-3"
        style={{ 
          backgroundColor: BASE_BG,
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
          {content.subTopic}
        </h1>
      </header>

      {/* ===== HERO - Personalized Greeting ===== */}
      <section className="px-5 pt-6 pb-4">
        <h2 className="text-xl font-semibold text-center leading-relaxed" style={{ color: colors.text.dark }}>
          Hi {displayName}, here are the paths you can choose for your journey
        </h2>
      </section>

      {/* ===== TIER SELECTOR TABS ===== */}
      <section className="px-5 py-4">
        <div className="flex gap-2" data-testid="tier-selector-tabs">
          {TIER_LEVELS.map((tier) => {
            const isSelected = selectedTier === tier;
            const isRecommended = tier === 'Supported';
            const config = TIER_CONFIG[tier];
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

      {/* ===== TIER SUMMARY CARD (Highlighted) ===== */}
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
          {/* Tier Header */}
          <div className="flex items-start justify-between mb-4">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <h3 className="text-lg font-bold" style={{ color: colors.text.dark }}>
                  {selectedTier}
                </h3>
                {selectedTier === 'Supported' && (
                  <span 
                    className="text-[9px] px-2 py-0.5 rounded-full font-semibold"
                    style={{ 
                      backgroundColor: colors.gold.primary,
                      color: colors.text.dark,
                    }}
                  >
                    Recommended
                  </span>
                )}
              </div>
              <p className="text-sm" style={{ color: colors.text.secondary }}>
                {tierData?.duration} weeks
              </p>
            </div>
            <div className="text-right">
              <p className="text-2xl font-bold" style={{ color: colors.text.dark }}>
                {formatPrice(tierData?.price || 0)}
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
                <p className="text-sm font-medium" style={{ color: colors.text.dark }}>{tierData?.duration} weeks</p>
              </div>
            </div>
            <div className="flex items-center gap-2.5">
              <div className="w-9 h-9 rounded-lg flex items-center justify-center" style={{ backgroundColor: `${colors.teal.primary}10` }}>
                <PhoneIcon className="w-4 h-4" style={{ color: colors.teal.primary }} />
              </div>
              <div>
                <p className="text-[11px] uppercase tracking-wide" style={{ color: colors.text.mutedDark }}>Consultation</p>
                <p className="text-sm font-medium" style={{ color: colors.text.dark }}>{TIER_CONFIG[selectedTier].sessions}</p>
              </div>
            </div>
            <div className="flex items-center gap-2.5">
              <div className="w-9 h-9 rounded-lg flex items-center justify-center" style={{ backgroundColor: `${colors.teal.primary}10` }}>
                <ClockIcon className="w-4 h-4" style={{ color: colors.teal.primary }} />
              </div>
              <div>
                <p className="text-[11px] uppercase tracking-wide" style={{ color: colors.text.mutedDark }}>Follow-ups</p>
                <p className="text-sm font-medium" style={{ color: colors.text.dark }}>{TIER_CONFIG[selectedTier].followups}</p>
              </div>
            </div>
            <div className="flex items-center gap-2.5">
              <div className="w-9 h-9 rounded-lg flex items-center justify-center" style={{ backgroundColor: `${colors.teal.primary}10` }}>
                <ChatIcon className="w-4 h-4" style={{ color: colors.teal.primary }} />
              </div>
              <div>
                <p className="text-[11px] uppercase tracking-wide" style={{ color: colors.text.mutedDark }}>Chat</p>
                <p className="text-sm font-medium" style={{ color: colors.text.dark }}>{TIER_CONFIG[selectedTier].chat}</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ===== REFUND GUARANTEE (Trust Strip) ===== */}
      <section className="px-5 py-3">
        <div 
          className="flex items-center justify-center gap-2 py-2.5 rounded-lg"
          style={{ backgroundColor: `${colors.teal.primary}08` }}
        >
          <CheckIcon className="w-4 h-4" style={{ color: colors.teal.primary }} />
          <span className="text-sm" style={{ color: colors.teal.primary }}>
            No questions asked — 7 day full refund guarantee
          </span>
        </div>
      </section>

      {/* ===== DIVIDER ===== */}
      <div className="mx-5 my-4" style={{ borderBottom: `1px solid ${DIVIDER_COLOR}` }} />

      {/* ===== OUTCOMES SECTION (No colored backgrounds) ===== */}
      <section className="px-5 py-4">
        <h3 className="text-base font-semibold mb-4" style={{ color: colors.text.dark }}>
          What will this journey help you with?
        </h3>
        
        {/* Grouped outcomes: Clarity, Timeline, Confidence */}
        <div className="space-y-4">
          {/* Clarity Block */}
          <div>
            <p className="text-xs font-medium uppercase tracking-wide mb-2" style={{ color: colors.teal.primary }}>
              Clarity
            </p>
            <div className="space-y-2">
              {tierData?.outcomes?.slice(0, 3).map((outcome, idx) => (
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
              {tierData?.outcomes?.slice(3, 5).map((outcome, idx) => (
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
              {tierData?.outcomes?.slice(5, 7).map((outcome, idx) => (
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
      <div className="mx-5 my-4" style={{ borderBottom: `1px solid ${DIVIDER_COLOR}` }} />

      {/* ===== HOW WILL YOUR JOURNEY UNFOLD (4-Step Timeline) ===== */}
      <section className="px-5 py-4">
        <h3 className="text-base font-semibold mb-4" style={{ color: colors.text.dark }}>
          How will your journey unfold?
        </h3>
        <div className="space-y-0">
          {[
            { step: 1, title: 'Choose your pack', desc: 'Select the tier that fits your needs' },
            { step: 2, title: 'Get matched with an expert', desc: 'Within 24 hours of purchase' },
            { step: 3, title: 'Calls + follow-ups + unlimited chat', desc: 'Ongoing support till you have clarity' },
            { step: 4, title: 'Optional add-ons', desc: 'Coming soon' },
          ].map((item, idx) => (
            <div key={idx} className="flex items-start gap-3 relative">
              {/* Timeline line */}
              {idx < 3 && (
                <div 
                  className="absolute left-4 top-8 w-px h-8"
                  style={{ backgroundColor: DIVIDER_COLOR }}
                />
              )}
              <div 
                className="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 text-sm font-semibold"
                style={{ 
                  backgroundColor: idx === 3 ? `${colors.text.mutedDark}20` : `${colors.teal.primary}15`,
                  color: idx === 3 ? colors.text.mutedDark : colors.teal.primary,
                }}
              >
                {item.step}
              </div>
              <div className="flex-1 pb-4">
                <p className="font-medium text-sm" style={{ color: idx === 3 ? colors.text.mutedDark : colors.text.dark }}>
                  {item.title}
                </p>
                <p className="text-xs mt-0.5" style={{ color: colors.text.secondary }}>
                  {item.desc}
                </p>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* ===== DIVIDER ===== */}
      <div className="mx-5 my-4" style={{ borderBottom: `1px solid ${DIVIDER_COLOR}` }} />

      {/* ===== OPTIONAL ADD-ONS (Coming Soon - No CTA) ===== */}
      {hasRemedies && (
        <section className="py-4">
          <h3 className="text-base font-semibold mb-3 px-5" style={{ color: colors.text.dark }}>
            Optional Add-ons
          </h3>
          <div className="flex gap-3 overflow-x-auto px-5 pb-2 scrollbar-hide">
            {content.optionalRemedies.slice(0, 3).map((remedy, idx) => (
              <div 
                key={idx}
                className="flex-shrink-0 w-48 rounded-xl p-4"
                style={{ 
                  backgroundColor: CARD_BG,
                  border: `1px solid ${CARD_BORDER}`,
                }}
              >
                <div className="flex items-center gap-2 mb-2">
                  <div className="w-7 h-7 rounded-lg flex items-center justify-center" style={{ backgroundColor: `${colors.teal.primary}10` }}>
                    <GiftIcon className="w-3.5 h-3.5" style={{ color: colors.teal.primary }} />
                  </div>
                </div>
                <h4 className="font-medium text-sm mb-1" style={{ color: colors.text.dark }}>
                  {remedy.name}
                </h4>
                <p className="text-xs mb-3" style={{ color: colors.text.secondary }}>
                  {remedy.description}
                </p>
                <span 
                  className="inline-block text-[10px] px-2.5 py-1 rounded-full font-medium"
                  style={{ 
                    backgroundColor: `${colors.text.mutedDark}15`,
                    color: colors.text.mutedDark,
                  }}
                >
                  Coming soon
                </span>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* ===== DIVIDER ===== */}
      <div className="mx-5 my-4" style={{ borderBottom: `1px solid ${DIVIDER_COLOR}` }} />

      {/* ===== WHY NIRO (Trust Section) ===== */}
      <section className="px-5 py-4">
        <h3 className="text-base font-semibold mb-4" style={{ color: colors.text.dark }}>
          Why Niro?
        </h3>
        <div className="space-y-3">
          {[
            { icon: <CheckIcon className="w-4 h-4" />, text: 'Verified astrologers across modalities' },
            { icon: <ChatIcon className="w-4 h-4" />, text: 'Unlimited follow-ups till clarity' },
            { icon: <ShieldIcon className="w-4 h-4" />, text: 'Private & secure conversations' },
            { icon: <CheckIcon className="w-4 h-4" />, text: 'No spam, ever' },
            { icon: <ShieldIcon className="w-4 h-4" />, text: '7-day refund guarantee — no questions asked' },
          ].map((item, idx) => (
            <div key={idx} className="flex items-center gap-3">
              <span style={{ color: colors.teal.primary }}>{item.icon}</span>
              <p className="text-sm" style={{ color: colors.text.dark }}>{item.text}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ===== DIVIDER ===== */}
      <div className="mx-5 my-4" style={{ borderBottom: `1px solid ${DIVIDER_COLOR}` }} />

      {/* ===== FAQs (Objection-killers only) ===== */}
      <section className="px-5 py-4 mb-6">
        <h3 className="text-base font-semibold mb-4" style={{ color: colors.text.dark }}>
          Frequently Asked Questions
        </h3>
        <div className="space-y-2">
          {CONVERSION_FAQS.map((faq, idx) => (
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

      {/* ===== STICKY CTA BAR (Simplified) ===== */}
      <div 
        className={`fixed ${hasBottomNav ? 'bottom-16' : 'bottom-0'} left-0 right-0 z-50`}
        style={{ 
          backgroundColor: CARD_BG,
          borderTop: `1px solid ${CARD_BORDER}`,
          boxShadow: '0 -2px 16px rgba(0,0,0,0.06)',
        }}
        data-testid="sticky-cta-bar"
      >
        <div className="px-5 py-4 flex items-center justify-between">
          <span className="text-xl font-bold" style={{ color: colors.text.dark }}>
            {formatPrice(tierData?.price || 0)}
          </span>
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
