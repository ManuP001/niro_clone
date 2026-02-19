import React, { useState, useEffect, useCallback } from 'react';
import { Routes, Route, useNavigate, useLocation, Navigate } from 'react-router-dom';
import { ChatProvider } from '../context/ChatContext';
import { colors } from '../components/screens/simplified/theme';
import { apiSimplified, trackEvent } from '../components/screens/simplified/utils';
import { clearUserIntent, getUserIntent } from '../components/screens/simplified/PublicLandingPage';

// Screens - Browse (public, no login required)
import HomeScreen from '../components/screens/simplified/HomeScreen';
import TopicLandingPage from '../components/screens/simplified/TopicLandingPage';
import ExpertsScreen from '../components/screens/simplified/ExpertsScreen';
import ExpertProfileScreen from '../components/screens/simplified/ExpertProfileScreen';
import RemediesScreen from '../components/screens/simplified/RemediesScreen';
import CategoryListingPage from '../components/screens/simplified/CategoryListingPage';

// Screens - Protected (login required)
import PackageLandingPage from '../components/screens/simplified/PackageLandingPage';
import CheckoutScreen from '../components/screens/simplified/CheckoutScreen';
import PlanDashboard from '../components/screens/simplified/PlanDashboard';
import MyPackScreen from '../components/screens/simplified/MyPackScreen';
import AskMiraScreen from '../components/screens/simplified/AskMiraScreen';
import ProfileScreen from '../components/screens/simplified/ProfileScreen';
import KundliScreenSimplified from '../components/screens/simplified/KundliScreenSimplified';
import ScheduleCallScreen from '../components/screens/simplified/ScheduleCallScreen';

// Components
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

// Routes that require authentication
const PROTECTED_ROUTES = [
  '/app/checkout',
  '/app/mypack',
  '/app/mira',
  '/app/profile',
  '/app/astro',
  '/app/schedule',
  '/app/plan',
];

/**
 * PublicAppLayout - Main app layout supporting both public and authenticated routes
 * 
 * Public routes (no login required):
 * - /app (home/topics)
 * - /app/topics
 * - /app/topic/:topicId
 * - /app/experts
 * - /app/expert/:expertId
 * - /app/remedies
 * - /app/categories
 * 
 * Protected routes (login required):
 * - /app/checkout
 * - /app/mypack
 * - /app/mira
 * - /app/profile
 * - /app/astro
 * - /app/schedule
 * - /app/plan/:planId
 */
