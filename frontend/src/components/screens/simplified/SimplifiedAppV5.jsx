/**
 * NIRO V5 Simplified App
 * Main app container with new 8-step onboarding flow
 * 
 * Flow: Splash -> Birth Details -> Pick Topic -> Pick Sub-topic -> Trust -> Choose Pack -> Checkout -> Home
 * 
 * Post-purchase: Home with horizontal topic rows -> Landing Pages
 */

import React, { useState, useEffect, useCallback } from 'react';
import { colors } from './theme';

// V5 Screens
import {
  SplashScreenV5,
  BirthDetailsScreenV5,
  TopicSelectionScreen,
  SubtopicSelectionScreen,
  TrustScreenV5,
  PackSelectionScreen,
  CheckoutScreenV5,
  HomeScreenV5,
  LandingPageV5,
  useOnboardingState,
  ONBOARDING_STEPS
} from './v5Screens';

// Keep existing bottom nav and other screens for post-purchase navigation
import BottomNav from './BottomNav';
import ExpertsScreen from './ExpertsScreen';
import ExpertProfileScreen from './ExpertProfileScreen';
import AskMiraScreen from './AskMiraScreen';
import ProfileScreen from './ProfileScreen';
import KundliScreenSimplified from './KundliScreenSimplified';
import RemediesScreen from './RemediesScreen';
import DevToggle from './DevToggle';
import { apiSimplified, trackEvent } from './utils';

// State keys
const USER_MODE_KEY = 'niro_user_mode';
const V5_ONBOARDING_KEY = 'niro_v5_onboarding_state';

/**
 * SimplifiedAppV5 - Main app with V5 8-step onboarding flow
 */
