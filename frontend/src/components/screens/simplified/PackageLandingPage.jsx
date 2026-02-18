import React, { useState, useEffect } from 'react';
import { colors, shadows } from './theme';
import { CheckIcon, ChevronRightIcon } from './icons.jsx';
import { trackEvent } from './utils';
import { getBackendUrl } from '../../../config';
import ResponsiveHeader from './ResponsiveHeader';

/**
 * PackageLandingPage V2 - Redesigned to match homepage aesthetic
 * 
 * Key Changes:
 * - ResponsiveHeader integration
 * - Centered max-width container
 * - Card-based sections with consistent styling
 * - Teal/cream color scheme
 * - Better typography hierarchy
 */

export default function PackageLandingPage({ 
  token, 
  packageId, 
  tileData,
  onCheckout, 
  onBack,
  onNavigate,
  onTabChange,
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

  // Loading state
  if (loading) {
    return (
      <div 
        className="min-h-screen flex items-center justify-center"
        style={{ backgroundColor: colors.background.primary }}
      >
        <div className="text-center">
          <div 
            className="w-12 h-12 border-4 rounded-full animate-spin mx-auto mb-4"
            style={{ borderColor: `${colors.teal.primary}30`, borderTopColor: colors.teal.primary }}
          />
          <p style={{ color: colors.text.muted }}>Loading package...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (error || !packageData) {
    return (
      <div 
        className="min-h-screen flex items-center justify-center p-6"
        style={{ backgroundColor: colors.background.primary }}
      >
        <div className="text-center">
          <p style={{ color: colors.ui.error }} className="mb-4">{error || 'Package not found'}</p>
          <button onClick={onBack} style={{ color: colors.teal.primary }} className="font-medium">
            Go back
          </button>
        </div>
      </div>
    );
  }

  const content = packageData.content || {};
  const price = packageData.price || 0;
  const durationDays = packageData.duration_days || (packageData.duration_weeks ? packageData.duration_weeks * 7 : 7);

  // Build display content
  const heroTitle = content.hero_title || packageData.name || 'Package';
  const heroSubtitle = content.hero_subtitle || packageData.description || '';
  const trustLine = content.trust_line || '';
  const overviewTitle = content.overview_title || `${durationDays}-Day Guidance`;
  const overviewDescription = content.overview_description || packageData.description || 'Unlimited guidance on your topic';
  const includes = content.includes || packageData.features || [];
  const helpSections = content.help_sections || [];
  const analysisSections = content.analysis_sections || [];
  const analysisIntro = content.analysis_intro || '';
  const deliverables = content.deliverables || [];
  const customSections = content.custom_sections || [];

  return (
    <div 
      className={`min-h-screen ${hasBottomNav ? 'pb-32 md:pb-28' : 'pb-28'}`}
      style={{ backgroundColor: colors.background.primary }}
    >
      {/* Responsive Header */}
      <ResponsiveHeader
        title={heroTitle}
        showBackButton={true}
        onBack={onBack}
        onNavigate={onNavigate}
        onTabChange={onTabChange}
        ctaText="📞 Get a free 10 mins consultation"
      />

      {/* Main Content Container */}
      <div className="max-w-3xl mx-auto">
        {/* Hero Section */}
        <section className="px-4 md:px-8 pt-8 pb-6 text-center">
          <h1 
            className="text-2xl md:text-3xl lg:text-4xl font-bold mb-4"
            style={{ color: colors.text.dark }}
          >
            {heroTitle}
          </h1>
          {heroSubtitle && (
            <p 
              className="text-base md:text-lg leading-relaxed mb-4 max-w-2xl mx-auto"
              style={{ color: colors.text.secondary }}
            >
              {heroSubtitle}
            </p>
          )}
          {trustLine && (
            <p 
              className="text-sm md:text-base italic"
              style={{ color: colors.teal.primary }}
            >
              {trustLine}
            </p>
          )}
        </section>

        {/* Trust Badges */}
        <section className="px-4 md:px-8 py-4">
          <div className="flex justify-center gap-4 md:gap-6 flex-wrap">
            {['Senior experts', 'Unlimited follow-ups', 'Private & secure'].map((badge, i) => (
              <div 
                key={i}
                className="flex items-center gap-2 px-4 py-2 rounded-full"
                style={{ 
                  backgroundColor: `${colors.teal.primary}10`,
                  border: `1px solid ${colors.teal.primary}30`,
                }}
              >
                <CheckIcon className="w-4 h-4" style={{ color: colors.teal.primary }} />
                <span className="text-sm font-medium" style={{ color: colors.teal.dark }}>
                  {badge}
                </span>
              </div>
            ))}
          </div>
        </section>

        {/* Package Overview Card */}
        <section className="px-4 md:px-8 py-4">
          <div 
            className="rounded-2xl p-6 md:p-8"
            style={{ 
              backgroundColor: '#ffffff', 
              boxShadow: shadows.card,
              border: `1px solid ${colors.ui.borderDark}`,
            }}
            data-testid="package-overview-card"
          >
            <div className="flex flex-col md:flex-row md:justify-between md:items-start gap-4 mb-6">
              <div>
                <h2 className="text-xl md:text-2xl font-bold mb-2" style={{ color: colors.text.dark }}>
                  {overviewTitle}
                </h2>
                <p className="text-sm md:text-base" style={{ color: colors.text.secondary }}>
                  {overviewDescription}
                </p>
              </div>
              <div className="text-left md:text-right flex-shrink-0">
                <p className="text-2xl md:text-3xl font-bold" style={{ color: colors.teal.primary }}>
                  {formatPrice(price)}
                </p>
                <p className="text-sm" style={{ color: colors.text.muted }}>
                  {durationDays} days package
                </p>
              </div>
            </div>

            {/* What's Included */}
            {includes.length > 0 && (
              <div className="pt-6 border-t" style={{ borderColor: colors.ui.borderDark }}>
                <h3 className="text-base font-semibold mb-4" style={{ color: colors.text.dark }}>
                  What's included
                </h3>
                <div className="grid md:grid-cols-2 gap-3">
                  {includes.map((item, i) => (
                    <div key={i} className="flex items-start gap-3">
                      <div 
                        className="w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5"
                        style={{ backgroundColor: `${colors.teal.primary}15` }}
                      >
                        <CheckIcon className="w-3.5 h-3.5" style={{ color: colors.teal.primary }} />
                      </div>
                      <span className="text-sm md:text-base" style={{ color: colors.text.secondary }}>{item}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </section>

        {/* Help Sections */}
        {helpSections.length > 0 && (
          <section className="px-4 md:px-8 py-4">
            <h2 className="text-lg md:text-xl font-bold mb-4" style={{ color: colors.text.dark }}>
              What this helps you with
            </h2>
            <div className="space-y-3">
              {helpSections.map((section, i) => (
                <div 
                  key={i}
                  className="rounded-xl overflow-hidden"
                  style={{ 
                    backgroundColor: '#ffffff', 
                    boxShadow: shadows.card,
                    border: `1px solid ${colors.ui.borderDark}`,
                  }}
                >
                  <button
                    onClick={() => setExpandedSection(expandedSection === `help-${i}` ? null : `help-${i}`)}
                    className="w-full px-5 py-4 flex justify-between items-center hover:bg-black/[0.02] transition-colors"
                  >
                    <span className="font-semibold text-sm md:text-base" style={{ color: colors.text.dark }}>
                      {section.title}
                    </span>
                    <ChevronRightIcon 
                      className={`w-5 h-5 transition-transform duration-200 ${expandedSection === `help-${i}` ? 'rotate-90' : ''}`}
                      style={{ color: colors.text.muted }}
                    />
                  </button>
                  {expandedSection === `help-${i}` && section.items && (
                    <div className="px-5 pb-4">
                      <ul className="space-y-2">
                        {section.items.map((item, j) => (
                          <li key={j} className="flex items-start gap-3">
                            <CheckIcon className="w-4 h-4 mt-0.5 flex-shrink-0" style={{ color: colors.teal.primary }} />
                            <span className="text-sm md:text-base" style={{ color: colors.text.secondary }}>{item}</span>
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
        {deliverables.length > 0 && (
          <section className="px-4 md:px-8 py-4">
            <h2 className="text-lg md:text-xl font-bold mb-4" style={{ color: colors.text.dark }}>
              What you'll leave with
            </h2>
            <div 
              className="rounded-xl p-5 md:p-6"
              style={{ 
                backgroundColor: '#ffffff', 
                boxShadow: shadows.card,
                border: `1px solid ${colors.ui.borderDark}`,
              }}
            >
              <div className="grid md:grid-cols-2 gap-3">
                {deliverables.map((item, i) => (
                  <div key={i} className="flex items-start gap-3">
                    <div 
                      className="w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5"
                      style={{ backgroundColor: `${colors.peach.primary}20` }}
                    >
                      <CheckIcon className="w-3.5 h-3.5" style={{ color: colors.peach.primary }} />
                    </div>
                    <span className="text-sm md:text-base" style={{ color: colors.text.secondary }}>{item}</span>
                  </div>
                ))}
              </div>
            </div>
          </section>
        )}

        {/* Analysis Sections */}
        {analysisSections.length > 0 && (
          <section className="px-4 md:px-8 py-4">
            <h2 className="text-lg md:text-xl font-bold mb-2" style={{ color: colors.text.dark }}>
              How we analyse your situation
            </h2>
            {analysisIntro && (
              <p className="text-sm md:text-base mb-4" style={{ color: colors.text.secondary }}>
                {analysisIntro}
              </p>
            )}
            <div className="space-y-3">
              {analysisSections.map((section, i) => (
                <div 
                  key={i}
                  className="rounded-xl overflow-hidden"
                  style={{ 
                    backgroundColor: '#ffffff', 
                    boxShadow: shadows.card,
                    border: `1px solid ${colors.ui.borderDark}`,
                  }}
                >
                  <button
                    onClick={() => setExpandedSection(expandedSection === `analysis-${i}` ? null : `analysis-${i}`)}
                    className="w-full px-5 py-4 flex justify-between items-center hover:bg-black/[0.02] transition-colors"
                  >
                    <span className="font-semibold text-sm md:text-base" style={{ color: colors.text.dark }}>
                      {section.title}
                    </span>
                    <ChevronRightIcon 
                      className={`w-5 h-5 transition-transform duration-200 ${expandedSection === `analysis-${i}` ? 'rotate-90' : ''}`}
                      style={{ color: colors.text.muted }}
                    />
                  </button>
                  {expandedSection === `analysis-${i}` && section.items && (
                    <div className="px-5 pb-4">
                      <ul className="space-y-2">
                        {section.items.map((item, j) => (
                          <li key={j} className="flex items-start gap-3">
                            <CheckIcon className="w-4 h-4 mt-0.5 flex-shrink-0" style={{ color: colors.teal.primary }} />
                            <span className="text-sm md:text-base" style={{ color: colors.text.secondary }}>{item}</span>
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
        {customSections.length > 0 && customSections.map((section, i) => (
          <section key={i} className="px-4 md:px-8 py-4">
            <h2 className="text-lg md:text-xl font-bold mb-4" style={{ color: colors.text.dark }}>
              {section.title}
            </h2>
            <div 
              className="rounded-xl p-5 md:p-6"
              style={{ 
                backgroundColor: '#ffffff', 
                boxShadow: shadows.card,
                border: `1px solid ${colors.ui.borderDark}`,
              }}
            >
              {section.content_type === 'paragraph' && section.text ? (
                <p className="text-sm md:text-base leading-relaxed" style={{ color: colors.text.secondary }}>
                  {section.text}
                </p>
              ) : section.items ? (
                <ul className="space-y-2">
                  {section.items.map((item, j) => (
                    <li key={j} className="flex items-start gap-3">
                      <CheckIcon className="w-4 h-4 mt-0.5 flex-shrink-0" style={{ color: colors.teal.primary }} />
                      <span className="text-sm md:text-base" style={{ color: colors.text.secondary }}>{item}</span>
                    </li>
                  ))}
                </ul>
              ) : null}
            </div>
          </section>
        ))}

        {/* Trust & Privacy Note */}
        <section className="px-4 md:px-8 py-6">
          <div 
            className="rounded-xl p-5 md:p-6 text-center"
            style={{ 
              backgroundColor: `${colors.teal.primary}08`,
              border: `1px solid ${colors.teal.primary}20`,
            }}
          >
            <div 
              className="w-12 h-12 rounded-full mx-auto mb-3 flex items-center justify-center"
              style={{ backgroundColor: `${colors.teal.primary}15` }}
            >
              <svg className="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke={colors.teal.primary} strokeWidth="2">
                <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
              </svg>
            </div>
            <p className="text-sm md:text-base" style={{ color: colors.text.secondary }}>
              We focus on clarity and timing — not fear. Your conversations are private and confidential.
            </p>
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
        <div className="max-w-3xl mx-auto px-4 md:px-8 py-4 flex items-center justify-between gap-4">
          <div>
            <p className="text-xl md:text-2xl font-bold" style={{ color: colors.text.dark }}>
              {formatPrice(price)}
            </p>
            <p className="text-xs md:text-sm" style={{ color: colors.text.muted }}>
              {durationDays} days • 100% satisfaction guaranteed
            </p>
          </div>
          <button
            onClick={handleCheckout}
            className="px-6 md:px-8 py-3 md:py-4 rounded-full font-semibold text-base transition-all active:scale-[0.98] hover:shadow-lg hover:-translate-y-0.5"
            style={{ 
              backgroundColor: colors.peach.primary,
              color: colors.text.dark,
              boxShadow: shadows.peach,
            }}
            data-testid="package-checkout-btn"
          >
            Start my journey
          </button>
        </div>
      </div>
    </div>
  );
}
