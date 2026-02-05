import React, { useState, useEffect, useCallback } from 'react';
import HomeScreen from './HomeScreen';
import TopicLandingPage from './TopicLandingPage';
import CheckoutScreen from './CheckoutScreen';
import PlanDashboard from './PlanDashboard';
import ExpertsScreen from './ExpertsScreen';
import ExpertProfileScreen from './ExpertProfileScreen';
import AskMiraScreen from './AskMiraScreen';
import ProfileScreen from './ProfileScreen';
import KundliScreenSimplified from './KundliScreenSimplified';
import RemediesScreen from './RemediesScreen';
import BottomNav from './BottomNav';
import CategoryListingPage from './CategoryListingPage';
import DevToggle from './DevToggle';
import BirthDetailsModal from './BirthDetailsModal';
import { apiSimplified, trackEvent } from './utils';
import { colors } from './theme';
import { 
  HowNiroWorksScreen, 
  TrustSafetyScreen, 
  HomeTourOverlay 
} from './onboarding';

// State constants
const ONBOARDING_KEY = 'niro_onboarding_completed';
const HOME_TOUR_KEY = 'niro_home_tour_completed';
const USER_MODE_KEY = 'niro_user_mode';
const USER_DETAILS_KEY = 'niro_user_details_completed';

// Onboarding steps (Updated flow)
// Splash (login) → User Details (new users) → How It Works → Trust & Safety → Home
const ONBOARDING_STEPS = {
  USER_DETAILS: 'userDetails',
  HOW_IT_WORKS: 'howItWorks',
  TRUST_SAFETY: 'trustSafety',
  HOME: 'home'
};

/**
 * SimplifiedApp - Main app container for NIRO V6
 * 
 * Features:
 * - Guided Onboarding: User Details (new users) → How It Works → Trust & Safety → Home
 * - Home Tour Overlay (first time only)
 * - Bottom Navigation: Home, Consult, Mira, Remedies, Astro
 * - Profile button in top-right on HomeScreen
 * - DevToggle for testing (enabled via ?dev=true)
 * - CategoryListingPage for "View all" and "Talk to human" CTAs
 */