export default function SimplifiedAppV5({ token, userId }) {
  // V5 Onboarding state hook
  const onboarding = useOnboardingState();
  
  // App navigation state (post-onboarding)
  const [activeTab, setActiveTab] = useState('home');
  const [screen, setScreen] = useState('home');
  const [screenParams, setScreenParams] = useState({});
  const [userState, setUserState] = useState(null);
  const [loadingState, setLoadingState] = useState(true);
  const [miraInitialMessage, setMiraInitialMessage] = useState('');
  
  // Dev mode
  const [userMode, setUserMode] = useState(() => localStorage.getItem(USER_MODE_KEY) || 'NEW');

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

  // Initialize app
  useEffect(() => {
    const init = async () => {
      await loadUserState();
      trackEvent('app_init', { 
        flow_version: 'v5',
        onboarding_step: onboarding.currentStep
      }, token);
      setLoadingState(false);
    };
    init();
  }, [loadUserState, token, onboarding.currentStep]);

  // Get user display name
  const getUserName = () => {
    return onboarding.birthDetails?.name || userState?.name || 'User';
  };

  // ==========================================
  // ONBOARDING HANDLERS
  // ==========================================
  
  const handleSplashComplete = () => {
    trackEvent('v5_splash_complete', {}, token);
    onboarding.goToStep(ONBOARDING_STEPS.BIRTH_DETAILS);
  };

  const handleBirthDetailsComplete = (details) => {
    trackEvent('v5_birth_details_complete', { 
      has_time: !!details.timeOfBirth,
      skipped_time: details.skipBirthTime 
    }, token);
    onboarding.setBirthDetails(details);
    onboarding.goToStep(ONBOARDING_STEPS.PICK_TOPIC);
  };

  const handleTopicSelected = (topicId) => {
    onboarding.selectTopic(topicId);
  };

  const handleTopicContinue = () => {
    if (onboarding.selectedTopic) {
      trackEvent('v5_topic_selected', { topic: onboarding.selectedTopic }, token);
      onboarding.goToStep(ONBOARDING_STEPS.PICK_SUBTOPIC);
    }
  };

  const handleSubtopicSelected = (subtopicSlug) => {
    onboarding.selectSubtopic(subtopicSlug);
  };

  const handleSubtopicContinue = () => {
    if (onboarding.selectedSubtopic) {
      trackEvent('v5_subtopic_selected', { subtopic: onboarding.selectedSubtopic }, token);
      onboarding.goToStep(ONBOARDING_STEPS.TRUST);
    }
  };

  const handleTrustContinue = () => {
    trackEvent('v5_trust_acknowledged', {}, token);
    onboarding.acknowledgeTrust();
    onboarding.goToStep(ONBOARDING_STEPS.CHOOSE_PACK);
  };

  const handleTierSelected = (tierName) => {
    onboarding.selectTier(tierName);
  };

  const handlePackContinue = () => {
    if (onboarding.selectedTier) {
      trackEvent('v5_pack_selected', { 
        tier: onboarding.selectedTier,
        subtopic: onboarding.selectedSubtopic 
      }, token);
      onboarding.goToStep(ONBOARDING_STEPS.CHECKOUT);
    }
  };

  const handlePaymentSuccess = (paymentData) => {
    trackEvent('v5_payment_success', { 
      subtopic: paymentData.subtopicSlug,
      tier: paymentData.tierName 
    }, token);
    onboarding.completeCheckout();
    onboarding.goToStep(ONBOARDING_STEPS.HOME);
  };

  // ==========================================
  // POST-ONBOARDING NAVIGATION
  // ==========================================
  
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

  const navigate = (newScreen, params = {}) => {
    setScreen(newScreen);
    setScreenParams(params);
    
    if (newScreen === 'mira' && params.initialMessage) {
      setMiraInitialMessage(params.initialMessage);
      setActiveTab('mira');
    }
  };

  const goBack = () => {
    switch (screen) {
      case 'landing':
        setScreen('home');
        setActiveTab('home');
        break;
      case 'expertProfile':
        setScreen('experts');
        setActiveTab('consult');
        break;
      case 'profile':
        setScreen('home');
        setActiveTab('home');
        break;
      default:
        setScreen('home');
        setActiveTab('home');
    }
    setScreenParams({});
  };

  const handleSelectSubtopicFromHome = (subtopicSlug) => {
    trackEvent('home_subtopic_clicked', { subtopic: subtopicSlug }, token);
    setScreen('landing');
    setScreenParams({ subtopicSlug });
  };

  const handleLandingCheckout = (checkoutData) => {
    // Update onboarding state with selection
    onboarding.selectSubtopic(checkoutData.subtopicSlug);
    onboarding.selectTier(checkoutData.tierName);
    
    // Navigate to checkout
    setScreen('checkout');
    setScreenParams(checkoutData);
  };

  // Dev mode handlers
  const handleModeChange = (mode) => {
    setUserMode(mode);
    localStorage.setItem(USER_MODE_KEY, mode);
    trackEvent('dev_mode_changed', { mode }, token);
  };

  const handleReset = () => {
    onboarding.resetState();
    localStorage.removeItem(V5_ONBOARDING_KEY);
    localStorage.removeItem(USER_MODE_KEY);
    setUserMode('NEW');
    window.location.reload();
  };

  // ==========================================
  // RENDER LOGIC
  // ==========================================
  
  // Loading state
  if (loadingState) {
    return (
      <div 
        className="min-h-screen flex items-center justify-center"
        style={{ background: colors.background.gradient }}
      >
        <div className="text-center">
          <h1 
            className="text-3xl font-bold mb-2"
            style={{ color: colors.gold.primary }}
          >
            NIRO
          </h1>
          <p style={{ color: colors.text.muted }}>Loading...</p>
        </div>
      </div>
    );
  }

  // ==========================================
  // ONBOARDING FLOW (Steps 0-6)
  // ==========================================
  
  if (!onboarding.isOnboardingComplete) {
    const currentStep = onboarding.currentStep;
    
    // Step 0: Splash
    if (currentStep === ONBOARDING_STEPS.SPLASH) {
      return <SplashScreenV5 onComplete={handleSplashComplete} />;
    }
    
    // Step 1: Birth Details
    if (currentStep === ONBOARDING_STEPS.BIRTH_DETAILS) {
      return (
        <BirthDetailsScreenV5 
          initialData={onboarding.birthDetails}
          onComplete={handleBirthDetailsComplete}
          onBack={() => onboarding.goToStep(ONBOARDING_STEPS.SPLASH)}
        />
      );
    }
    
    // Step 2: Pick Topic
    if (currentStep === ONBOARDING_STEPS.PICK_TOPIC) {
      return (
        <TopicSelectionScreen 
          selectedTopic={onboarding.selectedTopic}
          onSelectTopic={handleTopicSelected}
          onContinue={handleTopicContinue}
          onBack={() => onboarding.goToStep(ONBOARDING_STEPS.BIRTH_DETAILS)}
        />
      );
    }
    
    // Step 3: Pick Sub-topic
    if (currentStep === ONBOARDING_STEPS.PICK_SUBTOPIC) {
      return (
        <SubtopicSelectionScreen 
          selectedTopic={onboarding.selectedTopic}
          selectedSubtopic={onboarding.selectedSubtopic}
          onSelectSubtopic={handleSubtopicSelected}
          onContinue={handleSubtopicContinue}
          onBack={() => onboarding.goToStep(ONBOARDING_STEPS.PICK_TOPIC)}
        />
      );
    }
    
    // Step 4: Trust Screen
    if (currentStep === ONBOARDING_STEPS.TRUST) {
      return (
        <TrustScreenV5 
          onContinue={handleTrustContinue}
          onBack={() => onboarding.goToStep(ONBOARDING_STEPS.PICK_SUBTOPIC)}
        />
      );
    }
    
    // Step 5: Choose Pack
    if (currentStep === ONBOARDING_STEPS.CHOOSE_PACK) {
      return (
        <PackSelectionScreen 
          selectedSubtopic={onboarding.selectedSubtopic}
          selectedTier={onboarding.selectedTier}
          onSelectTier={handleTierSelected}
          onContinue={handlePackContinue}
          onBack={() => onboarding.goToStep(ONBOARDING_STEPS.TRUST)}
        />
      );
    }
    
    // Step 6: Checkout
    if (currentStep === ONBOARDING_STEPS.CHECKOUT) {
      return (
        <CheckoutScreenV5 
          subtopicSlug={onboarding.selectedSubtopic}
          tierName={onboarding.selectedTier}
          birthDetails={onboarding.birthDetails}
          onPaymentSuccess={handlePaymentSuccess}
          onBack={() => onboarding.goToStep(ONBOARDING_STEPS.CHOOSE_PACK)}
        />
      );
    }
  }

  // ==========================================
  // POST-ONBOARDING SCREENS (Step 7 = HOME)
  // ==========================================
  
  const showBottomNav = !['checkout', 'profile'].includes(screen);

  const renderPostOnboardingScreen = () => {
    // Landing page for a specific subtopic
    if (screen === 'landing') {
      return (
        <LandingPageV5 
          slug={screenParams.subtopicSlug}
          onCheckout={handleLandingCheckout}
          onBack={goBack}
          initialTier="Supported"
        />
      );
    }
    
    // Checkout from landing page
    if (screen === 'checkout') {
      return (
        <CheckoutScreenV5 
          subtopicSlug={screenParams.subtopicSlug}
          tierName={screenParams.tierName}
          birthDetails={onboarding.birthDetails}
          onPaymentSuccess={(data) => {
            trackEvent('landing_payment_success', data, token);
            setScreen('home');
            setActiveTab('home');
          }}
          onBack={goBack}
        />
      );
    }
    
    // Profile screen
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
    
    // Expert profile
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

    // Tab-based screens
    switch (activeTab) {
      case 'home':
        return (
          <HomeScreenV5 
            userName={getUserName()}
            onSelectSubtopic={handleSelectSubtopicFromHome}
            onNavigateToChat={() => {
              setActiveTab('mira');
              setScreen('mira');
            }}
          />
        );
      
      case 'consult':
        return (
          <ExpertsScreen 
            token={token}
            userState={userState}
            onNavigate={(dest, params) => {
              if (dest === 'expertProfile') {
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
            onNavigate={(dest, params) => navigate(dest, params)}
          />
        );
      
      case 'remedies':
        return (
          <RemediesScreen hasBottomNav={showBottomNav} />
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
      
      default:
        return (
          <HomeScreenV5 
            userName={getUserName()}
            onSelectSubtopic={handleSelectSubtopicFromHome}
            onNavigateToChat={() => setActiveTab('mira')}
          />
        );
    }
  };

  return (
    <div 
      className="simplified-app min-h-screen relative" 
      style={{ backgroundColor: colors.background.card }}
    >
      {/* DevToggle for testing */}
      <DevToggle 
        userMode={userMode}
        onModeChange={handleModeChange}
        onReset={handleReset}
      />

      {renderPostOnboardingScreen()}
      
      {/* Bottom Navigation (post-onboarding only) */}
      {showBottomNav && (
        <BottomNav 
          activeTab={activeTab}
          onTabChange={handleTabChange}
        />
      )}
    </div>
  );
}
