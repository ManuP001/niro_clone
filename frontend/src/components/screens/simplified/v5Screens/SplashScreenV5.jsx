/**
 * NIRO V5 Splash Screen
 * First screen in the 8-step onboarding flow
 */

import React, { useEffect, useState } from 'react';
import { colors, typography } from '../theme';

export default function SplashScreenV5({ onComplete }) {
  const [fadeIn, setFadeIn] = useState(false);
  const [showCTA, setShowCTA] = useState(false);

  useEffect(() => {
    // Fade in logo
    setTimeout(() => setFadeIn(true), 100);
    // Show CTA after animation
    setTimeout(() => setShowCTA(true), 1500);
    // Auto-advance after 3 seconds if no interaction
    const timer = setTimeout(() => {
      if (onComplete) onComplete();
    }, 4000);

    return () => clearTimeout(timer);
  }, [onComplete]);

  return (
    <div 
      className="min-h-screen flex flex-col items-center justify-center relative overflow-hidden"
      style={{ 
        background: colors.background.gradient 
      }}
    >
      {/* Decorative elements */}
      <div 
        className="absolute top-0 left-0 w-64 h-64 rounded-full opacity-20 blur-3xl"
        style={{ background: colors.gold.primary, transform: 'translate(-50%, -50%)' }}
      />
      <div 
        className="absolute bottom-0 right-0 w-96 h-96 rounded-full opacity-15 blur-3xl"
        style={{ background: colors.gold.light, transform: 'translate(30%, 30%)' }}
      />

      {/* Logo & Brand */}
      <div 
        className={`flex flex-col items-center transition-all duration-1000 ${fadeIn ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'}`}
      >
        {/* Logo Mark */}
        <div 
          className="w-24 h-24 rounded-full flex items-center justify-center mb-6"
          style={{ 
            background: `linear-gradient(135deg, ${colors.gold.primary} 0%, ${colors.gold.light} 100%)`,
            boxShadow: `0 8px 32px rgba(239, 225, 169, 0.4)`
          }}
        >
          <svg 
            viewBox="0 0 60 60" 
            className="w-14 h-14"
            fill="none"
          >
            {/* Stylized star/cosmic symbol */}
            <circle cx="30" cy="30" r="20" stroke={colors.teal.dark} strokeWidth="2" fill="none" />
            <circle cx="30" cy="30" r="12" stroke={colors.teal.dark} strokeWidth="1.5" fill="none" />
            <circle cx="30" cy="30" r="4" fill={colors.teal.dark} />
            {/* Rays */}
            <line x1="30" y1="6" x2="30" y2="14" stroke={colors.teal.dark} strokeWidth="2" />
            <line x1="30" y1="46" x2="30" y2="54" stroke={colors.teal.dark} strokeWidth="2" />
            <line x1="6" y1="30" x2="14" y2="30" stroke={colors.teal.dark} strokeWidth="2" />
            <line x1="46" y1="30" x2="54" y2="30" stroke={colors.teal.dark} strokeWidth="2" />
          </svg>
        </div>

        {/* Brand Name */}
        <h1 
          className="text-5xl font-bold mb-3"
          style={{ 
            fontFamily: typography.fontFamily.logo,
            background: colors.logo.gradient,
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            backgroundClip: 'text',
          }}
        >
          NIRO
        </h1>

        {/* Tagline */}
        <p 
          className="text-lg font-medium mb-8"
          style={{ color: colors.gold.primary }}
        >
          Your Astrology Companion
        </p>
      </div>

      {/* CTA Button */}
      <div 
        className={`transition-all duration-700 ${showCTA ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}`}
      >
        <button
          onClick={onComplete}
          className="px-10 py-4 rounded-full font-semibold text-lg transition-all hover:scale-105 active:scale-95"
          style={{
            background: colors.gold.primary,
            color: colors.text.dark,
            boxShadow: `0 4px 20px rgba(239, 225, 169, 0.4)`
          }}
          data-testid="splash-get-started-btn"
        >
          Get Started
        </button>
      </div>

      {/* Bottom text */}
      <p 
        className={`absolute bottom-8 text-sm transition-opacity duration-500 ${showCTA ? 'opacity-70' : 'opacity-0'}`}
        style={{ color: colors.text.muted }}
      >
        Trusted by 50,000+ users
      </p>
    </div>
  );
}