export default function SimplifiedApp({ token, userId }) {
  // Onboarding state - start from appropriate step based on saved state
  const [onboardingStep, setOnboardingStep] = useState(() => {
    const onboardingComplete = localStorage.getItem(ONBOARDING_KEY) === 'true';
    const userDetailsComplete = localStorage.getItem(USER_DETAILS_KEY) === 'true';
    
    if (onboardingComplete) return ONBOARDING_STEPS.HOME;
    if (userDetailsComplete) return ONBOARDING_STEPS.HOW_IT_WORKS;
    return ONBOARDING_STEPS.USER_DETAILS;
  });
  const [showHomeTour, setShowHomeTour] = useState(false);
  
  // App state
  const [activeTab, setActiveTab] = useState('home');
  const [screen, setScreen] = useState('home');
  const [screenParams, setScreenParams] = useState({});
  const [userState, setUserState] = useState(null);
  const [loadingState, setLoadingState] = useState(true);
  const [miraInitialMessage, setMiraInitialMessage] = useState('');
  const [showProfileModal, setShowProfileModal] = useState(false);
  
  // Dev mode state
  const [userMode, setUserMode] = useState(() => localStorage.getItem(USER_MODE_KEY) || 'NEW');

  // Check if onboarding is complete
  const isOnboardingComplete = localStorage.getItem(ONBOARDING_KEY) === 'true';
  const isHomeTourComplete = localStorage.getItem(HOME_TOUR_KEY) === 'true';
  const isUserDetailsComplete = localStorage.getItem(USER_DETAILS_KEY) === 'true';

  // Load user state
  const loadUserState = useCallback(async () => {
    try {
      const response = await apiSimplified.get('/user/state', token);
      setUserState(response.user_state);
      return response.user_state;
    } catch (err) {
      console.error('Failed to load user state:', err);
      setUserState({ is_new_user: true });
      return { is_new_user: true };
    }
  }, [token]);

  useEffect(() => {
    const init = async () => {
      const state = await loadUserState();
      trackEvent('app_init', { 
        onboarding_complete: isOnboardingComplete,
        flow_version: 'v6' 
      }, token);
      setLoadingState(false);
      
      // For returning users, skip user details
      if (state && !state.is_new_user && !isUserDetailsComplete) {
        localStorage.setItem(USER_DETAILS_KEY, 'true');
      }
    };
    init();
  }, [loadUserState, token, isOnboardingComplete, isUserDetailsComplete]);

  // Handle user details complete
  const handleUserDetailsComplete = () => {
    localStorage.setItem(USER_DETAILS_KEY, 'true');
    trackEvent('user_details_complete', {}, token);
    setOnboardingStep(ONBOARDING_STEPS.HOW_IT_WORKS);
    // Reload user state to get updated Kundli
    loadUserState();
  };

  // Handle onboarding navigation
  const handleOnboardingNext = (currentStep) => {
    switch (currentStep) {
      case ONBOARDING_STEPS.USER_DETAILS:
        handleUserDetailsComplete();
        break;
      case ONBOARDING_STEPS.HOW_IT_WORKS:
        trackEvent('onboarding_how_works_complete', {}, token);
        setOnboardingStep(ONBOARDING_STEPS.TRUST_SAFETY);
        break;
      case ONBOARDING_STEPS.TRUST_SAFETY:
        trackEvent('onboarding_trust_complete', {}, token);
        localStorage.setItem(ONBOARDING_KEY, 'true');
        setOnboardingStep(ONBOARDING_STEPS.HOME);
        if (!isHomeTourComplete) {
          setTimeout(() => setShowHomeTour(true), 500);
        }
        break;
      default:
        break;
    }
  };

  // Handle home tour complete
  const handleHomeTourComplete = () => {
    localStorage.setItem(HOME_TOUR_KEY, 'true');
    setShowHomeTour(false);
    trackEvent('home_tour_complete', {}, token);
  };

  // Handle user mode change (DevToggle)
  const handleModeChange = (mode) => {
    setUserMode(mode);
    localStorage.setItem(USER_MODE_KEY, mode);
    trackEvent('dev_mode_changed', { mode }, token);
  };

  // Handle reset (DevToggle)
  const handleReset = () => {
    localStorage.removeItem(ONBOARDING_KEY);
    localStorage.removeItem(HOME_TOUR_KEY);
    localStorage.removeItem(USER_MODE_KEY);
    localStorage.removeItem(USER_DETAILS_KEY);
    setOnboardingStep(ONBOARDING_STEPS.USER_DETAILS);
    setUserMode('NEW');
    window.location.reload();
  };

  // Tab change handler - Updated for new navigation
  const handleTabChange = (tabId) => {
    trackEvent('nav_tab_clicked', { tab_name: tabId }, token);
    
    setActiveTab(tabId);
    setMiraInitialMessage('');
    
    switch (tabId) {
      case 'home':
        setScreen('home');
        break;
      case 'consult':
        setScreen('experts');
        break;
      case 'mira':
        setScreen('mira');
        break;
      case 'remedies':
        setScreen('remedies');
        break;
      case 'astro':
        setScreen('kundli');
        break;
      default:
        setScreen('home');
    }
    setScreenParams({});
  };

  // Navigate to specific screen
  const navigate = (newScreen, params = {}) => {
    setScreen(newScreen);
    setScreenParams(params);
    
    if (newScreen === 'mira' && params.initialMessage) {
      setMiraInitialMessage(params.initialMessage);
      setActiveTab('mira');
    }
  };

  // Handle Chat with Mira CTA
  const handleChatWithMira = () => {
    trackEvent('cta_chat_with_mira', {}, token);
    setActiveTab('mira');
    setScreen('mira');
    setMiraInitialMessage('');
  };

  // Handle Talk to Human CTA
  const handleTalkToHuman = () => {
    trackEvent('cta_talk_to_human', {}, token);
    setScreen('categoryListing');
    setScreenParams({ showAllCategories: true, title: 'Talk to a Human Astrologer' });
  };

  // Go back handler
  const goBack = () => {
    switch (screen) {
      case 'topic':
        setScreen('home');
        setActiveTab('home');
        break;
      case 'checkout':
        setScreen('topic');
        break;
      case 'plan':
        setScreen('home');
        setActiveTab('home');
        break;
      case 'expertProfile':
        if (screenParams.fromTopic) {
          setScreen('topic');
        } else {
          setScreen('experts');
          setActiveTab('consult');
        }
        break;
      case 'categoryListing':
        setScreen('home');
        setActiveTab('home');
        break;
      default:
        setScreen('home');
        setActiveTab('home');
    }
    setScreenParams({});
  };

  // Checkout handler
  const handleCheckout = (tierId, scenarioIds = []) => {
    navigate('checkout', { tierId, scenarioIds });
  };

  // Purchase success handler
  const handlePurchaseSuccess = async (planId) => {
    await loadUserState();
    navigate('plan', { planId });
  };

  // Get user display name
  const getUserName = () => {
    return userState?.name || userState?.email?.split('@')[0] || 'there';
  };

  // Loading state - show simple loading instead of splash
  if (loadingState) {
    return (
      <div 
        className="min-h-screen flex items-center justify-center"
        style={{ background: colors.background.gradient }}
      >
        <div className="text-center">
          <div 
            className="w-12 h-12 border-4 rounded-full animate-spin mx-auto mb-4"
            style={{ borderColor: 'rgba(255,255,255,0.3)', borderTopColor: '#ffffff' }}
          />
          <p style={{ color: 'rgba(255,255,255,0.8)' }}>Loading...</p>
        </div>
      </div>
    );
  }

  // Render onboarding screens (Updated flow: User Details → How It Works → Trust & Safety)
  if (onboardingStep === ONBOARDING_STEPS.USER_DETAILS) {
    // Use BirthDetailsModal in full-screen mode during onboarding
    return (
      <BirthDetailsModal 
        token={token} 
        isOpen={true} 
        onClose={() => {}} // No close during onboarding 
        onComplete={handleUserDetailsComplete}
        isOnboarding={true} // Hide cancel button during onboarding
      />
    );
  }

  if (onboardingStep === ONBOARDING_STEPS.HOW_IT_WORKS) {
    return <HowNiroWorksScreen onNext={() => handleOnboardingNext(ONBOARDING_STEPS.HOW_IT_WORKS)} onBack={() => setOnboardingStep(ONBOARDING_STEPS.USER_DETAILS)} />;
  }

  if (onboardingStep === ONBOARDING_STEPS.TRUST_SAFETY) {
    return <TrustSafetyScreen onComplete={() => handleOnboardingNext(ONBOARDING_STEPS.TRUST_SAFETY)} onBack={() => setOnboardingStep(ONBOARDING_STEPS.HOW_IT_WORKS)} />;
  }

  // Determine if bottom nav should be shown
  const showBottomNav = !['checkout', 'profile', 'categoryListing'].includes(screen);

  // Render current screen
  const renderScreen = () => {
    // Sub-screens that override tabs
    if (screen === 'topic') {
      return (
        <TopicLandingPage 
          token={token}
          topicId={screenParams.topicId}
          onCheckout={handleCheckout}
          onBack={goBack}
          onNavigate={navigate}
          hasBottomNav={showBottomNav}
          userName={getUserName()}
        />
      );
    }
    
    if (screen === 'checkout') {
      return (
        <CheckoutScreen 
          token={token}
          tierId={screenParams.tierId}
          scenarioIds={screenParams.scenarioIds}
          onSuccess={handlePurchaseSuccess}
          onBack={goBack}
        />
      );
    }
    
    if (screen === 'plan') {
      return (
        <PlanDashboard 
          token={token}
          planId={screenParams.planId}
          onNavigate={navigate}
          onBack={goBack}
          hasBottomNav={showBottomNav}
        />
      );
    }
    
    if (screen === 'expertProfile') {
      return (
        <ExpertProfileScreen
          token={token}
          expertId={screenParams.expertId}
          userState={userState}
          onNavigate={navigate}
          onBack={goBack}
          hasBottomNav={showBottomNav}
        />
      );
    }

    if (screen === 'profile') {
      return (
        <ProfileScreen
          token={token}
          userId={userId}
          onBack={() => {
            setScreen('home');
            setActiveTab('home');
          }}
          hasBottomNav={false}
        />
      );
    }

    if (screen === 'categoryListing') {
      return (
        <CategoryListingPage
          categoryId={screenParams.categoryId}
          showAllCategories={screenParams.showAllCategories}
          title={screenParams.title || 'Browse Topics'}
          onBack={goBack}
          onTileClick={(tileId) => {
            trackEvent('tile_clicked_from_listing', { tile_id: tileId }, token);
            navigate('topic', { topicId: tileId });
          }}
        />
      );
    }

    // Tab-based screens
    switch (activeTab) {
      case 'home':
        return (
          <HomeScreen 
            token={token}
            userId={userId}
            userState={userState}
            userName={getUserName()}
            hasBottomNav={showBottomNav}
            onChatWithMira={handleChatWithMira}
            onTalkToHuman={handleTalkToHuman}
            onNavigate={(dest, params) => {
              if (dest === 'mira') {
                navigate('mira', params);
                setActiveTab('mira');
              } else if (dest === 'topic') {
                navigate('topic', params);
              } else if (dest === 'categoryListing') {
                navigate('categoryListing', params);
              } else {
                navigate(dest, params);
              }
            }}
            onOpenProfile={() => {
              setScreen('profile');
            }}
          />
        );
      
      case 'consult':
        return (
          <ExpertsScreen 
            token={token}
            userState={userState}
            onNavigate={(dest, params) => {
              if (dest === 'topic') {
                navigate('topic', params);
              } else if (dest === 'expertProfile') {
                navigate('expertProfile', params);
              } else {
                navigate(dest, params);
              }
            }}
          />
        );
      
      case 'mira':
        return (
          <AskMiraScreen 
            token={token}
            initialMessage={miraInitialMessage}
            onNavigate={(dest, params) => {
              if (dest === 'topic') {
                navigate('topic', params);
              } else {
                navigate(dest, params);
              }
            }}
          />
        );
      
      case 'remedies':
        return (
          <RemediesScreen
            hasBottomNav={showBottomNav}
          />
        );
      
      case 'astro':
        return (
          <KundliScreenSimplified
            token={token}
            userId={userId}
            hasBottomNav={showBottomNav}
            onNavigate={(dest, params) => {
              if (dest === 'profile') {
                setScreen('profile');
              } else {
                navigate(dest, params);
              }
            }}
          />
        );
      
      case 'mypack':
        // Show the user's active plan dashboard
        const activePlan = userState?.active_plans?.[0];
        if (activePlan) {
          return (
            <PlanDashboard 
              token={token}
              planId={activePlan.plan_id}
              onNavigate={navigate}
              onBack={() => {
                setActiveTab('home');
                setScreen('home');
              }}
              hasBottomNav={showBottomNav}
            />
          );
        }
        // Fallback to home if no active plan
        return (
          <HomeScreen 
            token={token}
            userId={userId}
            userState={userState}
            userName={getUserName()}
            hasBottomNav={showBottomNav}
            onChatWithMira={handleChatWithMira}
            onTalkToHuman={handleTalkToHuman}
            onNavigate={(dest, params) => navigate(dest, params)}
            onOpenProfile={() => setScreen('profile')}
          />
        );
      
      default:
        return (
          <HomeScreen 
            token={token}
            userId={userId}
            userState={userState}
            userName={getUserName()}
            hasBottomNav={showBottomNav}
            onChatWithMira={handleChatWithMira}
            onTalkToHuman={handleTalkToHuman}
            onNavigate={(dest, params) => navigate(dest, params)}
            onOpenProfile={() => setScreen('profile')}
          />
        );
    }
  };

  return (
    <div 
      className="simplified-app min-h-screen relative" 
      style={{ backgroundColor: colors.background.primary }}
    >
      {/* DevToggle */}
      <DevToggle 
        userMode={userMode}
        onModeChange={handleModeChange}
        onReset={handleReset}
      />

      {renderScreen()}
      
      {/* Bottom Navigation */}
      {showBottomNav && (
        <BottomNav 
          activeTab={activeTab}
          onTabChange={handleTabChange}
          hasActivePlan={userState?.active_plans?.length > 0}
        />
      )}

      {/* Home Tour Overlay */}
      {showHomeTour && (
        <HomeTourOverlay 
          onComplete={handleHomeTourComplete}
          onSkip={handleHomeTourComplete}
        />
      )}
    </div>
  );
}
