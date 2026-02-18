import React, { useState, useEffect } from 'react';
import { BrowserRouter, useNavigate, useLocation } from 'react-router-dom';
import './App.css';
import { getAuthToken, getCurrentUser, clearAuthToken } from './utils/auth';
import { getBackendUrl } from './config';
import { clearUserIntent, getUserIntent } from './components/screens/simplified/PublicLandingPage';
import { AppRoutes } from './router';

/**
 * App.js - V11 with React Router
 * 
 * Entry Flow:
 * 1. All users land on PublicLandingPage (public, no auth required)
 * 2. CTAs trigger login with intent stored in localStorage
 * 3. After login, route based on intent + user type via React Router
 * 4. Proper URL-based navigation with browser history support
 */

function AppContent() {
  const navigate = useNavigate();
  const location = useLocation();

  const [authState, setAuthState] = useState({
    isLoading: true,
    isAuthenticated: false,
    user: null,
    profileComplete: false,
    token: null,
    userId: null,
  });

  // Check for auth callback (code in URL query params from Google OAuth)
  const isAuthCallback = location.pathname === '/auth/callback' || 
                         location.search.includes('code=');

  // Check auth status on mount
  useEffect(() => {
    // Skip auth check if we're processing OAuth callback
    if (isAuthCallback) {
      setAuthState(prev => ({ ...prev, isLoading: false }));
      return;
    }

    const checkAuth = async () => {
      const token = getAuthToken();
      const backendUrl = getBackendUrl();
      
      if (!token) {
        setAuthState({
          isLoading: false,
          isAuthenticated: false,
          user: null,
          profileComplete: false,
          token: null,
          userId: null,
        });
        return;
      }

      try {
        const user = await getCurrentUser(backendUrl);
        
        if (!user) {
          clearAuthToken();
          setAuthState({
            isLoading: false,
            isAuthenticated: false,
            user: null,
            profileComplete: false,
            token: null,
            userId: null,
          });
          return;
        }

        setAuthState({
          isLoading: false,
          isAuthenticated: true,
          user,
          profileComplete: user.profile_complete || !!user.dob,
          token,
          userId: user.id,
        });
      } catch (err) {
        console.error('Auth check failed:', err);
        clearAuthToken();
        setAuthState({
          isLoading: false,
          isAuthenticated: false,
          user: null,
          profileComplete: false,
          token: null,
          userId: null,
        });
      }
    };

    checkAuth();
  }, [isAuthCallback]);

  // Handle login success
  const handleLoginSuccess = (user, token) => {
    if (token && user?.user_id) {
      localStorage.setItem('auth_token', token);
      localStorage.setItem('user_id', user.user_id);
    }
    
    const profileComplete = user?.profile_complete || !!user?.dob;
    
    if (profileComplete) {
      localStorage.setItem('niro_user_details_completed', 'true');
      localStorage.setItem('niro_onboarding_completed', 'true');
    }
    
    setAuthState({
      isLoading: false,
      isAuthenticated: true,
      user,
      profileComplete,
      token,
      userId: user?.user_id,
    });
    
    // Clear URL path after OAuth callback
    if (location.pathname === '/auth/callback') {
      // Check for stored intent and navigate accordingly
      const intent = getUserIntent();
      if (intent) {
        if (intent.type === 'free_call') {
          navigate('/app/schedule', { replace: true });
        } else if (intent.type === 'consultation') {
          navigate('/app', { replace: true });
        } else {
          navigate('/app', { replace: true });
        }
      } else {
        navigate('/', { replace: true });
      }
    } else {
      // Check for stored intent
      const intent = getUserIntent();
      if (intent) {
        navigate('/app', { replace: true });
      }
    }
  };

  // Handle auth error
  const handleAuthError = (error) => {
    console.error('Auth error:', error);
    clearUserIntent();
    setAuthState({
      isLoading: false,
      isAuthenticated: false,
      user: null,
      profileComplete: false,
      token: null,
      userId: null,
    });
    navigate('/', { replace: true });
  };

  // Handle logout
  const handleLogout = () => {
    clearAuthToken();
    clearUserIntent();
    setAuthState({
      isLoading: false,
      isAuthenticated: false,
      user: null,
      profileComplete: false,
      token: null,
      userId: null,
    });
    navigate('/', { replace: true });
  };

  // Handle login click from landing page
  const handleLoginClick = () => {
    navigate('/login');
  };

  // Handle navigation to app from landing page (for logged-in users)
  const handleNavigateToApp = (screen, params = {}) => {
    switch (screen) {
      case 'mypack':
        navigate('/app/mypack');
        break;
      case 'astro':
        navigate('/app/astro');
        break;
      case 'profile':
        navigate('/app/profile');
        break;
      case 'experts':
        navigate('/app/experts');
        break;
      case 'schedule':
        navigate('/app/schedule');
        break;
      case 'home':
      case 'topics':
        navigate('/app');
        break;
      default:
        navigate('/app');
    }
  };

  // Show loading state
  if (authState.isLoading) {
    return (
      <div className="h-screen w-full flex items-center justify-center" style={{ backgroundColor: '#FBF8F3' }}>
        <div className="text-center">
          <div className="w-12 h-12 bg-gradient-to-br from-teal-500 to-teal-600 rounded-full flex items-center justify-center mx-auto mb-4">
            <span className="text-white text-lg font-bold" style={{ fontFamily: "'Lexend', sans-serif" }}>n</span>
          </div>
          <p className="text-gray-600" style={{ fontFamily: "'Lexend', sans-serif" }}>Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="App min-h-screen" style={{ backgroundColor: '#FBF8F3' }}>
      <AppRoutes
        authState={authState}
        onLoginSuccess={handleLoginSuccess}
        onAuthError={handleAuthError}
        onLogout={handleLogout}
        onLoginClick={handleLoginClick}
        onNavigateToApp={handleNavigateToApp}
      />
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <AppContent />
    </BrowserRouter>
  );
}

export default App;
