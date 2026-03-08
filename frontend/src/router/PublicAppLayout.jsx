import React, { useState, useEffect, useCallback, useRef } from 'react';
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
import ScheduleCallScreen from '../components/screens/simplified/ScheduleCallScreenV2';
import ExpertPackagesPage from '../components/screens/simplified/ExpertPackagesPage';
import FreeCallWizard from '../components/screens/simplified/FreeCallWizard';

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

// Wrapper so ScheduleCallScreen can read expertId/expertName/consultation from router state
function ScheduleCallRouteWrapper({ token, user, onNavigate }) {
  const { state } = useLocation();
  const navigate = useNavigate();
  return (
    <ScheduleCallScreen
      token={token}
      user={user}
      onBack={() => navigate(-1)}
      onComplete={() => navigate('/app/mypack')}
      onNavigate={onNavigate}
      expertId={state?.expertId}
      expertName={state?.expertName}
      topicId={state?.topicId}
      consultation={state?.consultation}
      bookingId={state?.bookingId}
    />
  );
}

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
  const [showFreeCallWizard, setShowFreeCallWizard] = useState(false);
  const [freeCallInitialTopicId, setFreeCallInitialTopicId] = useState(null);

  // Android back button: when wizard is open, push a history entry so pressing
  // the hardware back button closes the wizard instead of leaving the app.
  const wizardClosingByButtonRef = useRef(false);

  useEffect(() => {
    if (!showFreeCallWizard) return;

    // Push a dummy entry (same URL) so back button can be intercepted
    window.history.pushState({ niroWizard: true }, '', window.location.href);

    const handlePopState = () => {
      if (wizardClosingByButtonRef.current) {
        // Already being closed by a button click — nothing to do
        wizardClosingByButtonRef.current = false;
        return;
      }
      setShowFreeCallWizard(false);
      setFreeCallInitialTopicId(null);
    };

    window.addEventListener('popstate', handlePopState);
    return () => window.removeEventListener('popstate', handlePopState);
  }, [showFreeCallWizard]);

  // Close wizard and clean up the extra history entry we pushed.
  // We use replaceState (synchronous) rather than history.go(-1) (async).
  // history.go(-1) would fire *after* any subsequent navigate() call and undo
  // the new navigation — e.g. expert profile → back to /app (the bug).
  // replaceState just strips the niroWizard marker from the current entry
  // without triggering a backward navigation, so it never races with navigate().
  const closeWizard = useCallback(() => {
    wizardClosingByButtonRef.current = true;
    setShowFreeCallWizard(false);
    setFreeCallInitialTopicId(null);
    if (window.history.state?.niroWizard) {
      window.history.replaceState(null, '', window.location.href);
    }
  }, []);

  // Onboarding state (only for authenticated users)
  const [onboardingStep, setOnboardingStep] = useState(() => {
    if (!isAuthenticated) return ONBOARDING_STEPS.COMPLETE;
    
    const onboardingComplete = localStorage.getItem(ONBOARDING_KEY) === 'true';
    const userDetailsComplete = localStorage.getItem(USER_DETAILS_KEY) === 'true';
    const isReturningUser = user?.profile_complete || user?.dob;

    if (onboardingComplete) return ONBOARDING_STEPS.COMPLETE;
    if (userDetailsComplete || isReturningUser) {
      // User details done — mark everything complete and go straight to app
      localStorage.setItem(USER_DETAILS_KEY, 'true');
      localStorage.setItem(ONBOARDING_KEY, 'true');
      return ONBOARDING_STEPS.COMPLETE;
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

  // Handle user intent from landing page — works for ALL users including anonymous.
  // Login is deferred to the booking step (ExpertProfile → Consult CTA).
  useEffect(() => {
    const intent = getUserIntent();
    if (!intent) return;
    clearUserIntent();

    if (intent.type === 'topic' && intent.topicId) {
      navigate(`/app/topic/${intent.topicId}`, { replace: true });
    } else if (intent.type === 'free_call') {
      // Open the guided wizard — no login required at this stage
      setShowFreeCallWizard(true);
    } else if (intent.type === 'expert' && intent.expertId) {
      navigate(`/app/expert/${intent.expertId}`, { replace: true });
    } else if (intent.returnTo) {
      navigate(intent.returnTo, { replace: true });
    }
  }, []); // eslint-disable-line

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
          localStorage.setItem('niro_redirect_after_login', '/app/mira');
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
          localStorage.setItem('niro_redirect_after_login', '/app/mypack');
          onLoginClick?.();
          return;
        }
        navigate('/app/mypack');
        break;
      case 'astro':
        if (!isAuthenticated) {
          localStorage.setItem('niro_redirect_after_login', '/app/astro');
          onLoginClick?.();
          return;
        }
        navigate('/app/astro');
        break;
      default:
        navigate('/app');
    }
  };

  // Handle topic selection — opens FreeCallWizard with topic pre-selected
  const handleTopicSelect = (topicId) => {
    setFreeCallInitialTopicId(topicId || null);
    setShowFreeCallWizard(true);
  };

  // Kept for direct /app/topic/:topicId URL access
  const handleTopicCtaClick = (topicId) => {
    navigate(`/app/experts${topicId ? `?topicId=${topicId}` : ''}`);
  };

  // Handle navigation from HomeScreen (supports multiple destination types)
  const handleNavigate = (destination, params = {}) => {
    switch (destination) {
      case 'topic':
        setFreeCallInitialTopicId(params.topicId || null);
        setShowFreeCallWizard(true);
        break;
      case 'packageLanding':
        navigate(`/app/package/${params.packageId}`);
        break;
      case 'expert':
      case 'expertProfile': {
        const q = new URLSearchParams();
        if (params.topicId) q.set('topicId', params.topicId);
        if (params.topicContext) q.set('context', params.topicContext);
        const qs = q.toString();
        navigate(`/app/expert/${params.expertId}${qs ? '?' + qs : ''}`);
        break;
      }
      case 'experts':
        navigate('/app/experts');
        break;
      case 'remedies':
        navigate('/app/remedies');
        break;
      case 'mira':
        if (!isAuthenticated) {
          localStorage.setItem('niro_redirect_after_login', '/app/mira');
          onLoginClick?.();
          return;
        }
        navigate('/app/mira');
        break;
      case 'mypack':
        if (!isAuthenticated) {
          localStorage.setItem('niro_redirect_after_login', '/app/mypack');
          onLoginClick?.();
          return;
        }
        navigate('/app/mypack');
        break;
      case 'profile':
        if (!isAuthenticated) {
          localStorage.setItem('niro_redirect_after_login', '/app/profile');
          onLoginClick?.();
          return;
        }
        navigate('/app/profile');
        break;
      case 'expertPackages':
        navigate(`/app/expert/${params?.expertId}/packages`);
        break;
      case 'schedule':
        if (!isAuthenticated) {
          // Redirect back to this expert's profile after login
          const scheduleExpertPath = params?.expertId ? `/app/expert/${params.expertId}` : '/app/experts';
          localStorage.setItem('niro_redirect_after_login', scheduleExpertPath);
          onLoginClick?.();
          return;
        }
        if (params?.consultation) {
          // Paid consultation — go to checkout first
          navigate('/app/checkout', {
            state: {
              expertId: params.expertId,
              expertName: params.expertName,
              consultation: params.consultation,
            }
          });
        } else {
          navigate('/app/schedule', { state: { expertId: params?.expertId, expertName: params?.expertName, topicId: params?.topicId || freeCallInitialTopicId } });
        }
        break;
      case 'plan':
        if (!isAuthenticated) {
          localStorage.setItem('niro_redirect_after_login', '/app/mypack');
          onLoginClick?.();
          return;
        }
        navigate(`/app/plan/${params.planId}`);
        break;
      case 'checkout':
        if (!isAuthenticated) {
          // Redirect back to this expert's profile after login
          const checkoutExpertPath = params?.expertId ? `/app/expert/${params.expertId}` : '/app/experts';
          localStorage.setItem('niro_redirect_after_login', checkoutExpertPath);
          onLoginClick?.();
          return;
        }
        navigate('/app/checkout', { state: params });
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
  // BirthDetailsModal saves to /api/profile/ itself, then calls onComplete() with no args.
  // We just need to advance the onboarding step and restore any pending redirect.
  const handleBirthDetailsSubmit = () => {
    localStorage.setItem(USER_DETAILS_KEY, 'true');
    localStorage.setItem(ONBOARDING_KEY, 'true');
    setOnboardingStep(ONBOARDING_STEPS.COMPLETE);
    trackEvent('birth_details_submitted');

    // After filling birth details, navigate to wherever the user was originally trying to go
    const redirect = localStorage.getItem('niro_redirect_after_login');
    if (redirect) {
      localStorage.removeItem('niro_redirect_after_login');
      navigate(redirect, { replace: true });
    }
  };

  // Handle CTA click - open the free call onboarding wizard (no login required at this stage)
  const handleCtaClick = (topicId = null) => {
    setFreeCallInitialTopicId(topicId || null);
    setShowFreeCallWizard(true);
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
          onComplete={handleBirthDetailsSubmit}
          token={token}
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
                  onTalkToHuman={handleCtaClick}
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
                  onTalkToHuman={handleCtaClick}
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
                  onCtaClick={handleTopicCtaClick}
                />
              } 
            />
            <Route 
              path="experts" 
              element={
                <ExpertsScreen 
                  onNavigate={handleNavigate}
                  onTabChange={handleTabChange}
                  isAuthenticated={isAuthenticated}
                  onLoginClick={onLoginClick}
                />
              } 
            />
            <Route
              path="expert/:expertId"
              element={
                <ExpertProfileScreen
                  onNavigate={handleNavigate}
                  isAuthenticated={isAuthenticated}
                  user={user}
                  onLoginClick={onLoginClick}
                  hasBottomNav={true}
                />
              }
            />
            <Route
              path="expert/:expertId/packages"
              element={<ExpertPackagesPage token={token} onNavigate={handleNavigate} />}
            />
            <Route 
              path="remedies" 
              element={
                <RemediesScreen 
                  onNavigate={handleNavigate}
                  onTabChange={handleTabChange}
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
                  <CheckoutScreen token={token} user={user} onTabChange={handleTabChange} />
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
                  <MyPackScreen
                    token={token}
                    user={user}
                    userState={userState}
                    onNavigate={handleNavigate}
                    onTabChange={handleTabChange}
                    hasBottomNav={shouldShowBottomNav()}
                  />
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
                  <ScheduleCallRouteWrapper token={token} user={user} onNavigate={handleNavigate} />
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

        {/* Free Call Onboarding Wizard */}
        {showFreeCallWizard && (
          <FreeCallWizard
            token={token}
            user={user}
            userState={userState}
            initialTopicId={freeCallInitialTopicId}
            onClose={closeWizard}
            onNavigate={handleNavigate}
            onTabChange={handleTabChange}
          />
        )}
      </div>
    </ChatProvider>
  );
}
