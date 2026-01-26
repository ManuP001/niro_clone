import React, { useEffect, useRef } from 'react';
import { BACKEND_URL } from '../../config';

/**
 * AuthCallback - Handles Google OAuth redirect
 * Processes session_id from URL fragment, exchanges for session_token
 * REMINDER: DO NOT HARDCODE THE URL, OR ADD ANY FALLBACKS OR REDIRECT URLS, THIS BREAKS THE AUTH
 */

const AuthCallback = ({ onAuthSuccess, onAuthError }) => {
  const hasProcessed = useRef(false);

  useEffect(() => {
    // Prevent double execution in StrictMode
    if (hasProcessed.current) return;
    hasProcessed.current = true;

    const processAuth = async () => {
      try {
        // Extract session_id from URL fragment
        const hash = window.location.hash;
        const params = new URLSearchParams(hash.replace('#', ''));
        const sessionId = params.get('session_id');

        console.log('AuthCallback: Processing session_id:', sessionId ? 'present' : 'missing');

        if (!sessionId) {
          throw new Error('No session_id in URL');
        }

        // Exchange session_id for our session_token
        const response = await fetch(`${BACKEND_URL}/api/auth/session`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify({ session_id: sessionId }),
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.detail || 'Authentication failed');
        }

        const data = await response.json();
        console.log('AuthCallback: Session exchange successful');

        // Store token in localStorage as backup
        if (data.token) {
          localStorage.setItem('auth_token', data.token);
          localStorage.setItem('user_id', data.user.user_id);
        }

        // Clear the URL hash
        window.history.replaceState(null, '', window.location.pathname);

        // Callback with user data
        if (onAuthSuccess) {
          onAuthSuccess(data.user, data.token);
        }

      } catch (error) {
        console.error('AuthCallback error:', error);
        if (onAuthError) {
          onAuthError(error.message);
        }
      }
    };

    processAuth();
  }, [onAuthSuccess, onAuthError]);

  return (
    <div
      className="min-h-screen flex flex-col items-center justify-center"
      style={{
        background: 'linear-gradient(180deg, #3E827A 0%, rgba(255, 255, 195, 0.58) 100%)',
      }}
    >
      {/* Loading indicator */}
      <div className="animate-spin rounded-full h-12 w-12 border-4 border-white border-t-transparent mb-4" />
      <p className="text-white text-lg">Signing you in...</p>
    </div>
  );
};

export default AuthCallback;
