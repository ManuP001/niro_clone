import React, { useEffect, useRef } from 'react';
import { BACKEND_URL } from '../../config';

/**
 * AuthCallback - Handles Google OAuth redirect
 * Processes authorization code from URL query params
 */

const AuthCallback = ({ onAuthSuccess, onAuthError }) => {
  const hasProcessed = useRef(false);

  useEffect(() => {
    // Prevent double execution in StrictMode
    if (hasProcessed.current) return;
    hasProcessed.current = true;

    const processAuth = async () => {
      try {
        // Extract authorization code from URL query params
        const urlParams = new URLSearchParams(window.location.search);
        const code = urlParams.get('code');
        const error = urlParams.get('error');

        console.log('AuthCallback: Processing auth code:', code ? 'present' : 'missing');

        if (error) {
          throw new Error(error === 'access_denied' ? 'Login was cancelled' : error);
        }

        if (!code) {
          throw new Error('No authorization code received');
        }

        // Exchange code for session token
        const redirectUri = window.location.origin + '/auth/callback';
        
        const response = await fetch(`${BACKEND_URL}/api/auth/google/callback`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify({ 
            code: code,
            redirect_uri: redirectUri
          }),
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.detail || 'Authentication failed');
        }

        const data = await response.json();
        console.log('AuthCallback: Session exchange successful');

        // Store token in localStorage
        if (data.token) {
          localStorage.setItem('auth_token', data.token);
          localStorage.setItem('user_id', data.user.user_id);
        }

        // If user has profile complete, they're returning - mark onboarding done
        if (data.user.profile_complete || data.user.dob) {
          localStorage.setItem('niro_user_details_completed', 'true');
          localStorage.setItem('niro_onboarding_completed', 'true');
        }

        // Clear the URL params
        window.history.replaceState(null, '', '/');

        // Callback with user data
        if (onAuthSuccess) {
          onAuthSuccess(data.user, data.token);
        }

      } catch (error) {
        console.error('AuthCallback error:', error);
        // Clear URL params on error too
        window.history.replaceState(null, '', '/');
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
