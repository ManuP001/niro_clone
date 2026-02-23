import React, { useState, useEffect } from 'react';
import { getBackendUrl } from '../../config';

/**
 * LoginScreen - Direct Google OAuth (V10 Design)
 * Updated to use Lexend font and new teal/peach/cream color scheme
 */

// Design system colors - V10 matching niro-final-marquee
const colors = {
  teal: {
    primary: '#4A9B8E',
    soft: '#6AB3A6',
    dark: '#2D5C4A',
  },
  peach: {
    primary: '#E8A87C',
    soft: '#F5C9A8',
  },
  cream: {
    primary: '#FBF8F3',
    warm: '#F5EFE7',
  },
  text: {
    dark: '#2D3748',
    secondary: '#5A6C7D',
    light: '#8F9BAA',
    onDark: '#FFFFFF',
    muted: 'rgba(255, 255, 255, 0.85)',
  },
  ui: {
    error: '#F44336',
  },
  background: {
    gradient: 'linear-gradient(180deg, #4A9B8E 0%, #FBF8F3 100%)',
  },
};

const shadows = {
  md: '0 4px 16px rgba(0, 0, 0, 0.12)',
  lg: '0 8px 32px rgba(0, 0, 0, 0.16)',
};

// Google icon SVG
const GoogleIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
    <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
    <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
    <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
    <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
  </svg>
);

const isLocalhost = typeof window !== 'undefined' && window.location.hostname === 'localhost';

const LoginScreen = ({ onLoginSuccess }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    const backendUrl = getBackendUrl();
    console.log('LoginScreen (Direct Google OAuth) initialized with BACKEND_URL:', backendUrl);
  }, []);

  const handleGoogleLogin = () => {
    setLoading(true);
    setError('');

    const callbackUrl = window.location.origin + '/auth/callback';
    const backendUrl = getBackendUrl();
    const googleLoginUrl = `${backendUrl}/api/auth/google/login?redirect_uri=${encodeURIComponent(callbackUrl)}`;

    console.log('Redirecting to Google OAuth:', googleLoginUrl);
    window.location.href = googleLoginUrl;
  };

  const handleDevLogin = async () => {
    setLoading(true);
    setError('');
    try {
      const backendUrl = getBackendUrl();
      const res = await fetch(`${backendUrl}/api/auth/dev-login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: 'dev@niro.local', name: 'Dev User' }),
      });
      const data = await res.json();
      if (data.ok && onLoginSuccess) {
        onLoginSuccess(data.user, data.token);
      } else {
        setError(data.detail || 'Dev login failed');
      }
    } catch (e) {
      setError('Dev login error: ' + e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      data-testid="login-screen"
      className="min-h-screen flex flex-col"
      style={{
        background: colors.background.gradient,
        fontFamily: "'Lexend', -apple-system, system-ui, sans-serif",
      }}
    >
      {/* Safe area top */}
      <div className="h-12" style={{ paddingTop: 'env(safe-area-inset-top)' }} />

      {/* Content */}
      <div className="flex-1 flex flex-col items-center justify-center px-6">
        {/* Logo */}
        <div className="mb-8">
          <h1
            className="text-5xl font-bold tracking-tight"
            style={{
              color: colors.text.onDark,
              fontFamily: "'Lexend', sans-serif",
              textShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
            }}
          >
            niro
          </h1>
        </div>

        {/* Tagline */}
        <p
          className="text-center text-lg mb-12 max-w-xs"
          style={{ color: colors.text.muted }}
        >
          Your personal astrology companion for life's big questions
        </p>

        {/* Google Sign-in Button */}
        <button
          data-testid="google-login-btn"
          onClick={handleGoogleLogin}
          disabled={loading}
          className="w-full max-w-sm py-4 px-6 rounded-full font-semibold text-base transition-all flex items-center justify-center gap-3 active:scale-[0.98] disabled:opacity-50 hover:shadow-lg"
          style={{
            backgroundColor: '#FFFFFF',
            color: colors.text.dark,
            boxShadow: shadows.md,
          }}
        >
          {loading ? (
            <div className="animate-spin rounded-full h-5 w-5 border-2 border-gray-300 border-t-gray-600" />
          ) : (
            <>
              <GoogleIcon />
              Login with Google
            </>
          )}
        </button>

        {/* Dev login — localhost only */}
        {isLocalhost && (
          <button
            onClick={handleDevLogin}
            disabled={loading}
            className="w-full max-w-sm mt-3 py-3 px-6 rounded-full font-medium text-sm transition-all disabled:opacity-50 border"
            style={{
              backgroundColor: 'transparent',
              color: colors.text.muted,
              borderColor: 'rgba(255,255,255,0.4)',
            }}
          >
            🛠 Dev Login (localhost only)
          </button>
        )}

        {/* Error message */}
        {error && (
          <p className="mt-4 text-sm text-center" style={{ color: colors.ui.error }}>
            {error}
          </p>
        )}

        {/* Trust indicators */}
        <div className="mt-12 flex items-center gap-6">
          <div className="flex items-center gap-2">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" style={{ color: colors.peach.primary }}>
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
            </svg>
            <span className="text-xs" style={{ color: colors.text.muted }}>Secure login</span>
          </div>
          <div className="flex items-center gap-2">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" style={{ color: colors.peach.primary }}>
              <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
              <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
            </svg>
            <span className="text-xs" style={{ color: colors.text.muted }}>Private data</span>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="pb-8 px-6 text-center">
        <p className="text-xs" style={{ color: colors.text.muted }}>
          By continuing, you agree to our Terms of Service and Privacy Policy
        </p>
      </div>
    </div>
  );
};

export default LoginScreen;
