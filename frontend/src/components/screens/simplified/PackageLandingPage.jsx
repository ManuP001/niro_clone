import React, { useState, useEffect } from 'react';
import { colors } from './theme';
import { ArrowLeftIcon, CheckIcon, ShieldIcon, ChevronRightIcon } from './icons.jsx';
import { trackEvent } from './utils';
import { getBackendUrl } from '../../../config';

/**
 * PackageLandingPage - Renders standalone package content from admin database
 * 
 * Used for tiles with linked_package_id (like Valentine's Special)
 * Fetches package content including:
 * - Hero section (title, subtitle, trust line)
 * - Overview (title, description, includes)
 * - Help sections (Clarity, Timeline, etc.)
 * - Analysis sections (We review, etc.)
 * - Deliverables
 * - Custom sections
 */

const GRADIENT_BG = 'linear-gradient(180deg, #E8F5F3 0%, #F5FBF9 50%, #FFFEF5 100%)';
const CARD_BG = 'rgba(255, 255, 255, 0.85)';
const CARD_BORDER = 'rgba(0,0,0,0.06)';
const DIVIDER_COLOR = 'rgba(0,0,0,0.06)';

export default function PackageLandingPage({ 
  token, 
  packageId, 
  tileData,
  onCheckout, 
  onBack, 
  hasBottomNav,
  userName 
}) {
  const [packageData, setPackageData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [expandedSection, setExpandedSection] = useState(null);

  useEffect(() => {
    loadPackageContent();
  }, [packageId]);

  const loadPackageContent = async () => {
    try {
      const backendUrl = getBackendUrl();
      const response = await fetch(`${backendUrl}/api/admin/public/package/${packageId}`);
      if (response.ok) {
        const data = await response.json();
        if (data.ok && data.package) {
          setPackageData(data.package);
        } else {
          setError('Package not found');
        }
      } else {
        setError('Failed to load package');
      }
    } catch (err) {
      console.error('Error loading package:', err);
      setError('Failed to load package');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (packageData) {
      trackEvent('package_landing_viewed', { 
        package_id: packageId, 
        package_name: packageData.name,
      }, token);
    }
  }, [packageData, packageId, token]);

  const formatPrice = (price) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(price);
  };

  const handleCheckout = () => {
    trackEvent('package_checkout_initiated', { 
      package_id: packageId,
      price: packageData?.price,
    }, token);
    onCheckout(packageId, []);
  };

  const displayName = userName || 'there';

  // Loading state
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ background: GRADIENT_BG }}>
        <div className="text-center">
          <div 
            className="w-12 h-12 border-4 rounded-full animate-spin mx-auto mb-4"
            style={{ borderColor: 'rgba(0,0,0,0.1)', borderTopColor: colors.teal.primary }}
          />
          <p style={{ color: colors.text.secondary }}>Loading...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (error || !packageData) {
    return (
      <div className="min-h-screen flex items-center justify-center p-6" style={{ background: GRADIENT_BG }}>
        <div className="text-center">
          <p style={{ color: colors.ui?.error || '#F44336' }} className="mb-4">{error || 'Package not found'}</p>
          <button onClick={onBack} style={{ color: colors.teal.primary }} className="font-medium">
            Go back
          </button>
        </div>
      </div>
    );
  }

  const content = packageData.content || {};
  const price = packageData.price || 0;
  const durationDays = packageData.duration_days || 7;

  return (
    <div 
      className={`min-h-screen ${hasBottomNav ? 'pb-28' : 'pb-24'}`}
      style={{ background: GRADIENT_BG }}
    >
      {/* Header */}
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
          data-testid="package-landing-back-btn"
        >
          <ArrowLeftIcon className="w-5 h-5" style={{ color: colors.text.dark }} />
        </button>
        <h1 className="text-lg font-semibold flex-1 truncate" style={{ color: colors.text.dark }}>
          {content.hero_title || packageData.name}
        </h1>
      </header>

      {/* Hero Section */}
      <section className="px-5 pt-6 pb-4">
        <h2 
          className="text-2xl font-bold text-center mb-3"
          style={{ color: colors.text.dark }}
        >
          {content.hero_title || packageData.name}
        </h2>
        <p 
          className="text-base text-center leading-relaxed mb-4"
          style={{ color: colors.text.secondary }}
        >
          {content.hero_subtitle || packageData.description}
        </p>
        {content.trust_line && (
          <p 
            className="text-sm text-center italic"
            style={{ color: colors.teal.primary }}
          >
            {content.trust_line}
          </p>
        )}
      </section>

      {/* Trust Badges */}
      <section className="px-5 py-3">
        <div className="flex justify-center gap-4 flex-wrap">
          {['Senior experts', 'Unlimited follow-ups', 'Private & secure'].map((badge, i) => (
            <div 
              key={i}
              className="flex items-center gap-1 text-xs"
              style={{ color: colors.text.secondary }}
            >
              <CheckIcon className="w-3 h-3" style={{ color: colors.teal.primary }} />
              {badge}
            </div>
          ))}
        </div>
      </section>

      {/* Package Overview Card */}
      <section className="px-5 py-3">
        <div 
          className="rounded-2xl p-4"
          style={{ 
            backgroundColor: CARD_BG, 
            border: `1px solid ${CARD_BORDER}`,
            boxShadow: '0 2px 8px rgba(0,0,0,0.04)',
          }}
        >
          <div className="flex justify-between items-start mb-3">
            <div>
              <h3 className="text-lg font-semibold" style={{ color: colors.text.dark }}>
                {content.overview_title || `${durationDays}-Day Guidance`}
              </h3>
              <p className="text-sm" style={{ color: colors.text.secondary }}>
                {content.overview_description || 'Unlimited guidance on your topic'}
              </p>
            </div>
            <div className="text-right">
              <p className="text-xl font-bold" style={{ color: colors.teal.primary }}>
                {formatPrice(price)}
              </p>
              <p className="text-xs" style={{ color: colors.text.secondary }}>
                {durationDays} days
              </p>
            </div>
          </div>

          {/* What's Included */}
          {content.includes && content.includes.length > 0 && (
            <div className="pt-3 border-t" style={{ borderColor: DIVIDER_COLOR }}>
              <p className="text-sm font-medium mb-2" style={{ color: colors.text.dark }}>
                What's included:
              </p>
              <ul className="space-y-2">
                {content.includes.map((item, i) => (
                  <li key={i} className="flex items-start gap-2">
                    <CheckIcon className="w-4 h-4 mt-0.5 flex-shrink-0" style={{ color: colors.teal.primary }} />
                    <span className="text-sm" style={{ color: colors.text.secondary }}>{item}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </section>

      {/* Help Sections (Clarity, Timeline, etc.) */}
      {content.help_sections && content.help_sections.length > 0 && (
        <section className="px-5 py-3">
          <h3 className="text-base font-semibold mb-3" style={{ color: colors.text.dark }}>
            What This Helps You With
          </h3>
          <div className="space-y-2">
            {content.help_sections.map((section, i) => (
              <div 
                key={i}
                className="rounded-xl overflow-hidden"
                style={{ 
                  backgroundColor: CARD_BG, 
                  border: `1px solid ${CARD_BORDER}`,
                }}
              >
                <button
                  onClick={() => setExpandedSection(expandedSection === `help-${i}` ? null : `help-${i}`)}
                  className="w-full px-4 py-3 flex justify-between items-center"
                >
                  <span className="font-medium text-sm" style={{ color: colors.text.dark }}>
                    {section.title}
                  </span>
                  <ChevronRightIcon 
                    className={`w-4 h-4 transition-transform ${expandedSection === `help-${i}` ? 'rotate-90' : ''}`}
                    style={{ color: colors.text.secondary }}
                  />
                </button>
                {expandedSection === `help-${i}` && section.items && (
                  <div className="px-4 pb-3">
                    <ul className="space-y-1.5">
                      {section.items.map((item, j) => (
                        <li key={j} className="flex items-start gap-2">
                          <span className="text-xs mt-1" style={{ color: colors.teal.primary }}>•</span>
                          <span className="text-sm" style={{ color: colors.text.secondary }}>{item}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Deliverables */}
      {content.deliverables && content.deliverables.length > 0 && (
        <section className="px-5 py-3">
          <h3 className="text-base font-semibold mb-3" style={{ color: colors.text.dark }}>
            What You'll Leave With
          </h3>
          <div 
            className="rounded-xl p-4"
            style={{ 
              backgroundColor: CARD_BG, 
              border: `1px solid ${CARD_BORDER}`,
            }}
          >
            <ul className="space-y-2">
              {content.deliverables.map((item, i) => (
                <li key={i} className="flex items-start gap-2">
                  <CheckIcon className="w-4 h-4 mt-0.5 flex-shrink-0" style={{ color: colors.teal.primary }} />
                  <span className="text-sm" style={{ color: colors.text.secondary }}>{item}</span>
                </li>
              ))}
            </ul>
          </div>
        </section>
      )}

      {/* Analysis Section */}
      {content.analysis_sections && content.analysis_sections.length > 0 && (
        <section className="px-5 py-3">
          <h3 className="text-base font-semibold mb-2" style={{ color: colors.text.dark }}>
            How We Analyse Your Situation
          </h3>
          {content.analysis_intro && (
            <p className="text-sm mb-3" style={{ color: colors.text.secondary }}>
              {content.analysis_intro}
            </p>
          )}
          <div className="space-y-2">
            {content.analysis_sections.map((section, i) => (
              <div 
                key={i}
                className="rounded-xl overflow-hidden"
                style={{ 
                  backgroundColor: CARD_BG, 
                  border: `1px solid ${CARD_BORDER}`,
                }}
              >
                <button
                  onClick={() => setExpandedSection(expandedSection === `analysis-${i}` ? null : `analysis-${i}`)}
                  className="w-full px-4 py-3 flex justify-between items-center"
                >
                  <span className="font-medium text-sm" style={{ color: colors.text.dark }}>
                    {section.title}
                  </span>
                  <ChevronRightIcon 
                    className={`w-4 h-4 transition-transform ${expandedSection === `analysis-${i}` ? 'rotate-90' : ''}`}
                    style={{ color: colors.text.secondary }}
                  />
                </button>
                {expandedSection === `analysis-${i}` && section.items && (
                  <div className="px-4 pb-3">
                    <ul className="space-y-1.5">
                      {section.items.map((item, j) => (
                        <li key={j} className="flex items-start gap-2">
                          <span className="text-xs mt-1" style={{ color: colors.teal.primary }}>•</span>
                          <span className="text-sm" style={{ color: colors.text.secondary }}>{item}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Custom Sections */}
      {content.custom_sections && content.custom_sections.length > 0 && (
        <section className="px-5 py-3">
          {content.custom_sections.map((section, i) => (
            <div key={i} className="mb-4">
              <h3 className="text-base font-semibold mb-2" style={{ color: colors.text.dark }}>
                {section.title}
              </h3>
              <div 
                className="rounded-xl p-4"
                style={{ 
                  backgroundColor: CARD_BG, 
                  border: `1px solid ${CARD_BORDER}`,
                }}
              >
                {section.content_type === 'paragraph' && section.text ? (
                  <p className="text-sm leading-relaxed" style={{ color: colors.text.secondary }}>
                    {section.text}
                  </p>
                ) : section.items ? (
                  <ul className="space-y-2">
                    {section.items.map((item, j) => (
                      <li key={j} className="flex items-start gap-2">
                        <span className="text-xs mt-1" style={{ color: colors.teal.primary }}>•</span>
                        <span className="text-sm" style={{ color: colors.text.secondary }}>{item}</span>
                      </li>
                    ))}
                  </ul>
                ) : null}
              </div>
            </div>
          ))}
        </section>
      )}

      {/* Ethics Note */}
      <section className="px-5 py-4">
        <div 
          className="rounded-xl p-4 text-center"
          style={{ 
            backgroundColor: 'rgba(62, 130, 122, 0.08)', 
            border: `1px solid rgba(62, 130, 122, 0.2)`,
          }}
        >
          <ShieldIcon className="w-5 h-5 mx-auto mb-2" style={{ color: colors.teal.primary }} />
          <p className="text-xs" style={{ color: colors.text.secondary }}>
            We focus on clarity and timing — not fear. Your conversations are private and confidential.
          </p>
        </div>
      </section>

      {/* Sticky CTA Bar */}
      <div 
        className="fixed bottom-0 left-0 right-0 z-50 px-5 py-3"
        style={{ 
          background: 'linear-gradient(180deg, rgba(255,255,255,0) 0%, rgba(255,255,255,0.95) 20%, #ffffff 100%)',
          paddingBottom: hasBottomNav ? '72px' : '16px',
        }}
      >
        <button
          onClick={handleCheckout}
          className="w-full py-4 rounded-xl font-semibold text-base transition-all active:scale-[0.98]"
          style={{ 
            backgroundColor: colors.teal.primary,
            color: '#ffffff',
            boxShadow: '0 4px 12px rgba(62, 130, 122, 0.3)',
          }}
          data-testid="package-checkout-btn"
        >
          Start My Journey • {formatPrice(price)}
        </button>
        <p className="text-center text-xs mt-2" style={{ color: colors.text.secondary }}>
          100% satisfaction guaranteed
        </p>
      </div>
    </div>
  );
}
