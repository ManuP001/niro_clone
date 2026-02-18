import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { colors } from './theme';

/**
 * PublicNavHeader - Shared navigation header for all public pages
 * Shows: Logo, Nav Links (Life Topics, Experts, Remedies), CTA button
 */

const NAV_LINKS = [
  { id: 'topics', label: 'Life Topics', href: '/topics' },
  { id: 'experts', label: 'Experts', href: '/experts' },
  { id: 'remedies', label: 'Remedies', href: '/remedies' },
];

export default function PublicNavHeader({ isAuthenticated, showBackButton = false, onBackClick }) {
  const navigate = useNavigate();
  const location = useLocation();

  const handleNavClick = (link) => {
    if (link.requiresAuth && !isAuthenticated) {
      // Store intent and redirect to login
      localStorage.setItem('niro_user_intent', JSON.stringify({ type: 'browse_remedies' }));
      navigate('/login');
    } else {
      navigate(link.href);
    }
  };

  const handleLogoClick = () => {
    navigate('/');
  };

  const handleCtaClick = () => {
    if (isAuthenticated) {
      navigate('/app/schedule');
    } else {
      localStorage.setItem('niro_user_intent', JSON.stringify({ type: 'free_call' }));
      navigate('/login');
    }
  };

  return (
    <header
      className="sticky top-0 z-50"
      style={{
        backgroundColor: 'rgba(251,248,243,0.95)',
        backdropFilter: 'blur(20px)',
        borderBottom: '1px solid rgba(0,0,0,0.06)',
      }}
    >
      <div className="max-w-7xl mx-auto px-4 md:px-8">
        <div className="flex items-center justify-between h-16 md:h-20">
          {/* Left: Back + Logo */}
          <div className="flex items-center gap-3">
            {showBackButton && (
              <button
                onClick={onBackClick || handleLogoClick}
                className="p-2 -ml-2 rounded-full hover:bg-black/5 transition-colors"
                data-testid="back-btn"
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
            )}
            <button 
              onClick={handleLogoClick} 
              className="flex items-center" 
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
          </div>

          {/* Center: Navigation Links (desktop) */}
          <nav className="hidden md:flex items-center gap-8">
            {NAV_LINKS.map((link) => {
              const isActive = location.pathname === link.href;
              return (
                <button
                  key={link.id}
                  onClick={() => handleNavClick(link)}
                  className="text-sm font-medium transition-colors relative py-2"
                  style={{ 
                    color: isActive ? colors.teal.primary : colors.text.secondary,
                  }}
                  data-testid={`nav-${link.id}`}
                >
                  {link.label}
                  {isActive && (
                    <span 
                      className="absolute bottom-0 left-0 right-0 h-0.5 rounded-full"
                      style={{ backgroundColor: colors.teal.primary }}
                    />
                  )}
                </button>
              );
            })}
          </nav>

          {/* Right: CTA */}
          <button
            onClick={handleCtaClick}
            className="flex items-center gap-2 px-4 md:px-5 py-2 md:py-2.5 rounded-full text-xs md:text-sm font-medium transition-all hover:shadow-md hover:-translate-y-0.5"
            style={{
              backgroundColor: colors.teal.primary,
              color: '#ffffff',
            }}
            data-testid="header-cta-btn"
          >
            <span className="hidden sm:inline">📞</span>
            <span className="sm:hidden">📞</span>
            <span className="hidden sm:inline">Get a free 10 mins consultation</span>
            <span className="sm:hidden">Free Call</span>
          </button>
        </div>

        {/* Mobile Navigation */}
        <nav className="flex md:hidden items-center justify-center gap-6 pb-3 -mt-1">
          {NAV_LINKS.map((link) => {
            const isActive = location.pathname === link.href;
            return (
              <button
                key={link.id}
                onClick={() => handleNavClick(link)}
                className="text-xs font-medium transition-colors relative py-1"
                style={{ 
                  color: isActive ? colors.teal.primary : colors.text.secondary,
                }}
                data-testid={`nav-mobile-${link.id}`}
              >
                {link.label}
                {isActive && (
                  <span 
                    className="absolute -bottom-0.5 left-0 right-0 h-0.5 rounded-full"
                    style={{ backgroundColor: colors.teal.primary }}
                  />
                )}
              </button>
            );
          })}
        </nav>
      </div>
    </header>
  );
}
