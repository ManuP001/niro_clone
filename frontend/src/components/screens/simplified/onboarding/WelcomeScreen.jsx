import React from 'react';
import { colors, shadows } from '../theme';

/**
 * WelcomeScreen - Onboarding Step 1
 * Headline + single tagline + Get Started CTA
 * Updated with teal-gold color scheme
 */
export default function WelcomeScreen({ onNext }) {
  return (
    <div 
      className="fixed inset-0 flex flex-col items-center justify-center px-8"
      style={{ 
        background: colors.background.gradient,
        paddingTop: 'env(safe-area-inset-top)',
        paddingBottom: 'env(safe-area-inset-bottom)',
      }}
    >
      {/* Constellation Background */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <svg className="absolute w-full h-full opacity-15" viewBox="0 0 400 800">
          <g stroke="#ffffff" strokeWidth="0.5" fill="none">
            <line x1="80" y1="100" x2="150" y2="160" />
            <line x1="150" y1="160" x2="220" y2="120" />
            <line x1="220" y1="120" x2="300" y2="180" />
            <line x1="50" y1="350" x2="120" y2="400" />
            <line x1="120" y1="400" x2="200" y2="360" />
            <line x1="280" y1="320" x2="360" y2="380" />
          </g>
          <g fill="#ffffff">
            <circle cx="80" cy="100" r="2" />
            <circle cx="150" cy="160" r="3" />
            <circle cx="220" cy="120" r="2" />
            <circle cx="300" cy="180" r="2" />
            <circle cx="50" cy="350" r="2" />
            <circle cx="120" cy="400" r="3" />
            <circle cx="200" cy="360" r="2" />
            <circle cx="280" cy="320" r="2" />
            <circle cx="360" cy="380" r="2" />
          </g>
        </svg>
      </div>

      <div className="text-center relative z-10 max-w-sm">
        {/* Logo */}
        <div className="relative w-36 h-36 mx-auto mb-8">
          <svg 
            className="absolute inset-0 w-full h-full animate-spin-slow" 
            viewBox="0 0 160 160"
            style={{ animationDuration: '20s' }}
          >
            <g stroke="rgba(255,255,255,0.4)" strokeWidth="1" fill="none">
              <polygon points="80,8 100,25 120,25 112,48 120,72 100,72 80,88 60,72 40,72 48,48 40,25 60,25" />
            </g>
            <g fill="rgba(255,255,255,0.6)">
              <circle cx="80" cy="8" r="3" />
              <circle cx="100" cy="25" r="2" />
              <circle cx="120" cy="25" r="2.5" />
              <circle cx="112" cy="48" r="2" />
              <circle cx="120" cy="72" r="2.5" />
              <circle cx="100" cy="72" r="2" />
              <circle cx="80" cy="88" r="3" />
              <circle cx="60" cy="72" r="2" />
              <circle cx="40" cy="72" r="2.5" />
              <circle cx="48" cy="48" r="2" />
              <circle cx="40" cy="25" r="2.5" />
              <circle cx="60" cy="25" r="2" />
            </g>
          </svg>
          
          <div 
            className="absolute inset-6 rounded-full"
            style={{ 
              background: 'radial-gradient(circle, rgba(239,225,169,0.3) 0%, transparent 100%)',
              boxShadow: '0 0 40px rgba(239,225,169,0.3)',
            }}
          />
          
          <div className="absolute inset-0 flex items-center justify-center">
            <span 
              className="text-3xl font-bold tracking-wide"
              style={{ 
                fontFamily: "'Kumbh Sans', 'Inter', sans-serif",
                background: colors.logo.gradient,
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                backgroundClip: 'text',
              }}
            >
              niro
            </span>
          </div>
        </div>
        
        {/* Headline */}
        <h1 
          className="text-2xl font-semibold mb-6 leading-tight"
          style={{ color: '#ffffff' }}
        >
          Guidance for life&apos;s biggest decisions
        </h1>
        
        {/* CTA */}
        <button
          onClick={onNext}
          className="w-full py-4 rounded-2xl font-semibold text-base transition-all hover:shadow-lg active:scale-[0.98]"
          style={{ 
            backgroundColor: colors.gold.primary, 
            color: colors.text.dark,
            boxShadow: shadows.md,
          }}
        >
          Get started
        </button>
      </div>
    </div>
  );
}
