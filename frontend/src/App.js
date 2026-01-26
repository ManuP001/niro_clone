import React, { useState, useEffect } from 'react';
import './App.css';
import LoginScreen from './components/screens/LoginScreen';
import AuthCallback from './components/screens/AuthCallback';
import OnboardingScreen from './components/screens/OnboardingScreen';
import HomeScreen from './components/screens/HomeScreen';
import ChatScreen from './components/screens/ChatScreen';
import KundliScreen from './components/screens/KundliScreen';
import HoroscopeScreen from './components/screens/HoroscopeScreen';
import PanchangScreen from './components/screens/PanchangScreen';
import CandidateSignalsScreen from './components/screens/CandidateSignalsScreen';
import BottomNav from './components/BottomNav';
import { ChatProvider } from './context/ChatContext';
import { getAuthToken, getCurrentUser, getUserProfile, clearAuthToken } from './utils/auth';
import { BACKEND_URL } from './config';

// NIRO V2 Imports
import { NiroV2App } from './components/screens/v2';

// NIRO Simplified V1 Imports
import { SimplifiedApp, SimplifiedAppV5 } from './components/screens/simplified';

function App() {
  const [authState, setAuthState] = useState({
    isLoading: true,
    isAuthenticated: false,
    user: null,
    profileComplete: false,
    token: null,
    userId: null,
  });
  const [activeScreen, setActiveScreen] = useState('home');
  // NIRO V2: Toggle between legacy and V2 UI
  const [useV2UI, setUseV2UI] = useState(false); // Default to Simplified
  // NIRO Simplified V1: New simplified flow
  const [useSimplified, setUseSimplified] = useState(true); // Default to Simplified V1
  // V5: Toggle between V4 and V5 onboarding
  const [useV5Flow, setUseV5Flow] = useState(false); // Default to V4

  // Check for auth callback (session_id in URL fragment) - MUST be synchronous
  const isAuthCallback = window.location.pathname === '/auth/callback' || 
                         window.location.hash.includes('session_id=');

  // Check auth status on mount
  useEffect(() => {
    // Skip auth check if we're processing OAuth callback
    if (isAuthCallback) {
      setAuthState(prev => ({ ...prev, isLoading: false }));
      return;
    }

    const checkAuth = async () => {
      const token = getAuthToken();
      
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
        const user = await getCurrentUser(BACKEND_URL);
        
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
          profileComplete: user.profile_complete,
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

  const handleLoginSuccess = (user, token) => {
    // Clear any previous onboarding state
    // localStorage.removeItem('niro_onboarding_completed');
    // localStorage.removeItem('niro_user_details_completed');
    
    setAuthState({
      isLoading: false,
      isAuthenticated: true,
      user,
      profileComplete: user?.profile_complete || false,
      token,
      userId: user?.user_id,
    });
    
    // Navigate to main app (clear auth callback path)
    if (window.location.pathname === '/auth/callback') {
      window.history.replaceState(null, '', '/');
    }
  };

  const handleAuthError = (error) => {
    console.error('Auth error:', error);
    setAuthState({
      isLoading: false,
      isAuthenticated: false,
      user: null,
      profileComplete: false,
      token: null,
      userId: null,
    });
    // Navigate back to login
    window.history.replaceState(null, '', '/');
  };

  const handleOnboardingComplete = () => {
    setAuthState((prev) => ({
      ...prev,
      profileComplete: true,
    }));
    setActiveScreen('chat');
  };

  const handleLogout = () => {
    clearAuthToken();
    setAuthState({
      isLoading: false,
      isAuthenticated: false,
      user: null,
      profileComplete: false,
      token: null,
      userId: null,
    });
    setActiveScreen('home');
  };

  // Show loading state
  if (authState.isLoading) {
    return (
      <div className="h-screen w-full bg-white flex items-center justify-center">
        <div className="text-center">
          <div className="w-12 h-12 bg-gradient-to-br from-emerald-600 to-teal-600 rounded-full flex items-center justify-center mx-auto mb-4">
            <span className="text-white text-lg font-bold">N</span>
          </div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  // Handle OAuth callback - process session_id BEFORE checking auth
  if (isAuthCallback) {
    return (
      <AuthCallback 
        onAuthSuccess={handleLoginSuccess}
        onAuthError={handleAuthError}
      />
    );
  }

  // Show login screen if not authenticated
  if (!authState.isAuthenticated) {
    return <LoginScreen onLoginSuccess={handleLoginSuccess} />;
  }

  // NIRO Simplified V1.5: Skip birth details onboarding, go directly to app
  // Only require login (phone/email), then proceed to simplified experience
  if (useSimplified) {
    return (
      <ChatProvider>
        <div className="App min-h-screen bg-gray-50 flex flex-col lg:items-center lg:justify-center lg:p-4">
          {/* UI Version Toggle (for development) */}
          <div className="fixed top-2 right-2 z-50 flex gap-1">
            <button 
              onClick={() => { setUseV5Flow(true); }}
              className={`text-white text-xs px-2 py-1 rounded-full shadow-lg ${useV5Flow ? 'bg-teal-600' : 'bg-slate-400'}`}
            >
              V5
            </button>
            <button 
              onClick={() => { setUseV5Flow(false); }}
              className={`text-white text-xs px-2 py-1 rounded-full shadow-lg ${!useV5Flow ? 'bg-amber-500' : 'bg-slate-400'}`}
            >
              V4
            </button>
            <button 
              onClick={() => { setUseSimplified(false); setUseV2UI(true); }}
              className={`text-white text-xs px-2 py-1 rounded-full shadow-lg ${useV2UI && !useSimplified ? 'bg-blue-600' : 'bg-slate-400'}`}
            >
              V2
            </button>
            <button 
              onClick={() => { setUseSimplified(false); setUseV2UI(false); }}
              className={`text-white text-xs px-2 py-1 rounded-full shadow-lg ${!useV2UI && !useSimplified ? 'bg-purple-600' : 'bg-slate-400'}`}
            >
              Old
            </button>
          </div>
          
          {/* Desktop: centered container with max width - overflow-auto for scrolling */}
          <div className="w-full lg:max-w-md lg:h-[85vh] lg:max-h-[900px] lg:rounded-2xl lg:shadow-xl lg:overflow-auto flex-1 flex flex-col">
            {useV5Flow ? (
              <SimplifiedAppV5 
                token={authState.token} 
                userId={authState.userId}
              />
            ) : (
              <SimplifiedApp 
                token={authState.token} 
                userId={authState.userId}
              />
            )}
          </div>
        </div>
      </ChatProvider>
    );
  }

  // Show onboarding if profile incomplete (for V2 and legacy modes only)
  if (!authState.profileComplete) {
    return (
      <OnboardingScreen token={authState.token} onComplete={handleOnboardingComplete} />
    );
  }

  // Authenticated and profile complete - show main app
  const renderScreen = () => {
    // NIRO V2: Use new UI if enabled
    if (useV2UI) {
      return (
        <NiroV2App 
          token={authState.token} 
          userId={authState.userId}
          existingChat={() => setActiveScreen('chat')}
        />
      );
    }
    
    // Legacy UI
    switch (activeScreen) {
      case 'home':
        return <HomeScreen onNavigate={setActiveScreen} />;
      case 'chat':
        return <ChatScreen token={authState.token} userId={authState.userId} />;
      case 'kundli':
        return <KundliScreen token={authState.token} userId={authState.userId} />;
      case 'horoscope':
        return <HoroscopeScreen />;
      case 'panchang':
        return <PanchangScreen />;
      case 'signals':
        return <CandidateSignalsScreen 
          userId={authState.userId}
        />;
      default:
        return <HomeScreen onNavigate={setActiveScreen} />;
    }
  };

  return (
    <ChatProvider>
      <div className="App min-h-screen bg-gray-50 flex flex-col lg:items-center lg:justify-center lg:p-4">
        {/* UI Version Toggle (for development) */}
        <div className="fixed top-2 right-2 z-50 flex gap-1">
          <button 
            onClick={() => { setUseSimplified(true); setUseV2UI(false); }}
            className={`text-white text-xs px-2 py-1 rounded-full shadow-lg ${useSimplified ? 'bg-emerald-600' : 'bg-slate-400'}`}
          >
            V1
          </button>
          <button 
            onClick={() => { setUseSimplified(false); setUseV2UI(true); }}
            className={`text-white text-xs px-2 py-1 rounded-full shadow-lg ${useV2UI && !useSimplified ? 'bg-blue-600' : 'bg-slate-400'}`}
          >
            V2
          </button>
          <button 
            onClick={() => { setUseSimplified(false); setUseV2UI(false); }}
            className={`text-white text-xs px-2 py-1 rounded-full shadow-lg ${!useV2UI && !useSimplified ? 'bg-purple-600' : 'bg-slate-400'}`}
          >
            Old
          </button>
        </div>
        
        {/* Desktop: centered container with max width */}
        <div className="w-full h-screen lg:h-auto lg:max-w-[840px] lg:rounded-lg lg:shadow-xl lg:bg-white flex flex-col lg:min-h-screen">
          <div className="flex-1 flex flex-col overflow-hidden">
            {/* Add padding-bottom for fixed bottom nav on mobile */}
            <div className="flex-1 overflow-y-auto pb-20 lg:pb-0">
              {renderScreen()}
            </div>
            {!useV2UI && !useSimplified && (
              <BottomNav activeScreen={activeScreen} onNavigate={setActiveScreen} onLogout={handleLogout} />
            )}
          </div>
        </div>
      </div>
    </ChatProvider>
  );
}

export default App;
