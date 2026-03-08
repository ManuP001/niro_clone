import React, { useState } from 'react';
import { colors } from './theme';

/**
 * ResponsiveHeader - Desktop-visible header with navigation
 * Shows on screens >= 768px (md breakpoint)
 * Mobile uses back button only
 * 
 * Features:
 * - Niro logo (links to home)
 * - Main navigation links (Life topics, Experts, Remedies, Astro)
 * - CTA button in top-right
 * - Back button for sub-pages
 * - Mobile hamburger menu
 */

const NAV_ITEMS = [
  { id: 'home', label: 'Home', href: '/' },
  { id: 'topics', label: 'Life Topics', href: '/app' },
  { id: 'experts', label: 'Experts', href: '/app/experts' },
  { id: 'remedies', label: 'Remedies', href: '/app/remedies' },
  { id: 'account', label: 'My Account', href: '/app/account' },
];

export default function ResponsiveHeader({
  onBack,
  onNavigate,
  onOpenProfile,
  onTabChange,
  showBackButton = false,
  title = '',
  transparent = false,
  ctaText = 'Get a free 5 min consultation',
  onCtaClick,
  user,
}) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const handleNavClick = (item) => {
    setMobileMenuOpen(false);
    
    // Handle external href (like Home -> /)
    if (item.href) {
      window.location.href = item.href;
      return;
    }
    
    if (item.scrollTo) {
      const section = document.getElementById(item.scrollTo);
      if (section) {
        section.scrollIntoView({ behavior: 'smooth' });
      } else if (onTabChange) {
        onTabChange('home');
      }
    } else if (item.tab && onTabChange) {
      onTabChange(item.tab);
    } else if (item.screen && onNavigate) {
      onNavigate(item.screen);
    }
  };

  const handleCtaClick = () => {
    setMobileMenuOpen(false);
    if (onCtaClick) {
      onCtaClick();
    }
  };

  const handleLogoClick = () => {
    setMobileMenuOpen(false);
    if (onTabChange) {
      onTabChange('home');
    }
  };

  return (
    <>
      <header
        className="sticky top-0 z-50"
        style={{
          backgroundColor: transparent ? 'transparent' : 'rgba(251,248,243,0.95)',
          backdropFilter: transparent ? 'none' : 'blur(20px)',
          borderBottom: transparent ? 'none' : '1px solid rgba(0,0,0,0.06)',
        }}
      >
        <div className="max-w-7xl mx-auto px-4 md:px-8">
          <div className="flex items-center justify-between h-16 md:h-20">
            {/* Left: Back button (mobile/sub-pages) OR Logo */}
            <div className="flex items-center gap-3">
              {showBackButton && onBack ? (
                <button
                  onClick={onBack}
                  className="p-2 -ml-2 rounded-full hover:bg-black/5 transition-colors"
                  data-testid="header-back-btn"
                >
                  <svg
                    className="w-5 h-5"
                    style={{ color: colors.text.dark }}
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                  </svg>
                </button>
              ) : null}

              {/* Logo - always visible on desktop, hidden on mobile when showing back */}
              <button
                onClick={handleLogoClick}
                className={`flex items-center ${showBackButton ? 'hidden md:flex' : 'flex'}`}
                data-testid="header-logo"
              >
                <span
                  className="text-3xl md:text-4xl font-bold tracking-tight"
                  style={{
                    fontFamily: "'Lexend', sans-serif",
                    color: colors.teal.dark,
                  }}
                >
                  niro
                </span>
              </button>

              {/* Mobile title when showing back button */}
              {showBackButton && title && (
                <h1
                  className="text-lg font-semibold truncate md:hidden"
                  style={{ color: colors.text.dark }}
                >
                  {title}
                </h1>
              )}
            </div>

            {/* Center: Desktop Navigation */}
            <nav className="hidden md:flex items-center gap-8">
              {NAV_ITEMS.map((item) => (
                <button
                  key={item.id}
                  onClick={() => handleNavClick(item)}
                  className="text-[15px] font-medium transition-colors hover:text-[#4A9B8E]"
                  style={{ color: colors.text.muted }}
                  data-testid={`nav-link-${item.id}`}
                >
                  {item.label}
                </button>
              ))}
            </nav>

            {/* Right: CTA + Profile (desktop) / Hamburger (mobile) */}
            <div className="flex items-center gap-3">
              {/* Desktop CTA Button */}
              <button
                onClick={handleCtaClick}
                className="hidden md:flex items-center gap-2 px-7 py-3 rounded-full text-[15px] font-medium transition-all hover:shadow-lg hover:-translate-y-0.5"
                style={{
                  backgroundColor: colors.teal.primary,
                  color: '#ffffff',
                  boxShadow: '0 4px 12px rgba(74,155,142,0.25)',
                }}
                data-testid="header-cta-btn"
              >
                📞 {ctaText}
              </button>

              {/* Profile Button — shows user's initial when logged in */}
              {onOpenProfile && (
                <button
                  onClick={onOpenProfile}
                  className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-full transition-all hover:bg-black/5"
                  style={{ border: `1px solid ${colors.ui.borderDark}` }}
                  data-testid="header-profile-btn"
                >
                  <div
                    className="w-7 h-7 rounded-full flex items-center justify-center text-sm font-semibold"
                    style={{ backgroundColor: colors.teal.primary, color: '#fff' }}
                  >
                    {user?.name ? user.name.charAt(0).toUpperCase() : '?'}
                  </div>
                  {user?.name && (
                    <span className="text-sm font-medium max-w-[100px] truncate" style={{ color: colors.text.dark }}>
                      {user.name.split(' ')[0]}
                    </span>
                  )}
                </button>
              )}

              {/* Mobile: Hamburger Menu */}
              <button
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                className="md:hidden p-2 rounded-lg hover:bg-black/5 transition-colors"
                data-testid="mobile-menu-toggle"
              >
                {mobileMenuOpen ? (
                  <svg className="w-6 h-6" fill="none" stroke={colors.text.dark} viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                ) : (
                  <svg className="w-6 h-6" fill="none" stroke={colors.text.dark} viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                  </svg>
                )}
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Mobile Menu Overlay */}
      {mobileMenuOpen && (
        <div
          className="fixed inset-0 z-40 md:hidden"
          style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}
          onClick={() => setMobileMenuOpen(false)}
        >
          <div
            className="absolute top-16 left-0 right-0 py-4 px-4"
            style={{
              backgroundColor: colors.background.primary,
              boxShadow: '0 4px 20px rgba(0,0,0,0.1)',
            }}
            onClick={(e) => e.stopPropagation()}
          >
            {/* Navigation Links */}
            <nav className="space-y-1 mb-4">
              {NAV_ITEMS.map((item) => (
                <button
                  key={item.id}
                  onClick={() => handleNavClick(item)}
                  className="w-full text-left px-4 py-3 rounded-xl text-base font-medium transition-colors hover:bg-black/5"
                  style={{ color: colors.text.dark }}
                  data-testid={`mobile-nav-${item.id}`}
                >
                  {item.label}
                </button>
              ))}
            </nav>

            {/* Divider */}
            <div className="h-px mx-4 mb-4" style={{ backgroundColor: colors.ui.borderDark }} />

            {/* CTA Button */}
            <button
              onClick={handleCtaClick}
              className="w-full flex items-center justify-center gap-2 px-5 py-3 rounded-xl text-base font-semibold transition-all"
              style={{
                backgroundColor: colors.peach.primary,
                color: colors.text.dark,
              }}
              data-testid="mobile-cta-btn"
            >
              <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z" />
              </svg>
              {ctaText}
            </button>

            {/* Profile Link */}
            {onOpenProfile && (
              <button
                onClick={() => {
                  setMobileMenuOpen(false);
                  onOpenProfile();
                }}
                className="w-full flex items-center gap-3 px-4 py-3 mt-3 rounded-xl text-base font-medium transition-colors hover:bg-black/5"
                style={{ color: colors.text.dark }}
                data-testid="mobile-profile-btn"
              >
                <div
                  className="w-7 h-7 rounded-full flex items-center justify-center text-sm font-semibold flex-shrink-0"
                  style={{ backgroundColor: colors.teal.primary, color: '#fff' }}
                >
                  {user?.name ? user.name.charAt(0).toUpperCase() : '?'}
                </div>
                {user?.name ? `Hi, ${user.name.split(' ')[0]}` : 'My Profile'}
              </button>
            )}
          </div>
        </div>
      )}
    </>
  );
}
