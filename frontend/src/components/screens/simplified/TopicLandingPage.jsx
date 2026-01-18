import React, { useState, useEffect } from 'react';
import { colors, shadows } from './theme';
import { getTileById, getPackageStructure, SAMPLE_EXPERTS, formatPrice } from './tileData';
import { ArrowLeftIcon, CheckIcon, StarIcon, ClockIcon, CalendarIcon, DocumentIcon, ChatIcon, GiftIcon, ShieldIcon, ChevronRightIcon, QuoteIcon } from './icons';
import { trackEvent } from './utils';
import RefundBadge from './RefundBadge';

/**
 * TopicLandingPage - Complete redesign with teal colors and Remedies section (V5)
 * Updated to match user reference images
 */
export default function TopicLandingPage({ token, topicId, onCheckout, onBack, onNavigate, hasBottomNav }) {
  const [expandedFaq, setExpandedFaq] = useState(null);
  const [selectedRemedies, setSelectedRemedies] = useState([]);
  
  const tileData = getTileById(topicId);
  const packageStructure = getPackageStructure(topicId);

  useEffect(() => {
    trackEvent('landing_viewed', { tile_id: topicId }, token);
  }, [topicId, token]);

  const handleBuyPack = () => {
    trackEvent('buy_pack_clicked', { tile_id: topicId, price: tileData?.price }, token);
    onCheckout(topicId, selectedRemedies);
  };

  const toggleRemedy = (remedyName) => {
    setSelectedRemedies(prev => 
      prev.includes(remedyName) 
        ? prev.filter(r => r !== remedyName)
        : [...prev, remedyName]
    );
  };

  const getTotalPrice = () => {
    let total = tileData?.price || 0;
    selectedRemedies.forEach(remedyName => {
      const remedy = tileData?.paidRemedies?.find(r => r.name === remedyName);
      if (remedy) total += remedy.price;
    });
    return total;
  };

  if (!tileData) {
    return (
      <div className="min-h-screen flex items-center justify-center p-6" style={{ backgroundColor: colors.background.primary }}>
        <div className="text-center">
          <p style={{ color: colors.ui.error }} className="mb-4">Package not found</p>
          <button onClick={onBack} style={{ color: colors.gold.primary }}>Go back</button>
        </div>
      </div>
    );
  }

  return (
    <div 
      className={`min-h-screen ${hasBottomNav ? 'pb-36' : 'pb-28'}`} 
      style={{ 
        backgroundColor: colors.gold.cream,
        paddingTop: 'env(safe-area-inset-top)',
      }}
    >
      {/* Hero Section */}
      <div 
        className="px-5 pt-4 pb-6"
        style={{ background: `linear-gradient(135deg, ${colors.teal.primary} 0%, ${colors.teal.dark} 100%)` }}
      >
        <button 
          onClick={onBack} 
          className="mb-4 flex items-center transition-colors"
          style={{ color: 'rgba(255,255,255,0.9)' }}
        >
          <ArrowLeftIcon className="w-5 h-5 mr-1" />
          Back
        </button>
        
        <p className="text-xs mb-1" style={{ color: 'rgba(255,255,255,0.7)' }}>
          {tileData.categoryTitle}
        </p>
        <h1 className="text-2xl font-bold mb-2" style={{ color: '#ffffff' }}>
          {tileData.title}
        </h1>
        <p className="text-base" style={{ color: 'rgba(255,255,255,0.95)' }}>
          {tileData.outcomeStatement}
        </p>
      </div>

      {/* Summary Card */}
      <div className="px-5 -mt-4">
        <div 
          className="rounded-xl p-4"
          style={{ 
            backgroundColor: '#ffffff',
            boxShadow: shadows.md,
          }}
        >
          <div className="grid grid-cols-2 gap-4">
            <div className="flex items-center gap-2">
              <CalendarIcon className="w-5 h-5" style={{ color: colors.teal.primary }} />
              <div>
                <p className="text-xs" style={{ color: colors.text.mutedDark }}>Duration</p>
                <p className="text-sm font-medium" style={{ color: colors.text.dark }}>{tileData.duration}</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <ClockIcon className="w-5 h-5" style={{ color: colors.teal.primary }} />
              <div>
                <p className="text-xs" style={{ color: colors.text.mutedDark }}>Response</p>
                <p className="text-sm font-medium" style={{ color: colors.text.dark }}>{tileData.responseSLA}</p>
              </div>
            </div>
          </div>
          <div className="mt-4 pt-4 border-t flex items-center justify-between" style={{ borderColor: colors.ui.borderDark }}>
            <div>
              <p className="text-xs" style={{ color: colors.text.mutedDark }}>Package Price</p>
              <p className="text-xl font-bold" style={{ color: colors.text.dark }}>{formatPrice(tileData.price)}</p>
            </div>
            <button
              onClick={handleBuyPack}
              className="px-6 py-3 rounded-xl font-semibold text-sm transition-all active:scale-[0.98]"
              style={{ 
                backgroundColor: colors.gold.primary,
                color: colors.text.dark,
                boxShadow: shadows.sm,
              }}
            >
              Buy Pack
            </button>
          </div>
        </div>
      </div>

      {/* Section 1: Who this is for */}
      <div className="px-5 py-6">
        <h2 className="text-lg font-semibold mb-4" style={{ color: colors.text.dark }}>Who this is for</h2>
        <div className="space-y-3">
          {tileData.whoFor?.map((item, idx) => (
            <div key={idx} className="flex items-start gap-3">
              <div 
                className="w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5"
                style={{ backgroundColor: `${colors.teal.primary}20` }}
              >
                <CheckIcon className="w-3.5 h-3.5" style={{ color: colors.teal.primary }} />
              </div>
              <p className="text-sm" style={{ color: colors.text.secondary }}>{item}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Section 2: What's Included */}
      <div className="px-5 py-6" style={{ backgroundColor: '#ffffff' }}>
        <h2 className="text-lg font-semibold mb-4" style={{ color: colors.text.dark }}>What&apos;s included</h2>
        <p className="text-sm mb-4" style={{ color: colors.text.secondary }}>{tileData.toolFeatures}</p>
        
        {/* Tools */}
        <div className="space-y-3">
          {tileData.includedTools?.map((tool, idx) => (
            <div 
              key={idx} 
              className="flex items-center gap-3 p-3 rounded-xl"
              style={{ backgroundColor: colors.gold.cream, border: `1px solid ${colors.ui.borderDark}` }}
            >
              <div 
                className="w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0"
                style={{ backgroundColor: `${colors.teal.primary}15` }}
              >
                <DocumentIcon className="w-5 h-5" style={{ color: colors.teal.primary }} />
              </div>
              <div className="flex-1">
                <p className="text-sm font-medium" style={{ color: colors.text.dark }}>{tool.name}</p>
                <p className="text-xs" style={{ color: colors.text.mutedDark }}>{tool.description}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Section 3: How it works */}
      <div className="px-5 py-6">
        <h2 className="text-lg font-semibold mb-4" style={{ color: colors.text.dark }}>How it works</h2>
        <div className="space-y-4">
          {packageStructure?.howItWorks?.map((step, idx) => (
            <div key={idx} className="flex gap-4">
              <div className="flex flex-col items-center">
                <div 
                  className="w-8 h-8 rounded-full flex items-center justify-center font-semibold text-sm"
                  style={{ backgroundColor: colors.teal.primary, color: '#ffffff' }}
                >
                  {step.step}
                </div>
                {idx < packageStructure.howItWorks.length - 1 && (
                  <div className="w-0.5 h-8 mt-2" style={{ backgroundColor: colors.ui.borderDark }} />
                )}
              </div>
              <div className="flex-1 pb-4">
                <p className="font-medium text-sm" style={{ color: colors.text.dark }}>{step.title}</p>
                <p className="text-sm mt-1" style={{ color: colors.text.secondary }}>{step.description}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Section 4: Remedies (Add-ons) */}
      <div className="px-5 py-6" style={{ backgroundColor: '#ffffff' }}>
        <h2 className="text-lg font-semibold mb-2" style={{ color: colors.text.dark }}>
          Add Remedies <span className="text-xs font-normal" style={{ color: colors.text.mutedDark }}>(Optional)</span>
        </h2>
        <p className="text-sm mb-4" style={{ color: colors.text.secondary }}>
          Enhance your journey with verified remedies
        </p>
        
        <div className="space-y-3">
          {tileData.paidRemedies?.map((remedy, idx) => {
            const isSelected = selectedRemedies.includes(remedy.name);
            return (
              <div 
                key={idx}
                onClick={() => toggleRemedy(remedy.name)}
                className="flex items-center gap-3 p-4 rounded-xl cursor-pointer transition-all"
                style={{ 
                  backgroundColor: isSelected ? `${colors.teal.primary}10` : colors.gold.cream,
                  border: `2px solid ${isSelected ? colors.teal.primary : colors.ui.borderDark}`,
                }}
              >
                {/* Checkbox */}
                <div 
                  className="w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0 border-2"
                  style={{ 
                    backgroundColor: isSelected ? colors.teal.primary : 'transparent',
                    borderColor: isSelected ? colors.teal.primary : colors.ui.borderDark,
                  }}
                >
                  {isSelected && <CheckIcon className="w-3.5 h-3.5" style={{ color: '#ffffff' }} />}
                </div>
                
                {/* Content */}
                <div className="flex-1">
                  <p className="text-sm font-medium" style={{ color: colors.text.dark }}>{remedy.name}</p>
                  <p className="text-xs" style={{ color: colors.text.mutedDark }}>{remedy.description}</p>
                </div>
                
                {/* Price */}
                <span className="font-semibold text-sm" style={{ color: colors.teal.primary }}>
                  +{formatPrice(remedy.price)}
                </span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Section 5: Meet your astrologers */}
      <div className="py-6">
        <div className="px-5 mb-4 flex items-center justify-between">
          <h2 className="text-lg font-semibold" style={{ color: colors.text.dark }}>Meet your experts</h2>
          <button className="text-xs font-medium flex items-center" style={{ color: colors.teal.primary }}>
            View all <ChevronRightIcon className="w-4 h-4 ml-0.5" />
          </button>
        </div>
        <div className="flex overflow-x-auto gap-3 px-5 pb-2 scrollbar-hide">
          {SAMPLE_EXPERTS.slice(0, 4).map((expert) => (
            <div
              key={expert.expert_id}
              className="flex-shrink-0 w-36 rounded-xl p-3 text-center"
              style={{ backgroundColor: '#ffffff', border: `1px solid ${colors.ui.borderDark}` }}
            >
              <div 
                className="w-14 h-14 rounded-full mx-auto mb-2 overflow-hidden"
                style={{ backgroundColor: colors.gold.cream }}
              >
                <img 
                  src={expert.photo_url} 
                  alt={expert.name}
                  className="w-full h-full object-cover"
                  onError={(e) => { e.target.style.display = 'none'; }}
                />
              </div>
              <p className="font-medium text-sm line-clamp-1" style={{ color: colors.text.dark }}>{expert.name}</p>
              <p className="text-xs mt-0.5" style={{ color: colors.teal.primary }}>{expert.modality_label}</p>
              <div className="flex items-center justify-center mt-1">
                <StarIcon className="w-3.5 h-3.5" style={{ color: '#F59E0B' }} filled />
                <span className="text-xs ml-1" style={{ color: colors.text.secondary }}>{expert.rating}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Section 6: Trust section */}
      <div className="px-5 py-6" style={{ backgroundColor: '#ffffff' }}>
        <h2 className="text-lg font-semibold mb-4" style={{ color: colors.text.dark }}>Why Niro</h2>
        
        {/* Refund Badge */}
        <div className="mb-4">
          <RefundBadge variant="default" />
        </div>
        
        <div className="space-y-3">
          <div className="flex items-start gap-3 p-3 rounded-xl" style={{ backgroundColor: colors.gold.cream }}>
            <CheckIcon className="w-5 h-5 mt-0.5" style={{ color: colors.teal.primary }} />
            <div>
              <p className="font-medium text-sm" style={{ color: colors.text.dark }}>Verified experts only</p>
              <p className="text-xs mt-0.5" style={{ color: colors.text.mutedDark }}>Every expert is background verified</p>
            </div>
          </div>
          <div className="flex items-start gap-3 p-3 rounded-xl" style={{ backgroundColor: colors.gold.cream }}>
            <ShieldIcon className="w-5 h-5 mt-0.5" style={{ color: colors.teal.primary }} />
            <div>
              <p className="font-medium text-sm" style={{ color: colors.text.dark }}>100% Private & Secure</p>
              <p className="text-xs mt-0.5" style={{ color: colors.text.mutedDark }}>Your conversations are encrypted</p>
            </div>
          </div>
          <div className="flex items-start gap-3 p-3 rounded-xl" style={{ backgroundColor: colors.gold.cream }}>
            <QuoteIcon className="w-5 h-5 mt-0.5" style={{ color: colors.teal.primary }} />
            <div>
              <p className="font-medium text-sm" style={{ color: colors.text.dark }}>10,000+ happy users</p>
              <p className="text-xs mt-0.5" style={{ color: colors.text.mutedDark }}>Join thousands who found clarity</p>
            </div>
          </div>
        </div>
      </div>

      {/* Section 7: FAQs */}
      <div className="px-5 py-6">
        <h2 className="text-lg font-semibold mb-4" style={{ color: colors.text.dark }}>FAQs</h2>
        <div className="space-y-3">
          {packageStructure?.faqs?.map((faq, idx) => (
            <div 
              key={idx}
              className="rounded-xl overflow-hidden"
              style={{ backgroundColor: '#ffffff', border: `1px solid ${colors.ui.borderDark}` }}
            >
              <button
                onClick={() => setExpandedFaq(expandedFaq === idx ? null : idx)}
                className="w-full p-4 flex items-center justify-between text-left"
              >
                <span className="font-medium text-sm pr-4" style={{ color: colors.text.dark }}>{faq.q}</span>
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
      </div>

      {/* Sticky CTA */}
      <div 
        className={`fixed ${hasBottomNav ? 'bottom-16' : 'bottom-0'} left-0 right-0 p-4 z-40`}
        style={{ 
          backgroundColor: '#ffffff',
          borderTop: `1px solid ${colors.ui.borderDark}`,
          boxShadow: '0 -4px 16px rgba(0,0,0,0.08)',
          paddingBottom: hasBottomNav ? '16px' : 'max(16px, env(safe-area-inset-bottom))',
        }}
      >
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs" style={{ color: colors.text.mutedDark }}>
            {selectedRemedies.length > 0 ? `Pack + ${selectedRemedies.length} remedy${selectedRemedies.length > 1 ? 's' : ''}` : 'Package total'}
          </span>
          <span className="text-lg font-bold" style={{ color: colors.text.dark }}>
            {formatPrice(getTotalPrice())}
          </span>
        </div>
        <button
          onClick={handleBuyPack}
          className="w-full font-semibold py-4 rounded-xl transition-all active:scale-[0.99]"
          style={{ 
            backgroundColor: colors.gold.primary,
            color: colors.text.dark,
            boxShadow: shadows.md,
          }}
        >
          Buy Pack
        </button>
      </div>
    </div>
  );
}
