import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { colors, shadows } from './theme';
import { 
  CheckIcon, 
  ChevronRightIcon,
  ClockIcon,
  CalendarIcon,
  ChatIcon,
  PhoneIcon
} from './icons';
import { trackEvent } from './utils';
import PublicNavHeader from './PublicNavHeader';

/**
 * PublicTopicLandingPage - Publicly accessible topic landing page
 * Fetches package data from API
 * No login required to browse - only required before checkout
 */

// Tier levels
const TIER_LEVELS = ['Focussed', 'Supported', 'Comprehensive'];
const DEFAULT_TIER = 'Supported';

// Default content for topics (fallback if API doesn't have content)
const DEFAULT_TOPIC_CONTENT = {
  career_clarity: {
    title: 'Career Clarity',
    subtitle: 'Decode what your chart says about your strengths and direction so you can choose your next move with clarity.',
    faqs: [
      { q: 'How does astrology help with career decisions?', a: 'Your birth chart reveals your natural strengths, favorable timing for changes, and the types of work that align with your energy.' },
      { q: 'What if I\'m considering multiple options?', a: 'We analyze each option against your chart to help you understand which aligns better with your planetary influences.' },
      { q: 'Can you predict exact job offers?', a: 'We can identify favorable periods for career growth and opportunities, though specific outcomes depend on multiple factors.' },
    ],
    whyNiro: [
      'Real astrologers (not generic reports) — across Vedic, Tarot, Numerology & more',
      'Unlimited follow-ups in Supported & Comprehensive packs',
      'Clear outcomes: patterns, timing, and what to expect next (no jargon)',
      'Private, secure, and designed for a judgement-free experience',
      '100% satisfaction guaranteed'
    ]
  },
  marriage_planning: {
    title: 'Marriage Planning',
    subtitle: 'Find clarity on compatibility, timing, and what your chart reveals about your journey to marriage.',
    faqs: [
      { q: 'How does kundli matching work?', a: 'We analyze both charts for compatibility across multiple dimensions including emotional, physical, and spiritual alignment.' },
      { q: 'What about love marriages?', a: 'Astrology helps understand the dynamics regardless of how you met. We focus on making relationships work, not judging how they started.' },
      { q: 'Can you suggest auspicious dates?', a: 'Yes, we can identify favorable muhurats based on both charts and planetary positions.' },
    ],
    whyNiro: [
      'Real astrologers (not generic reports) — across Vedic, Tarot, Numerology & more',
      'Unlimited follow-ups in Supported & Comprehensive packs',
      'Clear outcomes: patterns, timing, and what to expect next (no jargon)',
      'Private, secure, and designed for a judgement-free experience',
      '100% satisfaction guaranteed'
    ]
  },
  stress_management: {
    title: 'Stress & Wellness',
    subtitle: 'Understand your energy cycles and find relief through personalized guidance and healing practices.',
    faqs: [
      { q: 'How can astrology help with stress?', a: 'Your chart shows natural stress triggers and the best remedies for your specific planetary influences.' },
      { q: 'Do you recommend only astrological remedies?', a: 'We provide a holistic approach combining astrological insights with practical wellness suggestions.' },
      { q: 'What if I\'m going through a tough planetary period?', a: 'We help you navigate challenging dasha periods with appropriate remedies and mindset shifts.' },
    ],
    whyNiro: [
      'Real astrologers (not generic reports) — across Vedic, Tarot, Numerology & more',
      'Unlimited follow-ups in Supported & Comprehensive packs',
      'Clear outcomes: patterns, timing, and what to expect next (no jargon)',
      'Private, secure, and designed for a judgement-free experience',
      '100% satisfaction guaranteed'
    ]
  },
  relationship_healing: {
    title: 'Relationship Healing',
    subtitle: 'Navigate relationship challenges with astrological insights and find your path to harmony.',
    faqs: [
      { q: 'Can astrology save a troubled relationship?', a: 'Astrology helps understand relationship dynamics and provides remedies, but success requires effort from both partners.' },
      { q: 'What about family relationships?', a: 'Yes, we analyze charts for any relationship including parent-child, siblings, and in-laws.' },
      { q: 'How do remedies work for relationships?', a: 'Remedies address planetary influences that may be causing friction and help create more harmonious energies.' },
    ],
    whyNiro: [
      'Real astrologers (not generic reports) — across Vedic, Tarot, Numerology & more',
      'Unlimited follow-ups in Supported & Comprehensive packs',
      'Clear outcomes: patterns, timing, and what to expect next (no jargon)',
      'Private, secure, and designed for a judgement-free experience',
      '100% satisfaction guaranteed'
    ]
  }
};

