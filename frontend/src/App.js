import React, { useState, useEffect } from 'react';
import './App.css';
import LoginScreen from './components/screens/LoginScreen';
import AuthCallback from './components/screens/AuthCallback';
import { ChatProvider } from './context/ChatContext';
import { getAuthToken, getCurrentUser, clearAuthToken } from './utils/auth';
import { getBackendUrl } from './config';

// Admin Dashboard
import AdminDashboard from './components/admin/AdminDashboard';

// NIRO V10 Imports - New Landing Page Flow
import { 
  SimplifiedApp, 
  PublicLandingPage, 
  getUserIntent, 
  clearUserIntent 
} from './components/screens/simplified';

/**
 * App.js - V10 Routing with Public Landing Page
 * 
 * Entry Flow:
 * 1. All users land on PublicLandingPage (public, no auth required)
 * 2. CTAs trigger login with intent stored in localStorage
 * 3. After login, route based on intent + user type:
 *    - free_call: Birth Details → Schedule Call
 *    - consultation:topic_id: Birth Details → Topics → Packages
 * 4. Logged-in users see landing page with access to app via nav
 */

function App() {
  const [authState, setAuthState] = useState({
    isLoading: true,
    isAuthenticated: false,
    user: null,
    profileComplete: false,
    token: null,
    userId: null,
  });
  
  // View state: 'landing' | 'login' | 'app'
  const [currentView, setCurrentView] = useState('landing');
  
  // App navigation params (for passing intent to SimplifiedApp)
  const [appParams, setAppParams] = useState(null);

  // Check for admin route
  const isAdminRoute = window.location.pathname.startsWith('/admin');
  
  // Check for auth callback (code in URL query params from Google OAuth)
  const isAuthCallback = window.location.pathname === '/auth/callback' || 
                         window.location.search.includes('code=');

  // Render admin dashboard if on /admin route
  if (isAdminRoute) {
    return <AdminDashboard />;
  }

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
  }, []);

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
    if (window.location.pathname === '/auth/callback') {
      window.history.replaceState(null, '', '/');
    }
    
    // Check for stored intent and navigate accordingly
    const intent = getUserIntent();
    if (intent) {
      // Pass intent to app for routing
      setAppParams({ intent, isNewUser: !profileComplete });
      setCurrentView('app');
    } else {
      // No intent - go to landing page (logged in state)
      setCurrentView('landing');
    }
  };

  // Handle auth error
  const handleAuthError = (error) => {
    console.error('Auth error:', error);
    clearUserIntent(); // Clear any stored intent
    setAuthState({
      isLoading: false,
      isAuthenticated: false,
      user: null,
      profileComplete: false,
      token: null,
      userId: null,
    });
    window.history.replaceState(null, '', '/');
    setCurrentView('landing');
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
    setCurrentView('landing');
  };

  // Handle login click from landing page
  const handleLoginClick = () => {
    setCurrentView('login');
  };

  // Handle navigation to app from landing page (for logged-in users)
  const handleNavigateToApp = (screen, params = {}) => {
    setAppParams({ screen, ...params });
    setCurrentView('app');
  };

  // Handle back to landing from app
  const handleBackToLanding = () => {
    setAppParams(null);
    setCurrentView('landing');
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

  // Handle OAuth callback
  if (isAuthCallback) {
    return (
      <AuthCallback 
        onAuthSuccess={handleLoginSuccess}
        onAuthError={handleAuthError}
      />
    );
  }

  // Show login screen
  if (currentView === 'login') {
    return <LoginScreen onLoginSuccess={handleLoginSuccess} />;
  }

  // Show app (for authenticated users with intent or direct navigation)
  if (currentView === 'app' && authState.isAuthenticated) {
    return (
      <ChatProvider>
        <div className="App min-h-screen" style={{ backgroundColor: '#FBF8F3' }}>
          <SimplifiedApp 
            token={authState.token} 
            userId={authState.userId}
            user={authState.user}
            initialIntent={appParams?.intent}
            initialScreen={appParams?.screen}
            initialParams={appParams}
            onBackToLanding={handleBackToLanding}
            onLogout={handleLogout}
          />
        </div>
      </ChatProvider>
    );
  }

  // Default: Show public landing page (for all users - logged in or not)
  return (
    <PublicLandingPage
      isAuthenticated={authState.isAuthenticated}
      user={authState.user}
      onLoginClick={handleLoginClick}
      onNavigateToApp={handleNavigateToApp}
    />
  );
}

export default App;
