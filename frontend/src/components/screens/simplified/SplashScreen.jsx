import React, { useEffect, useState } from 'react';
import { colors } from './theme';

/**
 * SplashScreen - Single splash with NIRO branding (V5)
 * Updated with new teal-gold gradient
 */
export default function SplashScreen({ onComplete }) {
  const [isAnimating, setIsAnimating] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => {
      setIsAnimating(false);
      setTimeout(onComplete, 300);
    }, 2000);
    return () => clearTimeout(timer);
  }, [onComplete]);

  return (
    <div 
      className={`fixed inset-0 flex items-center justify-center transition-opacity duration-300 ${isAnimating ? 'opacity-100' : 'opacity-0'}`}
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
            <line x1="70" y1="550" x2="140" y2="600" />
            <line x1="140" y1="600" x2="220" y2="560" />
            <line x1="300" y1="520" x2="370" y2="580" />
          </g>
          <g fill="#ffffff">
            <circle cx="80" cy="100" r="2" className="animate-pulse" />
            <circle cx="150" cy="160" r="3" />
            <circle cx="220" cy="120" r="2" className="animate-pulse" />
            <circle cx="300" cy="180" r="2" />
            <circle cx="50" cy="350" r="2" />
            <circle cx="120" cy="400" r="3" className="animate-pulse" />
            <circle cx="200" cy="360" r="2" />
            <circle cx="280" cy="320" r="2" className="animate-pulse" />
            <circle cx="360" cy="380" r="2" />
            <circle cx="70" cy="550" r="2" />
            <circle cx="140" cy="600" r="3" className="animate-pulse" />
            <circle cx="220" cy="560" r="2" />
            <circle cx="300" cy="520" r="2" />
            <circle cx="370" cy="580" r="2" className="animate-pulse" />
          </g>
        </svg>
      </div>

      {/* Logo */}
      <div className="relative z-10 text-center">
        {/* Animated Ring */}
        <div className="relative w-40 h-40 mx-auto mb-6">
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
          
          {/* Inner Glow */}
          <div 
            className="absolute inset-8 rounded-full"
            style={{ 
              background: 'radial-gradient(circle, rgba(255,255,255,0.25) 0%, rgba(255,255,255,0.05) 100%)',
              boxShadow: '0 0 60px rgba(239,225,169,0.4)'
            }}
          />
          
          {/* Logo Text */}
          <div className="absolute inset-0 flex items-center justify-center">
            <span 
              className="text-4xl font-bold tracking-wide"
              style={{ 
                fontFamily: "'Kumbh Sans', 'Inter', sans-serif",
                background: colors.logo.gradient,
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                backgroundClip: 'text',
                textShadow: '0 2px 10px rgba(0,0,0,0.15)',
              }}
            >
              niro
            </span>
          </div>
        </div>
        
        {/* Subtitle */}
        <p 
          className="text-xs tracking-[0.3em] uppercase"
          style={{ color: colors.gold.primary }}
        >
          Astrology
        </p>
      </div>
    </div>
  );
}
