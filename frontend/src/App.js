import React, { useState, useEffect } from 'react';
import './App.css';
import LoginScreen from './components/screens/LoginScreen';
import OnboardingScreen from './components/screens/OnboardingScreen';
import HomeScreen from './components/screens/HomeScreen';
import ChatScreen from './components/screens/ChatScreen';
import KundliScreen from './components/screens/KundliScreen';
import HoroscopeScreen from './components/screens/HoroscopeScreen';
import PanchangScreen from './components/screens/PanchangScreen';
import CompatibilityScreen from './components/screens/CompatibilityScreen';
import ChecklistScreen from './components/screens/ChecklistScreen';
import CandidateSignalsScreen from './components/screens/CandidateSignalsScreen';
import BottomNav from './components/BottomNav';
import { ChatProvider } from './context/ChatContext';
import { getAuthToken, getCurrentUser, getUserProfile, clearAuthToken } from './utils/auth';
import { BACKEND_URL } from './config';

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
  const [checklistRequestId, setChecklistRequestId] = useState(null);
  const [candidateSignalsUserId, setCandidateSignalsUserId] = useState(null);

  // Check auth status on mount
  useEffect(() => {
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

  const handleLoginSuccess = (token, userId) => {
    setAuthState((prev) => ({
      ...prev,
      isAuthenticated: true,
      token,
      userId,
    }));
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

  // Show login screen if not authenticated
  if (!authState.isAuthenticated) {
    return <LoginScreen onLoginSuccess={handleLoginSuccess} />;
  }

  // Show onboarding if profile incomplete
  if (!authState.profileComplete) {
    return (
      <OnboardingScreen token={authState.token} onComplete={handleOnboardingComplete} />
    );
  }

  // Authenticated and profile complete - show main app
  const renderScreen = () => {
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
      case 'compatibility':
        return <CompatibilityScreen 
          onViewChecklist={(requestId) => {
            setChecklistRequestId(requestId);
            setActiveScreen('checklist');
          }}
          onViewCandidateSignals={(userId) => {
            setCandidateSignalsUserId(userId);
            setActiveScreen('candidate-signals');
          }}
        />;
      case 'checklist':
        return <ChecklistScreen 
          requestId={checklistRequestId} 
          onBack={() => setActiveScreen('compatibility')} 
        />;
      case 'candidate-signals':
        return <CandidateSignalsScreen 
          userId={candidateSignalsUserId} 
          onBack={() => setActiveScreen('compatibility')} 
        />;
      default:
        return <HomeScreen onNavigate={setActiveScreen} />;
    }
  };

  return (
    <ChatProvider>
      <div className="App min-h-screen bg-gray-50 flex flex-col lg:items-center lg:justify-center lg:p-4">
        {/* Desktop: centered container with max width */}
        <div className="w-full h-screen lg:h-auto lg:max-w-[840px] lg:rounded-lg lg:shadow-xl lg:bg-white flex flex-col lg:min-h-screen">
          <div className="flex-1 flex flex-col overflow-hidden">
            <div className="flex-1 overflow-y-auto">
              {renderScreen()}
            </div>
            <BottomNav activeScreen={activeScreen} onNavigate={setActiveScreen} onLogout={handleLogout} />
          </div>
        </div>
      </div>
    </ChatProvider>
  );
}

export default App;
