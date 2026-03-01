import React, { useState, useEffect, useCallback } from 'react';
import HomeScreen from './HomeScreen';
import TopicLandingPage from './TopicLandingPage';
import PackageLandingPage from './PackageLandingPage';
import CheckoutScreen from './CheckoutScreen';
import PlanDashboard from './PlanDashboard';
import MyPackScreen from './MyPackScreen';
import ExpertsScreen from './ExpertsScreen';
import ExpertProfileScreen from './ExpertProfileScreen';
import AskMiraScreen from './AskMiraScreen';
import ProfileScreen from './ProfileScreen';
import KundliScreenSimplified from './KundliScreenSimplified';
import RemediesScreen from './RemediesScreen';
import BottomNav from './BottomNav';
import CategoryListingPage from './CategoryListingPage';
import BirthDetailsModal from './BirthDetailsModal';
import ScheduleCallScreen from './ScheduleCallScreen';
import { apiSimplified, trackEvent } from './utils';
import { colors } from './theme';
import { clearUserIntent } from './PublicLandingPage';
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
 * SimplifiedApp - Main app container for NIRO V10
 * 
 * Features:
 * - Intent-based routing from PublicLandingPage
 * - Guided Onboarding: User Details (new users) → How It Works → Trust & Safety → Home
 * - Home Tour Overlay (first time only)
 * - Bottom Navigation: Home, Consult, Remedies, My Pack, Astro
 * - Profile button in top-right on HomeScreen
 * - Schedule Call screen with Google Calendar integration
 * 
 * User Types:
 * - New User: No birth details → Goes through full onboarding
 * - Returning User: Has birth details → Skips birth details screen
 * - Paying Customer: Has active packs → Shows My Pack tab
 * 
 * Intent Flows:
 * - free_call: New → Birth Details → Schedule | Returning → Schedule
 * - consultation:{topic}: New → Birth Details → Topics → Packages | Returning → Topics/MyPack
 */
