import React from 'react';
import { colors, shadows, borderRadius } from './theme';
import { SparklesIcon, ChatIcon, ConsultIcon } from './icons';

/**
 * HeroSection - New hero with Niro branding and dual CTAs (HORIZONTAL layout)
 * Based on user reference images
 */
export default function HeroSection({ onChatWithMira, onTalkToHuman }) {
  return (
    <div 
      className="relative overflow-hidden px-5 pt-8 pb-10"
      style={{ 
        background: colors.background.gradient,
        minHeight: '280px',
      }}
    >
      {/* Animated background elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        {/* Subtle floating orbs */}
        <div 
          className="absolute w-64 h-64 rounded-full opacity-20 animate-float-slow"
          style={{ 
            background: 'radial-gradient(circle, rgba(239,225,169,0.4) 0%, transparent 70%)',
            top: '-20%',
            right: '-10%',
          }}
        />
        <div 
          className="absolute w-48 h-48 rounded-full opacity-15 animate-float-slower"
          style={{ 
            background: 'radial-gradient(circle, rgba(255,255,195,0.5) 0%, transparent 70%)',
            bottom: '10%',
            left: '-10%',
          }}
        />
        
        {/* Constellation dots */}
        <svg className="absolute inset-0 w-full h-full opacity-20" viewBox="0 0 400 400">
          <g fill="rgba(255,255,255,0.6)">
            <circle cx="50" cy="80" r="2" className="animate-pulse-slow" />
            <circle cx="120" cy="50" r="1.5" />
            <circle cx="300" cy="100" r="2" className="animate-pulse-slow" />
            <circle cx="350" cy="60" r="1.5" />
            <circle cx="80" cy="200" r="1.5" className="animate-pulse-slow" />
            <circle cx="320" cy="180" r="2" />
            <circle cx="150" cy="250" r="1.5" />
            <circle cx="250" cy="280" r="2" className="animate-pulse-slow" />
          </g>
          <g stroke="rgba(255,255,255,0.15)" strokeWidth="0.5" fill="none">
            <line x1="50" y1="80" x2="120" y2="50" />
            <line x1="300" y1="100" x2="350" y2="60" />
            <line x1="150" y1="250" x2="250" y2="280" />
          </g>
        </svg>
      </div>

      {/* Content */}
      <div className="relative z-10">
        {/* Logo */}
        <div className="text-center mb-6">
          <h1 
            className="text-4xl font-bold tracking-wide"
            style={{ 
              fontFamily: "'Kumbh Sans', sans-serif",
              background: colors.logo.gradient,
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundClip: 'text',
              textShadow: '0 2px 20px rgba(239,225,169,0.3)',
            }}
          >
            niro
          </h1>
        </div>

        {/* Tagline */}
        <div className="text-center mb-6">
          <p 
            className="text-sm mb-1"
            style={{ color: 'rgba(255,255,255,0.7)' }}
          >
            Not predictions. Not generic advice.
          </p>
          <h2 
            className="text-xl font-semibold leading-tight"
            style={{ color: colors.text.primary }}
          >
            Expert guidance through life&apos;s important phases.
          </h2>
        </div>

        {/* Dual CTAs - HORIZONTAL Layout */}
        <div className="flex gap-3">
          {/* Primary CTA: Chat with Mira */}
          <button
            onClick={onChatWithMira}
            className="flex-1 flex items-center justify-center gap-2 py-3.5 rounded-xl font-semibold text-sm transition-all active:scale-[0.98] hover:shadow-lg"
            style={{ 
              backgroundColor: colors.gold.primary,
              color: colors.text.dark,
              boxShadow: shadows.md,
            }}
          >
            <SparklesIcon className="w-4 h-4" />
            Chat with Mira
          </button>

          {/* Secondary CTA: Talk to Human */}
          <button
            onClick={onTalkToHuman}
            className="flex-1 flex items-center justify-center gap-2 py-3.5 rounded-xl font-medium text-sm transition-all active:scale-[0.98]"
            style={{ 
              backgroundColor: 'rgba(255,255,255,0.15)',
              color: colors.text.primary,
              border: `1px solid ${colors.ui.border}`,
              backdropFilter: 'blur(10px)',
            }}
          >
            <ConsultIcon className="w-4 h-4" />
            Talk to Expert
          </button>
        </div>
      </div>

      {/* Bottom fade */}
      <div 
        className="absolute bottom-0 left-0 right-0 h-8"
        style={{ 
          background: `linear-gradient(to bottom, transparent, ${colors.teal.primary})`,
        }}
      />
    </div>
  );
}
