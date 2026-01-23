import React, { useState } from 'react';
import { colors, borderRadius, shadows } from './theme';

/**
 * LoginScreen - Redesigned with new teal-gold design language (V5)
 * Clean, premium aesthetic
 */
export default function LoginScreen({ onLogin }) {
  const [email, setEmail] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email.trim()) {
      setError('Please enter your email or phone');
      return;
    }
    
    setIsLoading(true);
    setError('');
    
    try {
      await onLogin(email);
    } catch (err) {
      setError('Something went wrong. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div 
      className="min-h-screen flex flex-col"
      style={{ 
        background: colors.background.gradient,
        paddingTop: 'env(safe-area-inset-top)',
        paddingBottom: 'env(safe-area-inset-bottom)',
      }}
    >
      {/* Constellation Background */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <svg className="absolute w-full h-full opacity-20" viewBox="0 0 400 800">
          <g stroke="#ffffff" strokeWidth="0.5" fill="none">
            <line x1="80" y1="60" x2="150" y2="120" />
            <line x1="150" y1="120" x2="200" y2="80" />
            <line x1="200" y1="80" x2="280" y2="140" />
            <line x1="280" y1="140" x2="350" y2="100" />
            <line x1="150" y1="120" x2="180" y2="200" />
            <line x1="50" y1="300" x2="120" y2="350" />
            <line x1="120" y1="350" x2="180" y2="320" />
            <line x1="180" y1="320" x2="250" y2="380" />
            <line x1="320" y1="250" x2="380" y2="300" />
            <line x1="100" y1="550" x2="160" y2="600" />
            <line x1="160" y1="600" x2="220" y2="560" />
            <line x1="280" y1="500" x2="340" y2="550" />
          </g>
          <g fill="#ffffff">
            <circle cx="80" cy="60" r="2" />
            <circle cx="150" cy="120" r="3" />
            <circle cx="200" cy="80" r="2" />
            <circle cx="280" cy="140" r="3" />
            <circle cx="350" cy="100" r="2" />
            <circle cx="180" cy="200" r="2" />
            <circle cx="50" cy="300" r="2" />
            <circle cx="120" cy="350" r="3" />
            <circle cx="180" cy="320" r="2" />
            <circle cx="250" cy="380" r="2" />
            <circle cx="320" cy="250" r="2" />
            <circle cx="380" cy="300" r="3" />
            <circle cx="100" cy="550" r="2" />
            <circle cx="160" cy="600" r="3" />
            <circle cx="220" cy="560" r="2" />
            <circle cx="280" cy="500" r="2" />
            <circle cx="340" cy="550" r="2" />
          </g>
        </svg>
      </div>

      {/* Content */}
      <div className="flex-1 flex flex-col items-center justify-center px-8 relative z-10">
        {/* Logo */}
        <div className="mb-10 text-center">
          <h1 
            className="text-5xl font-bold tracking-wide mb-2"
            style={{ 
              fontFamily: "'Kumbh Sans', 'Inter', sans-serif",
              background: colors.logo.gradient,
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundClip: 'text',
              textShadow: '0 2px 10px rgba(0,0,0,0.1)',
            }}
          >
            niro
          </h1>
          <p 
            className="text-sm tracking-[0.3em] uppercase"
            style={{ color: colors.gold.primary }}
          >
            Astrology
          </p>
        </div>

        {/* Tagline */}
        <p 
          className="text-lg text-center mb-12 max-w-xs"
          style={{ color: colors.text.primary, opacity: 0.9 }}
        >
          Trusted Astrology Guidance for Love, Career and Health
        </p>

        {/* Login Form */}
        <div 
          className="w-full max-w-sm p-6 rounded-2xl"
          style={{ 
            backgroundColor: 'rgba(255,255,255,0.95)',
            boxShadow: shadows.lg,
          }}
        >
          <h2 
            className="text-xl font-semibold text-center mb-6"
            style={{ color: colors.text.dark }}
          >
            Get Started
          </h2>
          
          <form onSubmit={handleSubmit}>
            <div className="mb-4">
              <label 
                className="block text-sm font-medium mb-2"
                style={{ color: colors.text.secondary }}
              >
                Email or Phone
              </label>
              <input
                type="text"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="your@email.com or +91 9876543210"
                className="w-full px-4 py-3 rounded-xl text-base focus:outline-none focus:ring-2 transition-all"
                style={{ 
                  backgroundColor: colors.gold.cream,
                  border: `1px solid ${colors.ui.borderDark}`,
                  color: colors.text.dark,
                  '--tw-ring-color': colors.teal.primary,
                }}
              />
              {error && (
                <p className="mt-2 text-sm text-red-500">{error}</p>
              )}
            </div>
            
            <button
              type="submit"
              disabled={isLoading}
              className="w-full py-4 rounded-xl font-semibold text-base transition-all hover:shadow-lg active:scale-[0.98] disabled:opacity-60"
              style={{ 
                backgroundColor: colors.gold.primary,
                color: colors.text.dark,
                boxShadow: shadows.md,
              }}
            >
              {isLoading ? 'Please wait...' : 'Continue'}
            </button>
          </form>
          
          <p 
            className="text-xs text-center mt-4"
            style={{ color: colors.text.mutedDark }}
          >
            By continuing, you agree to our Terms & Privacy Policy
          </p>
        </div>
      </div>

      {/* Bottom safe area spacer */}
      <div className="h-8" />
    </div>
  );
}