export default function PublicTopicLandingPage({ isAuthenticated }) {
  const { topicId } = useParams();
  const navigate = useNavigate();
  const [selectedTier, setSelectedTier] = useState(DEFAULT_TIER);
  const [expandedFaq, setExpandedFaq] = useState(null);
  const [packages, setPackages] = useState({});
  const [loading, setLoading] = useState(true);

  // Fetch packages from API
  useEffect(() => {
    const fetchPackages = async () => {
      try {
        const backendUrl = process.env.REACT_APP_BACKEND_URL || '';
        
        // Fetch all three tiers for this topic
        const tierPromises = TIER_LEVELS.map(tier => 
          fetch(`${backendUrl}/api/admin/public/package/${topicId}_${tier.toLowerCase()}`)
            .then(res => res.json())
            .then(data => ({ tier, data }))
            .catch(() => ({ tier, data: { ok: false } }))
        );
        
        const results = await Promise.all(tierPromises);
        
        const pkgMap = {};
        results.forEach(({ tier, data }) => {
          if (data.ok && data.package) {
            pkgMap[tier] = data.package;
          }
        });
        
        setPackages(pkgMap);
      } catch (err) {
        console.error('Failed to load packages:', err);
      } finally {
        setLoading(false);
      }
    };
    
    fetchPackages();
  }, [topicId]);

  useEffect(() => {
    trackEvent('public_landing_viewed', { 
      tile_id: topicId, 
      selected_tier: selectedTier,
      version: 'api'
    }, null);
  }, [topicId, selectedTier]);

  // Get current tier data
  const currentPackage = packages[selectedTier];
  
  // Get topic content (from package or fallback)
  const topicContent = DEFAULT_TOPIC_CONTENT[topicId] || {
    title: topicId.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase()),
    subtitle: 'Get personalized guidance for your journey.',
    faqs: [],
    whyNiro: DEFAULT_TOPIC_CONTENT.career_clarity.whyNiro
  };

  // Handle checkout - requires login
  const handleCheckout = () => {
    if (isAuthenticated) {
      // If already logged in, go to checkout
      navigate(`/app/checkout?tier=${topicId}_${selectedTier.toLowerCase()}`);
    } else {
      // Store intent and redirect to login
      localStorage.setItem('niro_user_intent', JSON.stringify({ 
        type: 'checkout',
        topicId: topicId,
        tier: selectedTier,
        returnTo: `/app/topic/${topicId}`
      }));
      navigate('/login');
    }
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

  // Loading state
  if (loading) {
    return (
      <div 
        className="min-h-screen"
        style={{ backgroundColor: colors.background.primary }}
      >
        <PublicNavHeader isAuthenticated={isAuthenticated} showBackButton={true} onBackClick={() => navigate('/topics')} />
        <div className="max-w-4xl mx-auto px-4 py-12 text-center">
          <div 
            className="w-12 h-12 border-4 rounded-full animate-spin mx-auto mb-4"
            style={{ borderColor: `${colors.teal.primary}30`, borderTopColor: colors.teal.primary }}
          />
          <p style={{ color: colors.text.muted }}>Loading packages...</p>
        </div>
      </div>
    );
  }

  // No packages found - show friendly message and redirect options
  if (Object.keys(packages).length === 0) {
    return (
      <div 
        className="min-h-screen"
        style={{ backgroundColor: colors.background.primary }}
      >
        <PublicNavHeader isAuthenticated={isAuthenticated} showBackButton={true} onBackClick={() => navigate('/topics')} />
        <div className="max-w-4xl mx-auto px-4 py-12 text-center">
          <div 
            className="w-16 h-16 mx-auto mb-4 rounded-full flex items-center justify-center"
            style={{ backgroundColor: `${colors.peach.soft}` }}
          >
            <svg className="w-8 h-8" viewBox="0 0 24 24" fill="none" stroke={colors.peach.primary} strokeWidth="2">
              <circle cx="12" cy="12" r="10" />
              <path d="M12 6v6l4 2" />
            </svg>
          </div>
          <h2 className="text-xl font-semibold mb-2" style={{ color: colors.text.dark }}>Coming Soon</h2>
          <p className="mb-6" style={{ color: colors.text.secondary }}>
            We're working on making this topic available. Check out our other topics in the meantime!
          </p>
          <button 
            onClick={() => navigate('/topics')} 
            className="px-6 py-3 rounded-full font-semibold transition-all hover:shadow-md"
            style={{ backgroundColor: colors.teal.primary, color: '#ffffff' }}
          >
            Browse Available Topics
          </button>
        </div>
      </div>
    );
  }

  return (
    <div 
      className="min-h-screen pb-28"
      style={{ backgroundColor: colors.background.primary }}
    >
      {/* Header with Navigation */}
      <PublicNavHeader 
        isAuthenticated={isAuthenticated}
        showBackButton={true}
        onBackClick={() => navigate('/topics')}
      />

      {/* Main Content Container */}
      <div className="max-w-4xl mx-auto">
        {/* Hero Section */}
        <section className="px-4 md:px-8 pt-6 pb-4 text-center">
          <h1 
            className="text-xl md:text-2xl lg:text-3xl font-bold mb-3"
            style={{ color: colors.text.dark }}
          >
            {currentPackage?.content?.hero_title || topicContent.title}
          </h1>
          <p 
            className="text-base md:text-lg leading-relaxed max-w-2xl mx-auto"
            style={{ color: colors.text.secondary }}
          >
            {currentPackage?.content?.hero_subtitle || topicContent.subtitle}
          </p>
        </section>

        {/* Choose Your Journey */}
        <section className="px-4 md:px-8 py-4 text-center">
          <h2 
            className="text-lg md:text-xl font-semibold"
            style={{ color: colors.text.dark }}
          >
            Choose your <span style={{ color: colors.teal.primary }}>journey</span>
          </h2>
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
              const pkg = packages[tier];
              const isAvailable = !!pkg;
              const isRecommended = pkg?.popular || tier === 'Supported';
              
              return (
                <button
                  key={tier}
                  onClick={() => isAvailable && setSelectedTier(tier)}
                  disabled={!isAvailable}
                  className={`flex-1 py-3 md:py-4 px-2 md:px-4 rounded-full transition-all relative flex flex-col items-center ${!isAvailable ? 'opacity-40 cursor-not-allowed' : ''}`}
                  style={{
                    backgroundColor: isSelected ? colors.teal.primary : 'transparent',
                    color: isSelected ? '#ffffff' : colors.text.secondary,
                  }}
                  data-testid={`tier-tab-${tier.toLowerCase()}`}
                >
                  {isRecommended && isAvailable && (
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
                    {pkg ? `${pkg.duration_weeks} weeks` : 'Coming soon'}
                  </span>
                </button>
              );
            })}
          </div>
        </section>

        {/* Tier Summary Card */}
        {currentPackage && (
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
              <div className="flex items-start justify-between mb-5">
                <div>
                  <h2 className="text-xl md:text-2xl font-bold" style={{ color: colors.text.dark }}>
                    {selectedTier}
                  </h2>
                  <p className="text-sm md:text-base" style={{ color: colors.text.secondary }}>
                    {currentPackage.duration_weeks} weeks package
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-2xl md:text-3xl font-bold" style={{ color: colors.teal.primary }}>
                    {formatPrice(currentPackage.price)}
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
                      {currentPackage.duration_weeks} weeks
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
                      {currentPackage.calls_included} × {currentPackage.call_duration_mins} mins
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
        )}

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

        {/* Features/What's Included */}
        {currentPackage?.features && currentPackage.features.length > 0 && (
          <section className="px-4 md:px-8 py-6">
            <h2 className="text-lg md:text-xl font-bold mb-5" style={{ color: colors.text.dark }}>
              What's included
            </h2>
            <div 
              className="rounded-xl p-5 md:p-6"
              style={{ backgroundColor: '#ffffff', boxShadow: shadows.card }}
            >
              <div className="grid md:grid-cols-2 gap-3">
                {currentPackage.features.map((feature, idx) => (
                  <div key={idx} className="flex items-start gap-2.5">
                    <CheckIcon className="w-4 h-4 flex-shrink-0 mt-0.5" style={{ color: colors.teal.primary }} />
                    <p className="text-sm md:text-base" style={{ color: colors.text.secondary }}>{feature}</p>
                  </div>
                ))}
              </div>
            </div>
          </section>
        )}

        {/* Outcomes Section (from package content) */}
        {currentPackage?.content?.outcomes && (
          <section className="px-4 md:px-8 py-6">
            <h2 className="text-lg md:text-xl font-bold mb-5" style={{ color: colors.text.dark }}>
              What will this journey help you with?
            </h2>
            
            <div className="grid md:grid-cols-3 gap-4 md:gap-6">
              {Object.entries(currentPackage.content.outcomes).map(([category, items]) => (
                <div 
                  key={category}
                  className="rounded-xl p-5"
                  style={{ backgroundColor: '#ffffff', boxShadow: shadows.card }}
                >
                  <p 
                    className="text-xs font-semibold uppercase tracking-wider mb-3 pb-2 border-b"
                    style={{ color: colors.teal.primary, borderColor: colors.ui.borderDark }}
                  >
                    {category}
                  </p>
                  <div className="space-y-3">
                    {items.map((item, idx) => (
                      <div key={idx} className="flex items-start gap-2.5">
                        <CheckIcon className="w-4 h-4 flex-shrink-0 mt-0.5" style={{ color: colors.teal.primary }} />
                        <p className="text-sm" style={{ color: colors.text.secondary }}>{item}</p>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* How Will Your Journey Unfold */}
        {currentPackage?.content?.how_unfolds && (
          <section className="px-4 md:px-8 py-6">
            <h2 className="text-lg md:text-xl font-bold mb-5" style={{ color: colors.text.dark }}>
              How will your journey unfold
            </h2>
            <div 
              className="rounded-xl p-5 md:p-6"
              style={{ backgroundColor: '#ffffff', boxShadow: shadows.card }}
            >
              <div className="space-y-4">
                {currentPackage.content.how_unfolds.map((step, idx) => (
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
        )}

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
              {topicContent.whyNiro.map((bullet, idx) => (
                <div key={idx} className="flex items-start gap-3">
                  <CheckIcon className="w-5 h-5 flex-shrink-0 mt-0.5" style={{ color: colors.teal.primary }} />
                  <p className="text-sm md:text-base" style={{ color: colors.text.secondary }}>{bullet}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* FAQs */}
        {topicContent.faqs.length > 0 && (
          <section className="px-4 md:px-8 py-6 mb-6">
            <h2 className="text-lg md:text-xl font-bold mb-5" style={{ color: colors.text.dark }}>
              Frequently Asked Questions
            </h2>
            <div className="grid md:grid-cols-2 gap-3 md:gap-4">
              {topicContent.faqs.map((faq, idx) => (
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
        )}
      </div>

      {/* Sticky CTA Bar */}
      {currentPackage && (
        <div 
          className="fixed bottom-0 left-0 right-0 z-50"
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
                {formatPrice(currentPackage.price)}
              </p>
              <p className="text-xs md:text-sm" style={{ color: colors.text.muted }}>
                {currentPackage.duration_weeks} weeks package
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
      )}
    </div>
  );
}
