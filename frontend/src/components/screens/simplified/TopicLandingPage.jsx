import React, { useState, useEffect, useMemo } from 'react';
import { colors, shadows } from './theme';
import { 
  ArrowLeftIcon, 
  CheckIcon, 
  StarIcon, 
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
  LOVE_SUBTOPICS, 
  CAREER_SUBTOPICS, 
  HEALTH_SUBTOPICS,
  getSubtopicBySlug,
  getAllSubtopics 
} from './v5Data/landingPageContent';

/**
 * TopicLandingPage - V4 Landing Page Redesign (Frame 27 Layout)
 * 
 * Structure:
 * 1. Header - Back + Title
 * 2. Hero - Title + Promise + Supporting line
 * 3. Tier Selector Tabs - Focussed / Supported (Recommended) / Comprehensive
 * 4. Tier Summary Card - Details of selected tier
 * 5. Outcomes Section - What the journey helps with
 * 6. How It Unfolds - Delivery structure
 * 7. Paid Remedies Slider - Optional add-ons
 * 8. Sticky CTA Bar - Always visible
 * 9. After Purchase Steps - 4-step timeline
 * 10. Why Niro Trust Section
 * 11. FAQ Accordion
 */

// Tier configuration
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

export default function TopicLandingPage({ token, topicId, onCheckout, onBack, onNavigate, hasBottomNav }) {
  const [selectedTier, setSelectedTier] = useState(DEFAULT_TIER);
  const [expandedFaq, setExpandedFaq] = useState(null);
  const [selectedRemedies, setSelectedRemedies] = useState([]);

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
      remedies_selected: selectedRemedies.length
    }, token);
    onCheckout(tierId, selectedRemedies);
  };

  // Toggle remedy selection
  const toggleRemedy = (remedyName) => {
    setSelectedRemedies(prev => 
      prev.includes(remedyName) 
        ? prev.filter(r => r !== remedyName)
        : [...prev, remedyName]
    );
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

  // If no content found
  if (!content) {
    return (
      <div className="min-h-screen flex items-center justify-center p-6" style={{ backgroundColor: colors.gold.cream }}>
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
      className={`min-h-screen ${hasBottomNav ? 'pb-40' : 'pb-32'}`}
      style={{ backgroundColor: colors.gold.cream }}
    >
      {/* ===== SECTION 1: Header ===== */}
      <header 
        className="sticky top-0 z-50 px-4 py-3 flex items-center gap-3"
        style={{ 
          backgroundColor: '#ffffff',
          borderBottom: `1px solid ${colors.ui.borderDark}`,
        }}
      >
        <button 
          onClick={onBack}
          className="p-2 -ml-2 rounded-full hover:bg-gray-100 transition-colors"
          data-testid="landing-back-btn"
        >
          <ArrowLeftIcon className="w-5 h-5" style={{ color: colors.text.dark }} />
        </button>
        <h1 className="text-lg font-semibold flex-1 truncate" style={{ color: colors.text.dark }}>
          {content.subTopic}
        </h1>
      </header>

      {/* ===== SECTION 2: Hero ===== */}
      <section className="px-5 py-6" style={{ backgroundColor: '#ffffff' }}>
        <p className="text-xs font-medium mb-2" style={{ color: colors.teal.primary }}>
          {content.category}
        </p>
        <h2 className="text-2xl font-bold mb-3" style={{ color: colors.text.dark }}>
          {content.headline}
        </h2>
        <p className="text-base mb-2" style={{ color: colors.text.secondary }}>
          {content.heroPromise}
        </p>
        <p className="text-sm" style={{ color: colors.text.mutedDark }}>
          {content.refundGuarantee}
        </p>
      </section>

      {/* ===== SECTION 3: Tier Selector Tabs ===== */}
      <section className="px-5 py-4" style={{ backgroundColor: '#ffffff', borderTop: `1px solid ${colors.ui.borderDark}` }}>
        <div className="flex gap-2" data-testid="tier-selector-tabs">
          {TIER_LEVELS.map((tier) => {
            const isSelected = selectedTier === tier;
            const isRecommended = tier === 'Supported';
            return (
              <button
                key={tier}
                onClick={() => setSelectedTier(tier)}
                className={`flex-1 py-3 px-2 rounded-xl text-sm font-medium transition-all relative ${
                  isSelected ? 'shadow-md' : ''
                }`}
                style={{
                  backgroundColor: isSelected ? colors.teal.primary : '#f5f5f5',
                  color: isSelected ? '#ffffff' : colors.text.secondary,
                }}
                data-testid={`tier-tab-${tier.toLowerCase()}`}
              >
                {tier}
                {isRecommended && (
                  <span 
                    className="absolute -top-2 left-1/2 -translate-x-1/2 text-[10px] px-2 py-0.5 rounded-full font-semibold whitespace-nowrap"
                    style={{ 
                      backgroundColor: colors.gold.primary,
                      color: colors.text.dark,
                    }}
                  >
                    Recommended
                  </span>
                )}
              </button>
            );
          })}
        </div>
      </section>

      {/* ===== SECTION 4: Tier Summary Card ===== */}
      <section className="px-5 py-4">
        <div 
          className="rounded-2xl p-5"
          style={{ 
            backgroundColor: '#ffffff',
            boxShadow: shadows.card,
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
                    className="text-[10px] px-2 py-0.5 rounded-full font-semibold"
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
                {tierData?.duration} guidance package
              </p>
            </div>
            <div className="text-right">
              <p className="text-2xl font-bold" style={{ color: colors.teal.primary }}>
                {formatPrice(tierData?.price || 0)}
              </p>
            </div>
          </div>

          {/* Tier Details Grid */}
          <div className="grid grid-cols-2 gap-3 pt-4 border-t" style={{ borderColor: colors.ui.borderDark }}>
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg flex items-center justify-center" style={{ backgroundColor: `${colors.teal.primary}15` }}>
                <CalendarIcon className="w-4 h-4" style={{ color: colors.teal.primary }} />
              </div>
              <div>
                <p className="text-xs" style={{ color: colors.text.mutedDark }}>Duration</p>
                <p className="text-sm font-medium" style={{ color: colors.text.dark }}>{tierData?.duration}</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg flex items-center justify-center" style={{ backgroundColor: `${colors.teal.primary}15` }}>
                <PhoneIcon className="w-4 h-4" style={{ color: colors.teal.primary }} />
              </div>
              <div>
                <p className="text-xs" style={{ color: colors.text.mutedDark }}>Consultations</p>
                <p className="text-sm font-medium" style={{ color: colors.text.dark }}>
                  {selectedTier === 'Focussed' ? '1 session' : selectedTier === 'Supported' ? '3 sessions' : '5 sessions'}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg flex items-center justify-center" style={{ backgroundColor: `${colors.teal.primary}15` }}>
                <ClockIcon className="w-4 h-4" style={{ color: colors.teal.primary }} />
              </div>
              <div>
                <p className="text-xs" style={{ color: colors.text.mutedDark }}>Follow-ups</p>
                <p className="text-sm font-medium" style={{ color: colors.text.dark }}>
                  {selectedTier === 'Focussed' ? '1 included' : selectedTier === 'Supported' ? '2 included' : '3+ included'}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg flex items-center justify-center" style={{ backgroundColor: `${colors.teal.primary}15` }}>
                <ChatIcon className="w-4 h-4" style={{ color: colors.teal.primary }} />
              </div>
              <div>
                <p className="text-xs" style={{ color: colors.text.mutedDark }}>Chat</p>
                <p className="text-sm font-medium" style={{ color: colors.text.dark }}>
                  {selectedTier === 'Focussed' ? '7 days' : 'Unlimited'}
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ===== SECTION 5: Outcomes Section ===== */}
      <section className="px-5 py-6" style={{ backgroundColor: '#ffffff' }}>
        <h3 className="text-lg font-semibold mb-4" style={{ color: colors.text.dark }}>
          What will this journey help you with?
        </h3>
        <div className="space-y-3">
          {tierData?.outcomes?.slice(0, 7).map((outcome, idx) => (
            <div 
              key={idx}
              className="flex items-start gap-3 p-3 rounded-xl"
              style={{ backgroundColor: colors.gold.cream }}
            >
              <div 
                className="w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5"
                style={{ backgroundColor: colors.teal.primary }}
              >
                <CheckIcon className="w-3.5 h-3.5" style={{ color: '#ffffff' }} />
              </div>
              <p className="text-sm" style={{ color: colors.text.dark }}>{outcome}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ===== SECTION 6: How It Unfolds ===== */}
      <section className="px-5 py-6">
        <h3 className="text-lg font-semibold mb-4" style={{ color: colors.text.dark }}>
          How will it unfold?
        </h3>
        <div 
          className="rounded-2xl p-5"
          style={{ backgroundColor: '#ffffff', boxShadow: shadows.card }}
        >
          <div className="space-y-4">
            {/* Expert Type */}
            <div className="flex items-start gap-3">
              <div className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0" style={{ backgroundColor: `${colors.teal.primary}15` }}>
                <StarIcon className="w-4 h-4" style={{ color: colors.teal.primary }} />
              </div>
              <div>
                <p className="font-medium text-sm" style={{ color: colors.text.dark }}>Expert Type</p>
                <p className="text-sm" style={{ color: colors.text.secondary }}>
                  {selectedTier === 'Comprehensive' 
                    ? 'Multi-expert: Vedic + Tarot/Healing perspective' 
                    : 'Verified Vedic Astrologer'}
                </p>
              </div>
            </div>

            {/* Consultations */}
            <div className="flex items-start gap-3">
              <div className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0" style={{ backgroundColor: `${colors.teal.primary}15` }}>
                <PhoneIcon className="w-4 h-4" style={{ color: colors.teal.primary }} />
              </div>
              <div>
                <p className="font-medium text-sm" style={{ color: colors.text.dark }}>Consultations</p>
                <p className="text-sm" style={{ color: colors.text.secondary }}>
                  {tierData?.consultations || 'Personalized session cadence'}
                </p>
              </div>
            </div>

            {/* Chat Access */}
            <div className="flex items-start gap-3">
              <div className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0" style={{ backgroundColor: `${colors.teal.primary}15` }}>
                <ChatIcon className="w-4 h-4" style={{ color: colors.teal.primary }} />
              </div>
              <div>
                <p className="font-medium text-sm" style={{ color: colors.text.dark }}>Async Chat</p>
                <p className="text-sm" style={{ color: colors.text.secondary }}>
                  {tierData?.asyncChat || (selectedTier === 'Focussed' ? '7 days' : 'Unlimited for full duration')}
                </p>
              </div>
            </div>

            {/* Response SLA */}
            <div className="flex items-start gap-3">
              <div className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0" style={{ backgroundColor: `${colors.teal.primary}15` }}>
                <ClockIcon className="w-4 h-4" style={{ color: colors.teal.primary }} />
              </div>
              <div>
                <p className="font-medium text-sm" style={{ color: colors.text.dark }}>Response Time</p>
                <p className="text-sm" style={{ color: colors.text.secondary }}>
                  {selectedTier === 'Focussed' ? 'Within 48 hours' : 'Within 24 hours (priority)'}
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ===== SECTION 7: Paid Remedies Slider ===== */}
      {hasRemedies ? (
        <section className="py-6">
          <h3 className="text-lg font-semibold mb-4 px-5" style={{ color: colors.text.dark }}>
            Optional Add-ons
          </h3>
          <div className="flex gap-3 overflow-x-auto px-5 pb-2 scrollbar-hide">
            {content.optionalRemedies.map((remedy, idx) => (
              <div 
                key={idx}
                className="flex-shrink-0 w-56 rounded-xl p-4"
                style={{ 
                  backgroundColor: '#ffffff',
                  boxShadow: shadows.sm,
                  border: `1px solid ${colors.ui.borderDark}`,
                }}
              >
                <div className="flex items-center gap-2 mb-2">
                  <div className="w-8 h-8 rounded-lg flex items-center justify-center" style={{ backgroundColor: `${colors.gold.primary}30` }}>
                    <GiftIcon className="w-4 h-4" style={{ color: colors.teal.primary }} />
                  </div>
                  <span className="text-xs px-2 py-0.5 rounded-full font-medium capitalize" style={{ backgroundColor: `${colors.teal.primary}15`, color: colors.teal.primary }}>
                    {remedy.type}
                  </span>
                </div>
                <h4 className="font-semibold text-sm mb-1" style={{ color: colors.text.dark }}>
                  {remedy.name}
                </h4>
                <p className="text-xs mb-3" style={{ color: colors.text.secondary }}>
                  {remedy.description}
                </p>
                <button
                  onClick={() => toggleRemedy(remedy.name)}
                  className="w-full py-2 rounded-lg text-xs font-semibold transition-colors"
                  style={{
                    backgroundColor: selectedRemedies.includes(remedy.name) ? colors.teal.primary : `${colors.teal.primary}15`,
                    color: selectedRemedies.includes(remedy.name) ? '#ffffff' : colors.teal.primary,
                  }}
                >
                  {selectedRemedies.includes(remedy.name) ? '✓ Added' : 'Add to my journey'}
                </button>
              </div>
            ))}
          </div>
        </section>
      ) : (
        <section className="px-5 py-4">
          <div 
            className="rounded-xl p-4 text-center"
            style={{ backgroundColor: `${colors.teal.primary}08`, border: `1px dashed ${colors.teal.primary}30` }}
          >
            <p className="text-sm" style={{ color: colors.text.secondary }}>
              Remedies available after your first consult.
            </p>
          </div>
        </section>
      )}

      {/* ===== SECTION 9: What happens after purchase ===== */}
      <section className="px-5 py-6" style={{ backgroundColor: '#ffffff' }}>
        <h3 className="text-lg font-semibold mb-4" style={{ color: colors.text.dark }}>
          What happens after your purchase?
        </h3>
        <div className="space-y-4">
          {[
            { step: 1, title: 'Confirmation sent', desc: 'Instant confirmation + next steps via WhatsApp/email' },
            { step: 2, title: 'Expert matching', desc: 'You get matched with the right expert within 24 hours' },
            { step: 3, title: 'Sessions begin', desc: 'Calls + follow-ups continue until you have clarity' },
            { step: 4, title: 'Remedies delivered', desc: 'If added, remedies are coordinated and delivered to you' },
          ].map((item, idx) => (
            <div key={idx} className="flex items-start gap-4">
              <div 
                className="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 font-semibold text-sm"
                style={{ 
                  backgroundColor: colors.teal.primary,
                  color: '#ffffff',
                }}
              >
                {item.step}
              </div>
              <div className="flex-1 pb-4" style={{ borderBottom: idx < 3 ? `1px solid ${colors.ui.borderDark}` : 'none' }}>
                <p className="font-medium text-sm" style={{ color: colors.text.dark }}>{item.title}</p>
                <p className="text-xs mt-0.5" style={{ color: colors.text.secondary }}>{item.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* ===== SECTION 10: Why Niro Trust Section ===== */}
      <section className="px-5 py-6">
        <h3 className="text-lg font-semibold mb-4" style={{ color: colors.text.dark }}>
          Why Niro?
        </h3>
        <div 
          className="rounded-2xl p-5"
          style={{ backgroundColor: '#ffffff', boxShadow: shadows.card }}
        >
          <div className="space-y-3">
            {[
              { icon: <CheckIcon className="w-4 h-4" />, text: 'Verified astrologers across modalities' },
              { icon: <ChatIcon className="w-4 h-4" />, text: 'Unlimited follow-ups till clarity' },
              { icon: <ShieldIcon className="w-4 h-4" />, text: 'Private & secure conversations' },
              { icon: <CheckIcon className="w-4 h-4" />, text: 'No spam, ever' },
              { icon: <ShieldIcon className="w-4 h-4" />, text: '7-day refund guarantee — no questions asked' },
            ].map((item, idx) => (
              <div key={idx} className="flex items-center gap-3">
                <div 
                  className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0"
                  style={{ backgroundColor: `${colors.teal.primary}15` }}
                >
                  <span style={{ color: colors.teal.primary }}>{item.icon}</span>
                </div>
                <p className="text-sm" style={{ color: colors.text.dark }}>{item.text}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ===== SECTION 11: FAQ Accordion ===== */}
      <section className="px-5 py-6 mb-8">
        <h3 className="text-lg font-semibold mb-4" style={{ color: colors.text.dark }}>
          Frequently Asked Questions
        </h3>
        <div className="space-y-3">
          {content.faqs?.map((faq, idx) => (
            <div 
              key={idx}
              className="rounded-xl overflow-hidden"
              style={{ backgroundColor: '#ffffff', border: `1px solid ${colors.ui.borderDark}` }}
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
                  <p className="text-sm" style={{ color: colors.text.secondary }}>{faq.a}</p>
                </div>
              )}
            </div>
          ))}
        </div>
      </section>

      {/* ===== SECTION 8: Sticky CTA Bar ===== */}
      <div 
        className={`fixed ${hasBottomNav ? 'bottom-16' : 'bottom-0'} left-0 right-0 z-50`}
        style={{ 
          backgroundColor: '#ffffff',
          borderTop: `1px solid ${colors.ui.borderDark}`,
          boxShadow: '0 -4px 20px rgba(0,0,0,0.1)',
        }}
        data-testid="sticky-cta-bar"
      >
        <div className="px-5 py-4">
          <div className="flex items-center justify-between mb-3">
            <div>
              <div className="flex items-center gap-2">
                <span className="text-xl font-bold" style={{ color: colors.text.dark }}>
                  {formatPrice(tierData?.price || 0)}
                </span>
                {selectedTier === 'Supported' && (
                  <span 
                    className="text-[10px] px-2 py-0.5 rounded-full font-semibold"
                    style={{ backgroundColor: colors.gold.primary, color: colors.text.dark }}
                  >
                    Recommended
                  </span>
                )}
              </div>
              <p className="text-xs" style={{ color: colors.text.secondary }}>
                {tierData?.duration} • {selectedTier}
              </p>
            </div>
            <button
              onClick={handleCheckout}
              className="px-8 py-3 rounded-xl font-semibold text-base transition-all active:scale-[0.98]"
              style={{ 
                backgroundColor: colors.teal.primary,
                color: '#ffffff',
                boxShadow: shadows.md,
              }}
              data-testid="start-journey-btn"
            >
              Start my journey
            </button>
          </div>
          <div className="flex items-center justify-center gap-4 text-xs" style={{ color: colors.text.mutedDark }}>
            <span className="flex items-center gap-1">
              <ShieldIcon className="w-3.5 h-3.5" />
              Secure payments
            </span>
            <span>•</span>
            <span>7-day full refund, no questions</span>
          </div>
        </div>
      </div>
    </div>
  );
}
