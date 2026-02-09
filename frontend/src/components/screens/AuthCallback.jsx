import React, { useEffect, useRef } from 'react';
import { BACKEND_URL } from '../../config';

/**
 * AuthCallback - Handles Google OAuth redirect
 * Processes authorization code from URL query params
 * 
 * Flow for preview environments:
 * 1. Preview redirects to production for OAuth (since only getniro.ai is in Google Console)
 * 2. Production exchanges code, stores token
 * 3. Production redirects back to preview with token in URL
 * 4. Preview stores token and completes auth
 */

const AuthCallback = ({ onAuthSuccess, onAuthError }) => {
  const hasProcessed = useRef(false);

  useEffect(() => {
    // Prevent double execution in StrictMode
    if (hasProcessed.current) return;
    hasProcessed.current = true;

    const processAuth = async () => {
      try {
        // Check if we're receiving a token redirect from production (for preview environments)
        const urlParams = new URLSearchParams(window.location.search);
        const tokenFromRedirect = urlParams.get('token');
        const userDataEncoded = urlParams.get('user');
        
        if (tokenFromRedirect && userDataEncoded) {
          // This is a redirect from production with token - just store and complete
          console.log('AuthCallback: Received token redirect from production');
          const userData = JSON.parse(decodeURIComponent(userDataEncoded));
          
          localStorage.setItem('auth_token', tokenFromRedirect);
          localStorage.setItem('user_id', userData.user_id);
          
          if (userData.profile_complete || userData.dob) {
            localStorage.setItem('niro_user_details_completed', 'true');
            localStorage.setItem('niro_onboarding_completed', 'true');
          }
          
          // Clear the URL params
          window.history.replaceState(null, '', '/');
          
          if (onAuthSuccess) {
            onAuthSuccess(userData, tokenFromRedirect);
          }
          return;
        }

        // Normal flow - extract authorization code from URL query params
        const code = urlParams.get('code');
        const error = urlParams.get('error');

        console.log('AuthCallback: Processing auth code:', code ? 'present' : 'missing');

        if (error) {
          throw new Error(error === 'access_denied' ? 'Login was cancelled' : error);
        }

        if (!code) {
          throw new Error('No authorization code received');
        }

        // Check if we're on production and need to redirect back to preview
        const returnOrigin = localStorage.getItem('oauth_return_origin');
        const currentOrigin = window.location.origin;
        const isProduction = currentOrigin.includes('getniro.ai') || currentOrigin.includes('.emergent.host');
        
        // Exchange code for session token - use the same redirect_uri as login
        const PRODUCTION_ORIGIN = 'https://getniro.ai';
        const redirectUri = isProduction 
          ? currentOrigin + '/auth/callback'
          : PRODUCTION_ORIGIN + '/auth/callback';
        
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
        
        // If we're on production and need to redirect back to preview
        if (isProduction && returnOrigin && returnOrigin !== currentOrigin) {
          console.log('AuthCallback: Redirecting back to preview:', returnOrigin);
          localStorage.removeItem('oauth_return_origin');
          
          // Redirect to preview with token in URL
          const previewCallbackUrl = `${returnOrigin}/auth/callback?token=${encodeURIComponent(data.token)}&user=${encodeURIComponent(JSON.stringify(data.user))}`;
          window.location.href = previewCallbackUrl;
          return;
        }

        // Clear the URL params
        window.history.replaceState(null, '', '/');
        
        // Clear return origin if set
        localStorage.removeItem('oauth_return_origin');

        // Callback with user data
        if (onAuthSuccess) {
          onAuthSuccess(data.user, data.token);
        }

      } catch (error) {
        console.error('AuthCallback error:', error);
        // Clear URL params on error too
        window.history.replaceState(null, '', '/');
        localStorage.removeItem('oauth_return_origin');
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