export default function SimplifiedApp({ 
  token, 
  userId, 
  user,
  initialIntent = null,
  initialScreen = null,
  initialParams = null,
  onBackToLanding = null,
  onLogout = null,
}) {
  // Track if we have a pending intent to process after onboarding
  const [pendingIntent, setPendingIntent] = useState(initialIntent);
  
  // Onboarding state - start from appropriate step based on saved state AND user profile
  const [onboardingStep, setOnboardingStep] = useState(() => {
    const onboardingComplete = localStorage.getItem(ONBOARDING_KEY) === 'true';
    const userDetailsComplete = localStorage.getItem(USER_DETAILS_KEY) === 'true';
    
    // If user has profile_complete from server, they're a returning user
    const isReturningUser = user?.profile_complete || user?.dob;
    
    // If we have an intent, we need to check if we need birth details
    if (initialIntent && !isReturningUser && !userDetailsComplete) {
      return ONBOARDING_STEPS.USER_DETAILS;
    }
    
    if (onboardingComplete) return ONBOARDING_STEPS.HOME;
    if (userDetailsComplete || isReturningUser) {
      if (isReturningUser && !userDetailsComplete) {
        localStorage.setItem(USER_DETAILS_KEY, 'true');
      }
      return ONBOARDING_STEPS.HOW_IT_WORKS;
    }
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
        flow_version: 'v10',
        has_intent: !!initialIntent,
      }, token);
      setLoadingState(false);
      
      // For returning users (has profile or paid), skip user details
      const isReturningUser = user?.profile_complete || user?.dob;
      
      if ((state && !state.is_new_user) || isReturningUser) {
        if (!isUserDetailsComplete) {
          localStorage.setItem(USER_DETAILS_KEY, 'true');
          if (!isOnboardingComplete && isReturningUser) {
            localStorage.setItem(ONBOARDING_KEY, 'true');
            setOnboardingStep(ONBOARDING_STEPS.HOME);
          }
        }
        
        // Handle intent for returning users (they skip birth details)
        if (initialIntent && isReturningUser) {
          if (initialIntent.type === 'free_call') {
            setScreen('schedule');
            clearUserIntent();
            setPendingIntent(null);
          } else if (initialIntent.type === 'consultation' && initialIntent.topicId) {
            // Check if user has pack for this topic
            const hasPack = state?.active_plans?.some(plan => 
              plan.topic_id === initialIntent.topicId || plan.topics?.includes(initialIntent.topicId)
            );
            if (hasPack) {
              setScreen('mypack');
              setActiveTab('mypack');
            } else {
              setScreen('home');
              setActiveTab('home');
              setTimeout(() => {
                const topicsSection = document.getElementById('topics-section');
                if (topicsSection) {
                  topicsSection.scrollIntoView({ behavior: 'smooth' });
                }
              }, 500);
            }
            clearUserIntent();
            setPendingIntent(null);
          }
        }
      }
      
      // Handle initial screen override (for logged-in users navigating from landing)
      if (initialScreen && !initialIntent) {
        if (initialScreen === 'mypack') {
          setScreen('mypack');
          setActiveTab('mypack');
        } else if (initialScreen === 'astro') {
          setScreen('kundli');
          setActiveTab('astro');
        } else if (initialScreen === 'profile') {
          setScreen('profile');
        } else if (initialScreen === 'experts') {
          setScreen('experts');
          setActiveTab('consult');
        } else if (initialScreen === 'schedule') {
          setScreen('schedule');
        }
      }
    };
    init();
  }, [loadUserState, token, isOnboardingComplete, isUserDetailsComplete, user, initialIntent, initialScreen]);

  // Handle user details complete - route based on pending intent
  const handleUserDetailsComplete = () => {
    localStorage.setItem(USER_DETAILS_KEY, 'true');
    trackEvent('user_details_complete', {}, token);
    
    // If we have a pending intent, route accordingly
    if (pendingIntent) {
      if (pendingIntent.type === 'free_call') {
        // Go directly to schedule call screen
        setScreen('schedule');
        setOnboardingStep(ONBOARDING_STEPS.HOME);
        localStorage.setItem(ONBOARDING_KEY, 'true');
        clearUserIntent();
        setPendingIntent(null);
        return;
      } else if (pendingIntent.type === 'consultation' && pendingIntent.topicId) {
        // Go to home with topics visible (they can scroll to their topic)
        setScreen('home');
        setActiveTab('home');
        setOnboardingStep(ONBOARDING_STEPS.HOME);
        localStorage.setItem(ONBOARDING_KEY, 'true');
        clearUserIntent();
        setPendingIntent(null);
        // Scroll to topics section after a short delay
        setTimeout(() => {
          const topicsSection = document.getElementById('topics-section');
          if (topicsSection) {
            topicsSection.scrollIntoView({ behavior: 'smooth' });
          }
        }, 500);
        return;
      }
    }
    
    // Default: Continue with normal onboarding
    setOnboardingStep(ONBOARDING_STEPS.HOW_IT_WORKS);
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
      case 'mypack':
        setScreen('mypack');
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
    // 'topic' now goes to experts filtered by that topic — skip TopicLandingPage
    if (newScreen === 'topic') {
      setScreen('experts');
      setScreenParams({ topicId: params.topicId });
      return;
    }

    setScreen(newScreen);
    setScreenParams(params);

    if (newScreen === 'mira' && params.initialMessage) {
      setMiraInitialMessage(params.initialMessage);
    }
    if (newScreen === 'mira') {
      // Mira is no longer a nav tab — keep current tab highlighted
    }
  };

  // Handle Chat with Mira CTA (accessible from homepage, not bottom nav)
  const handleChatWithMira = () => {
    trackEvent('cta_chat_with_mira', {}, token);
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
        setScreenParams({});
        break;
      case 'packageLanding':
        setScreen('home');
        setActiveTab('home');
        setScreenParams({});
        break;
      case 'checkout':
        // Restore previous screen and its params
        if (screenParams._prevScreen && screenParams._prevParams) {
          setScreen(screenParams._prevScreen);
          setScreenParams(screenParams._prevParams);
        } else {
          setScreen('home');
          setActiveTab('home');
          setScreenParams({});
        }
        break;
      case 'plan':
        setScreen('home');
        setActiveTab('home');
        setScreenParams({});
        break;
      case 'expertProfile':
        if (screenParams.fromTopic) {
          setScreen('experts');
          setScreenParams({ topicId: screenParams.fromTopic });
        } else {
          setScreen('experts');
          setActiveTab('consult');
          setScreenParams({});
        }
        break;
      case 'experts':
        setScreen('home');
        setActiveTab('home');
        setScreenParams({});
        break;
      case 'categoryListing':
        setScreen('home');
        setActiveTab('home');
        setScreenParams({});
        break;
      default:
        setScreen('home');
        setActiveTab('home');
        setScreenParams({});
    }
  };

  // Checkout handler - preserve previous screen context for back navigation
  const handleCheckout = (tierId, scenarioIds = []) => {
    const prevScreen = screen;
    const prevParams = { ...screenParams };
    navigate('checkout', { tierId, scenarioIds, _prevScreen: prevScreen, _prevParams: prevParams });
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
  const showBottomNav = !['checkout', 'profile', 'categoryListing', 'schedule'].includes(screen);

  // Render current screen
  const renderScreen = () => {
    // Schedule Call screen (for free 10-min call flow)
    if (screen === 'schedule') {
      return (
        <ScheduleCallScreen
          onBack={() => {
            if (onBackToLanding) {
              onBackToLanding();
            } else {
              setScreen('home');
              setActiveTab('home');
            }
          }}
          onComplete={() => {
            setScreen('home');
            setActiveTab('home');
          }}
          userName={getUserName()}
        />
      );
    }
    
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
          onTabChange={handleTabChange}
        />
      );
    }
    
    // Package Landing Page (for standalone packages like Valentine's)
    if (screen === 'packageLanding') {
      return (
        <PackageLandingPage 
          token={token}
          packageId={screenParams.packageId}
          tileData={screenParams.tileData}
          onCheckout={handleCheckout}
          onBack={goBack}
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
          onTabChange={handleTabChange}
        />
      );
    }
    
    if (screen === 'plan' || screen === 'planDashboard') {
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
          wizardTopicId={screenParams.topicId || screenParams.fromTopic}
          userState={userState}
          onNavigate={navigate}
          onBack={goBack}
          hasBottomNav={showBottomNav}
          onTabChange={handleTabChange}
        />
      );
    }

    if (screen === 'profile') {
      return (
        <ProfileScreen
          token={token}
          userId={userId}
          onResetDemo={onResetDemo}
          hasBottomNav={false}
          onBack={() => {
            setScreen('home');
            setActiveTab('home');
          }}
          onNavigate={navigate}
          onTabChange={handleTabChange}
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

    // Experts screen — topic-filtered, navigated to from topic cards
    if (screen === 'experts') {
      return (
        <ExpertsScreen
          token={token}
          userState={userState}
          hasBottomNav={showBottomNav}
          topicId={screenParams.topicId}
          onNavigate={(dest, params) => {
            if (dest === 'expertProfile') {
              navigate('expertProfile', { ...params, fromTopic: screenParams.topicId });
            } else {
              navigate(dest, params);
            }
          }}
          onTabChange={handleTabChange}
          onBack={() => {
            setScreen('home');
            setActiveTab('home');
            setScreenParams({});
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
            onTabChange={handleTabChange}
          />
        );
      
      case 'consult':
        return (
          <ExpertsScreen 
            token={token}
            userState={userState}
            hasBottomNav={showBottomNav}
            onNavigate={(dest, params) => {
              if (dest === 'topic') {
                navigate('topic', params);
              } else if (dest === 'expertProfile') {
                navigate('expertProfile', params);
              } else {
                navigate(dest, params);
              }
            }}
            onTabChange={handleTabChange}
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
            onTabChange={handleTabChange}
            onNavigate={navigate}
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
            onTabChange={handleTabChange}
          />
        );
      
      case 'mypack':
        // Show the user's My Pack dashboard
        return (
          <MyPackScreen 
            token={token}
            userState={userState}
            onNavigate={navigate}
            hasBottomNav={showBottomNav}
            onTabChange={handleTabChange}
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
      {/* Main Content Container - Full width, responsive */}
      <div className="w-full max-w-7xl mx-auto">
        {renderScreen()}
      </div>
      
      {/* Bottom Navigation - Mobile only */}
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