export default function PublicAppLayout({ authState, onLogout, onLoginClick }) {
  const navigate = useNavigate();
  const location = useLocation();
  const { token, userId, user, isAuthenticated } = authState;

  // Check if current route requires authentication
  const isProtectedRoute = PROTECTED_ROUTES.some(route => 
    location.pathname.startsWith(route)
  );

  // Redirect to login if accessing protected route without auth
  useEffect(() => {
    if (isProtectedRoute && !isAuthenticated) {
      // Store the intended destination
      localStorage.setItem('niro_redirect_after_login', location.pathname);
      navigate('/login', { replace: true });
    }
  }, [isProtectedRoute, isAuthenticated, location.pathname, navigate]);

  // User state
  const [userState, setUserState] = useState(null);
  const [loadingState, setLoadingState] = useState(true);
  const [miraInitialMessage, setMiraInitialMessage] = useState('');
  const [showHomeTour, setShowHomeTour] = useState(false);

  // Onboarding state (only for authenticated users)
  const [onboardingStep, setOnboardingStep] = useState(() => {
    if (!isAuthenticated) return ONBOARDING_STEPS.COMPLETE;
    
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

  // Load user state (only for authenticated users)
  const loadUserState = useCallback(async () => {
    if (!isAuthenticated || !token) {
      setLoadingState(false);
      return null;
    }
    
    try {
      const response = await apiSimplified.get('/user/state', token);
      setUserState(response.user_state);
      return response.user_state;
    } catch (err) {
      console.error('Failed to load user state:', err);
      setLoadingState(false);
      return null;
    }
  }, [token, isAuthenticated]);

  // Initial load
  useEffect(() => {
    if (isAuthenticated) {
      loadUserState().finally(() => setLoadingState(false));
    } else {
      setLoadingState(false);
    }
  }, [loadUserState, isAuthenticated]);

  // Handle user intent from landing page (only for authenticated users)
  useEffect(() => {
    if (!isAuthenticated) return;
    
    const intent = getUserIntent();
    if (intent) {
      clearUserIntent();
      
      if (intent.type === 'topic' && intent.topicId) {
        navigate(`/app/topic/${intent.topicId}`, { replace: true });
      } else if (intent.type === 'free_call') {
        navigate('/app/schedule', { replace: true });
      } else if (intent.type === 'expert' && intent.expertId) {
        navigate(`/app/expert/${intent.expertId}`, { replace: true });
      } else if (intent.returnTo) {
        navigate(intent.returnTo, { replace: true });
      }
    }
  }, [navigate, isAuthenticated]);

  // Update active tab on route change
  useEffect(() => {
    const path = location.pathname;
    if (path.includes('/experts') || path.includes('/expert/')) setActiveTab('consult');
    else if (path.includes('/mira')) setActiveTab('mira');
    else if (path.includes('/remedies')) setActiveTab('remedies');
    else if (path.includes('/mypack')) setActiveTab('mypack');
    else if (path.includes('/astro')) setActiveTab('astro');
    else setActiveTab('home');
  }, [location.pathname]);

  // Handle tab navigation
  const handleTabChange = (tab) => {
    setActiveTab(tab);
    switch (tab) {
      case 'home':
        navigate('/app');
        break;
      case 'consult':
        navigate('/app/experts');
        break;
      case 'mira':
        if (!isAuthenticated) {
          onLoginClick?.();
          return;
        }
        navigate('/app/mira');
        break;
      case 'remedies':
        navigate('/app/remedies');
        break;
      case 'mypack':
        if (!isAuthenticated) {
          onLoginClick?.();
          return;
        }
        navigate('/app/mypack');
        break;
      case 'astro':
        if (!isAuthenticated) {
          onLoginClick?.();
          return;
        }
        navigate('/app/astro');
        break;
      default:
        navigate('/app');
    }
  };

  // Handle topic selection
  const handleTopicSelect = (topicId) => {
    navigate(`/app/topic/${topicId}`);
  };

  // Handle navigation from HomeScreen (supports multiple destination types)
  const handleNavigate = (destination, params = {}) => {
    switch (destination) {
      case 'topic':
        navigate(`/app/topic/${params.topicId}`);
        break;
      case 'packageLanding':
        navigate(`/app/package/${params.packageId}`);
        break;
      case 'expert':
        navigate(`/app/expert/${params.expertId}`);
        break;
      case 'experts':
        navigate('/app/experts');
        break;
      case 'remedies':
        navigate('/app/remedies');
        break;
      case 'mira':
        if (!isAuthenticated) {
          onLoginClick?.();
          return;
        }
        navigate('/app/mira');
        break;
      case 'mypack':
        if (!isAuthenticated) {
          onLoginClick?.();
          return;
        }
        navigate('/app/mypack');
        break;
      case 'profile':
        if (!isAuthenticated) {
          onLoginClick?.();
          return;
        }
        navigate('/app/profile');
        break;
      case 'schedule':
        if (!isAuthenticated) {
          onLoginClick?.();
          return;
        }
        navigate('/app/schedule');
        break;
      default:
        navigate('/app');
    }
  };

  // Handle expert selection
  const handleExpertSelect = (expertId) => {
    navigate(`/app/expert/${expertId}`);
  };

  // Handle onboarding completion
  const handleOnboardingComplete = () => {
    localStorage.setItem(ONBOARDING_KEY, 'true');
    setOnboardingStep(ONBOARDING_STEPS.COMPLETE);
    
    // Show home tour for first-time users
    const homeTourComplete = localStorage.getItem(HOME_TOUR_KEY) === 'true';
    if (!homeTourComplete && location.pathname === '/app') {
      setShowHomeTour(true);
    }
  };

  // Handle birth details submission
  const handleBirthDetailsSubmit = async (birthData) => {
    if (!isAuthenticated || !token) return;
    
    try {
      await apiSimplified.post('/user/birth-details', birthData, token);
      localStorage.setItem(USER_DETAILS_KEY, 'true');
      setOnboardingStep(ONBOARDING_STEPS.HOW_IT_WORKS);
      trackEvent('birth_details_submitted');
    } catch (err) {
      console.error('Failed to save birth details:', err);
    }
  };

  // Handle onboarding step progression
  const handleOnboardingNext = () => {
    if (onboardingStep === ONBOARDING_STEPS.HOW_IT_WORKS) {
      setOnboardingStep(ONBOARDING_STEPS.TRUST_SAFETY);
    } else if (onboardingStep === ONBOARDING_STEPS.TRUST_SAFETY) {
      handleOnboardingComplete();
    }
  };

  // Show onboarding screens for authenticated users
  if (isAuthenticated && onboardingStep !== ONBOARDING_STEPS.COMPLETE) {
    if (onboardingStep === ONBOARDING_STEPS.USER_DETAILS) {
      return (
        <BirthDetailsModal
          isOpen={true}
          onClose={() => {}}
          onSubmit={handleBirthDetailsSubmit}
          user={user}
        />
      );
    }
    if (onboardingStep === ONBOARDING_STEPS.HOW_IT_WORKS) {
      return <HowNiroWorksScreen onNext={handleOnboardingNext} />;
    }
    if (onboardingStep === ONBOARDING_STEPS.TRUST_SAFETY) {
      return <TrustSafetyScreen onNext={handleOnboardingNext} />;
    }
  }

  // Helper to check if current route should show bottom nav
  const shouldShowBottomNav = () => {
    const path = location.pathname;
    // Hide bottom nav on checkout and specific flows
    if (path.includes('/checkout')) return false;
    if (path.includes('/plan/')) return false;
    return true;
  };

  return (
    <ChatProvider>
      <div 
        className="min-h-screen flex flex-col"
        style={{ backgroundColor: colors.background.primary }}
      >
        {/* Main Content */}
        <main className="flex-1 pb-20">
          <Routes>
            {/* Public Browse Routes - No login required */}
            <Route 
              index 
              element={
                <HomeScreen 
                  userState={userState}
                  onNavigate={handleNavigate}
                  onTabChange={handleTabChange}
                  isAuthenticated={isAuthenticated}
                  user={user}
                  onLoginClick={onLoginClick}
                />
              } 
            />
            <Route 
              path="topics" 
              element={
                <HomeScreen 
                  userState={userState}
                  onNavigate={handleNavigate}
                  onTabChange={handleTabChange}
                  isAuthenticated={isAuthenticated}
                  user={user}
                  onLoginClick={onLoginClick}
                />
              } 
            />
            <Route 
              path="topic/:topicId" 
              element={
                <TopicLandingPage 
                  isAuthenticated={isAuthenticated}
                  user={user}
                  onLoginClick={onLoginClick}
                />
              } 
            />
            <Route 
              path="experts" 
              element={
                <ExpertsScreen 
                  onExpertSelect={handleExpertSelect}
                  isAuthenticated={isAuthenticated}
                  onLoginClick={onLoginClick}
                />
              } 
            />
            <Route 
              path="expert/:expertId" 
              element={
                <ExpertProfileScreen 
                  isAuthenticated={isAuthenticated}
                  user={user}
                  onLoginClick={onLoginClick}
                />
              } 
            />
            <Route 
              path="remedies" 
              element={
                <RemediesScreen 
                  isAuthenticated={isAuthenticated}
                  token={token}
                  onLoginClick={onLoginClick}
                />
              } 
            />
            <Route 
              path="categories" 
              element={
                <CategoryListingPage 
                  onTopicSelect={handleTopicSelect}
                />
              } 
            />

            {/* Protected Routes - Login required */}
            <Route 
              path="package/:packageId" 
              element={
                isAuthenticated ? (
                  <PackageLandingPage token={token} />
                ) : (
                  <Navigate to="/login" replace />
                )
              } 
            />
            <Route 
              path="checkout" 
              element={
                isAuthenticated ? (
                  <CheckoutScreen token={token} user={user} />
                ) : (
                  <Navigate to="/login" replace />
                )
              } 
            />
            <Route 
              path="plan/:planId" 
              element={
                isAuthenticated ? (
                  <PlanDashboard token={token} user={user} />
                ) : (
                  <Navigate to="/login" replace />
                )
              } 
            />
            <Route 
              path="mypack" 
              element={
                isAuthenticated ? (
                  <MyPackScreen token={token} user={user} />
                ) : (
                  <Navigate to="/login" replace />
                )
              } 
            />
            <Route 
              path="mira" 
              element={
                isAuthenticated ? (
                  <AskMiraScreen 
                    token={token} 
                    user={user}
                    initialMessage={miraInitialMessage}
                    onClearInitialMessage={() => setMiraInitialMessage('')}
                  />
                ) : (
                  <Navigate to="/login" replace />
                )
              } 
            />
            <Route 
              path="profile" 
              element={
                isAuthenticated ? (
                  <ProfileScreen 
                    token={token} 
                    user={user}
                    onLogout={onLogout}
                  />
                ) : (
                  <Navigate to="/login" replace />
                )
              } 
            />
            <Route 
              path="astro" 
              element={
                isAuthenticated ? (
                  <KundliScreenSimplified token={token} user={user} />
                ) : (
                  <Navigate to="/login" replace />
                )
              } 
            />
            <Route 
              path="schedule" 
              element={
                isAuthenticated ? (
                  <ScheduleCallScreen token={token} user={user} />
                ) : (
                  <Navigate to="/login" replace />
                )
              } 
            />

            {/* Fallback */}
            <Route path="*" element={<Navigate to="/app" replace />} />
          </Routes>
        </main>

        {/* Bottom Navigation */}
        {shouldShowBottomNav() && (
          <BottomNav 
            activeTab={activeTab}
            onTabChange={handleTabChange}
            isAuthenticated={isAuthenticated}
          />
        )}

        {/* Home Tour Overlay (for authenticated users) */}
        {showHomeTour && isAuthenticated && (
          <HomeTourOverlay 
            onComplete={() => {
              localStorage.setItem(HOME_TOUR_KEY, 'true');
              setShowHomeTour(false);
            }}
          />
        )}
      </div>
    </ChatProvider>
  );
}
