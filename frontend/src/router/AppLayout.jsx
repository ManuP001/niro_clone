import React, { useState, useEffect, useCallback } from 'react';
import { Routes, Route, useNavigate, useLocation, Navigate } from 'react-router-dom';
import { ChatProvider } from '../context/ChatContext';
import { colors } from '../components/screens/simplified/theme';
import { apiSimplified, trackEvent } from '../components/screens/simplified/utils';
import { clearUserIntent, getUserIntent } from '../components/screens/simplified/PublicLandingPage';

// Screens
import HomeScreen from '../components/screens/simplified/HomeScreen';
import TopicLandingPage from '../components/screens/simplified/TopicLandingPage';
import PackageLandingPage from '../components/screens/simplified/PackageLandingPage';
import CheckoutScreen from '../components/screens/simplified/CheckoutScreen';
import PlanDashboard from '../components/screens/simplified/PlanDashboard';
import MyPackScreen from '../components/screens/simplified/MyPackScreen';
import ExpertsScreen from '../components/screens/simplified/ExpertsScreen';
import ExpertProfileScreen from '../components/screens/simplified/ExpertProfileScreen';
import AskMiraScreen from '../components/screens/simplified/AskMiraScreen';
import ProfileScreen from '../components/screens/simplified/ProfileScreen';
import KundliScreenSimplified from '../components/screens/simplified/KundliScreenSimplified';
import RemediesScreen from '../components/screens/simplified/RemediesScreen';
import ScheduleCallScreen from '../components/screens/simplified/ScheduleCallScreen';
import CategoryListingPage from '../components/screens/simplified/CategoryListingPage';
import BottomNav from '../components/screens/simplified/BottomNav';
import BirthDetailsModal from '../components/screens/simplified/BirthDetailsModal';

// Onboarding
import { 
  HowNiroWorksScreen, 
  TrustSafetyScreen, 
  HomeTourOverlay 
} from '../components/screens/simplified/onboarding';

// State constants
const ONBOARDING_KEY = 'niro_onboarding_completed';
const HOME_TOUR_KEY = 'niro_home_tour_completed';
const USER_DETAILS_KEY = 'niro_user_details_completed';

// Onboarding steps
const ONBOARDING_STEPS = {
  USER_DETAILS: 'userDetails',
  HOW_IT_WORKS: 'howItWorks',
  TRUST_SAFETY: 'trustSafety',
  COMPLETE: 'complete'
};

/**
 * AppLayout - Main authenticated app layout with React Router
 * 
 * Handles:
 * - Onboarding flow for new users
 * - Intent-based routing from landing page
 * - Bottom navigation
 * - User state management
 */
