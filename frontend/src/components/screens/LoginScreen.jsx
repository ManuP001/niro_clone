import React, { useState, useEffect } from 'react';
import { BACKEND_URL } from '../../config';

/**
 * LoginScreen - Updated with teal-gold design language (V5)
 * Matches the simplified screens color scheme
 */

// Design system colors - matching simplified/theme.js
const colors = {
  teal: {
    primary: '#3E827A',
    dark: '#2D5F59',
    light: '#5A9E96',
  },
  gold: {
    primary: '#EFE1A9',
    light: '#FFFFC3',
    cream: 'rgba(255, 255, 195, 0.58)',
  },
  text: {
    primary: '#FFFFFF',
    dark: '#2D2D2D',
    secondary: '#5C5C5C',
    muted: 'rgba(255, 255, 255, 0.7)',
    mutedDark: '#8A8A8A',
  },
  ui: {
    border: 'rgba(255, 255, 255, 0.2)',
    borderDark: 'rgba(0, 0, 0, 0.1)',
    error: '#F44336',
  },
  logo: {
    gradient: 'linear-gradient(135deg, #EFE1A9 0%, #FFFFFF 50%, #EFE1A9 100%)',
  },
  background: {
    gradient: 'linear-gradient(180deg, #3E827A 0%, rgba(255, 255, 195, 0.58) 100%)',
  },
};

const shadows = {
  md: '0 4px 16px rgba(0, 0, 0, 0.12)',
  lg: '0 8px 32px rgba(0, 0, 0, 0.16)',
};

const LoginScreen = ({ onLoginSuccess }) => {
  const [identifier, setIdentifier] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    console.log('LoginScreen initialized with BACKEND_URL:', BACKEND_URL);
  }, []);

  const handleContinue = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const url = `${BACKEND_URL}/api/auth/identify`;
      console.log('Identifying user at:', url);

      const response = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ identifier }),
      });

      const data = await response.json();
      console.log('Identify response:', response.status, data);

      if (!response.ok || !data.ok) {
        setError(data.detail || 'Failed to login');
        return;
      }

      // Save token and user_id to localStorage
      localStorage.setItem('auth_token', data.token);
      localStorage.setItem('user_id', data.user_id);

      console.log('Login successful, calling onLoginSuccess');
      // Call success callback
      onLoginSuccess(data.token, data.user_id);
    } catch (err) {
      console.error('Login error:', err);
      console.error('BACKEND_URL was:', BACKEND_URL);
      if (err.name === 'TypeError' && err.message.includes('fetch')) {
        setError('Network error. Please check your connection and try again.');
      } else {
        setError(`Network error: ${err.message}. Please try again.`);
      }
    } finally {
      setLoading(false);
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
          {/* Animated Logo Ring */}
          <div className="relative w-32 h-32 mx-auto mb-6">
            <svg 
              className="absolute inset-0 w-full h-full" 
              viewBox="0 0 160 160"
              style={{ animation: 'spin 20s linear infinite' }}
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
            
            {/* Inner glow */}
            <div 
              className="absolute inset-6 rounded-full"
              style={{ 
                background: 'radial-gradient(circle, rgba(239,225,169,0.3) 0%, transparent 100%)',
                boxShadow: '0 0 40px rgba(239,225,169,0.3)',
              }}
            />
            
            {/* Logo text */}
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
          
          {/* Subtitle */}
          <p 
            className="text-xs tracking-[0.3em] uppercase"
            style={{ color: colors.gold.primary }}
          >
            Astrology
          </p>
        </div>

        {/* Tagline */}
        <p 
          className="text-lg text-center mb-10 max-w-xs"
          style={{ color: colors.text.primary }}
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
          
          <form onSubmit={handleContinue}>
            <div className="mb-4">
              <label 
                className="block text-sm font-medium mb-2"
                style={{ color: colors.text.secondary }}
              >
                Email or Phone
              </label>
              <input
                type="text"
                value={identifier}
                onChange={(e) => setIdentifier(e.target.value)}
                placeholder="your@email.com or +91 987654"
                className="w-full px-4 py-3 rounded-xl text-base focus:outline-none focus:ring-2 transition-all"
                style={{ 
                  backgroundColor: colors.gold.cream,
                  border: `1px solid ${colors.ui.borderDark}`,
                  color: colors.text.dark,
                }}
              />
              {error && (
                <p className="mt-2 text-sm" style={{ color: colors.ui.error }}>{error}</p>
              )}
            </div>
            
            <button
              type="submit"
              disabled={loading}
              className="w-full py-4 rounded-xl font-semibold text-base transition-all hover:shadow-lg active:scale-[0.98] disabled:opacity-60"
              style={{ 
                backgroundColor: colors.gold.primary,
                color: colors.text.dark,
                boxShadow: shadows.md,
              }}
            >
              {loading ? 'Please wait...' : 'Continue'}
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
      
      {/* Spin animation keyframes */}
      <style>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};

export default LoginScreen;