export default function AppLayout({ authState, onLogout }) {
  const navigate = useNavigate();
  const location = useLocation();
  const { token, userId, user } = authState;

  // User state
  const [userState, setUserState] = useState(null);
  const [loadingState, setLoadingState] = useState(true);
  const [miraInitialMessage, setMiraInitialMessage] = useState('');
  const [showHomeTour, setShowHomeTour] = useState(false);

  // Onboarding state
  const [onboardingStep, setOnboardingStep] = useState(() => {
    const onboardingComplete = localStorage.getItem(ONBOARDING_KEY) === 'true';
    const userDetailsComplete = localStorage.getItem(USER_DETAILS_KEY) === 'true';
    const isReturningUser = user?.profile_complete || user?.dob;

    if (onboardingComplete) return ONBOARDING_STEPS.COMPLETE;
    if (userDetailsComplete || isReturningUser) {
      if (isReturningUser && !userDetailsComplete) {
        localStorage.setItem(USER_DETAILS_KEY, 'true');
      }
      return ONBOARDING_STEPS.HOW_IT_WORKS;
    }
    return ONBOARDING_STEPS.USER_DETAILS;
  });

  // Track current tab for bottom nav
  const [activeTab, setActiveTab] = useState(() => {
    const path = location.pathname;
    if (path.includes('/experts') || path.includes('/expert/')) return 'consult';
    if (path.includes('/mira')) return 'mira';
    if (path.includes('/remedies')) return 'remedies';
    if (path.includes('/mypack')) return 'mypack';
    if (path.includes('/astro')) return 'astro';
    return 'home';
  });

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
      const state = await loadUserState();
      trackEvent('app_init', { 
        flow_version: 'v11_router',
        path: location.pathname,
      }, token);
      setLoadingState(false);

      const isReturningUser = user?.profile_complete || user?.dob;
      const isOnboardingComplete = localStorage.getItem(ONBOARDING_KEY) === 'true';
      const isUserDetailsComplete = localStorage.getItem(USER_DETAILS_KEY) === 'true';

      // Handle returning users
      if ((state && !state.is_new_user) || isReturningUser) {
        if (!isUserDetailsComplete) {
          localStorage.setItem(USER_DETAILS_KEY, 'true');
        }
        if (!isOnboardingComplete && isReturningUser) {
          localStorage.setItem(ONBOARDING_KEY, 'true');
          setOnboardingStep(ONBOARDING_STEPS.COMPLETE);
        }
      }

      // Handle stored intent
      const intent = getUserIntent();
      if (intent && isReturningUser) {
        if (intent.type === 'free_call') {
          navigate('/app/schedule', { replace: true });
          clearUserIntent();
        } else if (intent.type === 'consultation' && intent.topicId) {
          const hasPack = state?.active_plans?.some(plan => 
            plan.topic_id === intent.topicId || plan.topics?.includes(intent.topicId)
          );
          if (hasPack) {
            navigate('/app/mypack', { replace: true });
          } else {
            navigate('/app', { replace: true });
            setTimeout(() => {
              const topicsSection = document.getElementById('topics-section');
              if (topicsSection) {
                topicsSection.scrollIntoView({ behavior: 'smooth' });
              }
            }, 500);
          }
          clearUserIntent();
        }
      }
    };
    init();
  }, [loadUserState, token, user, location.pathname, navigate]);

  // Update active tab based on route
  useEffect(() => {
    const path = location.pathname;
    if (path === '/app' || path === '/app/') setActiveTab('home');
    else if (path.includes('/experts') || path.includes('/expert/')) setActiveTab('consult');
    else if (path.includes('/mira')) setActiveTab('mira');
    else if (path.includes('/remedies')) setActiveTab('remedies');
    else if (path.includes('/mypack')) setActiveTab('mypack');
    else if (path.includes('/astro')) setActiveTab('astro');
  }, [location.pathname]);

  // Handle user details complete
  const handleUserDetailsComplete = () => {
    localStorage.setItem(USER_DETAILS_KEY, 'true');
    trackEvent('user_details_complete', {}, token);

    const intent = getUserIntent();
    if (intent) {
      if (intent.type === 'free_call') {
        navigate('/app/schedule', { replace: true });
        localStorage.setItem(ONBOARDING_KEY, 'true');
        setOnboardingStep(ONBOARDING_STEPS.COMPLETE);
        clearUserIntent();
        return;
      } else if (intent.type === 'consultation' && intent.topicId) {
        navigate('/app', { replace: true });
        localStorage.setItem(ONBOARDING_KEY, 'true');
        setOnboardingStep(ONBOARDING_STEPS.COMPLETE);
        clearUserIntent();
        setTimeout(() => {
          const topicsSection = document.getElementById('topics-section');
          if (topicsSection) {
            topicsSection.scrollIntoView({ behavior: 'smooth' });
          }
        }, 500);
        return;
      }
    }

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
        setOnboardingStep(ONBOARDING_STEPS.COMPLETE);
        const isHomeTourComplete = localStorage.getItem(HOME_TOUR_KEY) === 'true';
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

  // Tab change handler with navigation
  const handleTabChange = (tabId) => {
    trackEvent('nav_tab_clicked', { tab_name: tabId }, token);
    setActiveTab(tabId);
    setMiraInitialMessage('');

    switch (tabId) {
      case 'home':
        navigate('/app');
        break;
      case 'consult':
        navigate('/app/experts');
        break;
      case 'mira':
        navigate('/app/mira');
        break;
      case 'remedies':
        navigate('/app/remedies');
        break;
      case 'mypack':
        navigate('/app/mypack');
        break;
      case 'astro':
        navigate('/app/astro');
        break;
      default:
        navigate('/app');
    }
  };

  // Navigate helper - converts old navigate calls to React Router
  const handleNavigate = (dest, params = {}) => {
    switch (dest) {
      case 'topic':
        navigate(`/app/topic/${params.topicId}`);
        break;
      case 'packageLanding':
        navigate(`/app/package/${params.packageId}`, { state: params });
        break;
      case 'checkout':
        navigate('/app/checkout', { state: params });
        break;
      case 'plan':
      case 'planDashboard':
        navigate(`/app/plan/${params.planId}`);
        break;
      case 'expertProfile':
        navigate(`/app/expert/${params.expertId}`, { state: params });
        break;
      case 'experts':
        navigate('/app/experts');
        break;
      case 'mira':
        if (params.initialMessage) {
          setMiraInitialMessage(params.initialMessage);
        }
        navigate('/app/mira');
        break;
      case 'profile':
        navigate('/app/profile');
        break;
      case 'categoryListing':
        navigate('/app/categories', { state: params });
        break;
      case 'schedule':
        navigate('/app/schedule');
        break;
      case 'home':
        navigate('/app');
        break;
      default:
        navigate('/app');
    }
  };

  // Handle checkout
  const handleCheckout = (tierId, scenarioIds = []) => {
    navigate('/app/checkout', { 
      state: { 
        tierId, 
        scenarioIds,
        _returnPath: location.pathname,
      } 
    });
  };

  // Handle purchase success
  const handlePurchaseSuccess = async (planId) => {
    await loadUserState();
    navigate(`/app/plan/${planId}`);
  };

  // Get user display name
  const getUserName = () => {
    return userState?.name || userState?.email?.split('@')[0] || 'there';
  };

  // Determine if bottom nav should be shown
  const hideBottomNavPaths = ['/app/checkout', '/app/profile', '/app/categories', '/app/schedule'];
  const showBottomNav = !hideBottomNavPaths.some(p => location.pathname.startsWith(p));

  // Loading state
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

  // Render onboarding screens
  if (onboardingStep === ONBOARDING_STEPS.USER_DETAILS) {
    return (
      <BirthDetailsModal 
        token={token} 
        isOpen={true} 
        onClose={() => {}} 
        onComplete={handleUserDetailsComplete}
        isOnboarding={true}
      />
    );
  }

  if (onboardingStep === ONBOARDING_STEPS.HOW_IT_WORKS) {
    return (
      <HowNiroWorksScreen 
        onNext={() => handleOnboardingNext(ONBOARDING_STEPS.HOW_IT_WORKS)} 
        onBack={() => setOnboardingStep(ONBOARDING_STEPS.USER_DETAILS)} 
      />
    );
  }

  if (onboardingStep === ONBOARDING_STEPS.TRUST_SAFETY) {
    return (
      <TrustSafetyScreen 
        onComplete={() => handleOnboardingNext(ONBOARDING_STEPS.TRUST_SAFETY)} 
        onBack={() => setOnboardingStep(ONBOARDING_STEPS.HOW_IT_WORKS)} 
      />
    );
  }

  // Common screen props
  const screenProps = {
    token,
    userId,
    userState,
    userName: getUserName(),
    hasBottomNav: showBottomNav,
    onNavigate: handleNavigate,
    onTabChange: handleTabChange,
    onCheckout: handleCheckout,
  };

  return (
    <ChatProvider>
      <div 
        className="min-h-screen relative" 
        style={{ backgroundColor: colors.background.primary }}
      >
        <div className="w-full max-w-7xl mx-auto">
          <Routes>
            {/* Home */}
            <Route 
              index 
              element={
                <HomeScreen 
                  {...screenProps}
                  onChatWithMira={() => navigate('/app/mira')}
                  onTalkToHuman={() => navigate('/app/categories', { 
                    state: { showAllCategories: true, title: 'Talk to a Human Astrologer' } 
                  })}
                  onOpenProfile={() => navigate('/app/profile')}
                />
              } 
            />

            {/* Topic */}
            <Route 
              path="topic/:topicId" 
              element={
                <TopicLandingPageWrapper {...screenProps} />
              } 
            />

            {/* Package */}
            <Route 
              path="package/:packageId" 
              element={
                <PackageLandingPageWrapper {...screenProps} />
              } 
            />

            {/* Checkout */}
            <Route 
              path="checkout" 
              element={
                <CheckoutScreenWrapper 
                  {...screenProps}
                  onSuccess={handlePurchaseSuccess}
                />
              } 
            />

            {/* Plan Dashboard */}
            <Route 
              path="plan/:planId" 
              element={
                <PlanDashboardWrapper {...screenProps} />
              } 
            />

            {/* My Pack */}
            <Route 
              path="mypack" 
              element={
                <MyPackScreen {...screenProps} />
              } 
            />

            {/* Experts */}
            <Route 
              path="experts" 
              element={
                <ExpertsScreen {...screenProps} />
              } 
            />

            {/* Expert Profile */}
            <Route 
              path="expert/:expertId" 
              element={
                <ExpertProfileWrapper {...screenProps} />
              } 
            />

            {/* Mira Chat */}
            <Route 
              path="mira" 
              element={
                <AskMiraScreen 
                  token={token}
                  initialMessage={miraInitialMessage}
                  onNavigate={handleNavigate}
                />
              } 
            />

            {/* Profile */}
            <Route 
              path="profile" 
              element={
                <ProfileScreen 
                  {...screenProps}
                  hasBottomNav={false}
                  onBack={() => navigate(-1)}
                />
              } 
            />

            {/* Astro/Kundli */}
            <Route 
              path="astro" 
              element={
                <KundliScreenSimplified {...screenProps} />
              } 
            />

            {/* Remedies */}
            <Route 
              path="remedies" 
              element={
                <RemediesScreen {...screenProps} />
              } 
            />

            {/* Schedule Call */}
            <Route 
              path="schedule" 
              element={
                <ScheduleCallScreen
                  onBack={() => navigate('/')}
                  onComplete={() => navigate('/app')}
                  userName={getUserName()}
                />
              } 
            />

            {/* Category Listing */}
            <Route 
              path="categories" 
              element={
                <CategoryListingWrapper 
                  onBack={() => navigate(-1)}
                  onNavigate={handleNavigate}
                />
              } 
            />

            {/* Fallback */}
            <Route path="*" element={<Navigate to="/app" replace />} />
          </Routes>
        </div>

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
    </ChatProvider>
  );
}

// Wrapper components to extract route params
function TopicLandingPageWrapper(props) {
  const navigate = useNavigate();
  const { topicId } = useParams();
  
  return (
    <TopicLandingPage 
      {...props}
      topicId={topicId}
      onBack={() => navigate(-1)}
    />
  );
}

function PackageLandingPageWrapper(props) {
  const navigate = useNavigate();
  const location = useLocation();
  const { packageId } = useParams();
  
  return (
    <PackageLandingPage 
      {...props}
      packageId={packageId}
      tileData={location.state?.tileData}
      onBack={() => navigate(-1)}
    />
  );
}

function CheckoutScreenWrapper(props) {
  const navigate = useNavigate();
  const location = useLocation();
  
  return (
    <CheckoutScreen 
      {...props}
      tierId={location.state?.tierId}
      scenarioIds={location.state?.scenarioIds || []}
      onBack={() => {
        if (location.state?._returnPath) {
          navigate(location.state._returnPath);
        } else {
          navigate(-1);
        }
      }}
    />
  );
}

function PlanDashboardWrapper(props) {
  const navigate = useNavigate();
  const { planId } = useParams();
  
  return (
    <PlanDashboard 
      {...props}
      planId={planId}
      onBack={() => navigate(-1)}
    />
  );
}

function ExpertProfileWrapper(props) {
  const navigate = useNavigate();
  const location = useLocation();
  const { expertId } = useParams();
  
  return (
    <ExpertProfileScreen 
      {...props}
      expertId={expertId}
      onBack={() => navigate(-1)}
    />
  );
}

function CategoryListingWrapper({ onBack, onNavigate }) {
  const location = useLocation();
  const { categoryId, showAllCategories, title } = location.state || {};
  
  return (
    <CategoryListingPage
      categoryId={categoryId}
      showAllCategories={showAllCategories}
      title={title || 'Browse Topics'}
      onBack={onBack}
      onTileClick={(tileId) => {
        onNavigate('topic', { topicId: tileId });
      }}
    />
  );
}

// Import useParams for wrapper components
import { useParams } from 'react-router-dom';
