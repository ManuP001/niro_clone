import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';

// Landing page
import PublicLandingPage from '../components/screens/simplified/PublicLandingPage';
import LoginScreen from '../components/screens/LoginScreen';
import AuthCallback from '../components/screens/AuthCallback';

// App layouts
import AppLayout from './AppLayout';
import PublicAppLayout from './PublicAppLayout';

// Legacy public pages (kept for future use, not routed)
// import PublicExpertsPage from '../components/screens/simplified/PublicExpertsPage';
// import PublicExpertProfilePage from '../components/screens/simplified/PublicExpertProfilePage';
// import PublicTopicsPage from '../components/screens/simplified/PublicTopicsPage';
// import PublicTopicLandingPage from '../components/screens/simplified/PublicTopicLandingPage';
// import PublicRemediesPage from '../components/screens/simplified/PublicRemediesPage';

// Admin
import AdminDashboard from '../components/admin/AdminDashboard';

/**
 * AppRoutes - Central routing configuration
 * 
 * Public Routes (no login required):
 * - / : Marketing landing page
 * - /login : Login screen
 * - /auth/callback : OAuth callback handler
 * 
 * Public App Routes (no login required, main PWA experience):
 * - /app : Home screen (topics browsing)
 * - /app/topics : Topics listing (alias for /app)
 * - /app/topic/:topicId : Topic landing page
 * - /app/experts : Experts listing
 * - /app/expert/:expertId : Expert profile
 * - /app/remedies : Remedies listing
 * 
 * Protected App Routes (require auth):
 * - /app/checkout : Checkout screen
 * - /app/mypack : My Pack screen
 * - /app/mira : Ask Mira chat
 * - /app/profile : User profile
 * - /app/astro : Kundli/Astro screen
 * - /app/schedule : Schedule call screen
 * - /app/plan/:planId : Plan dashboard
 * 
 * Admin Routes:
 * - /admin/* : Admin dashboard
 * 
 * Legacy public routes (disabled, files kept for future):
 * - /topics, /experts, /remedies, /topic/:id, /experts/:id
 */
export default function AppRoutes({ 
  authState, 
  onLoginSuccess, 
  onAuthError, 
  onLogout,
  onLoginClick,
  onNavigateToApp,
}) {
  return (
    <Routes>
      {/* Marketing Landing Page */}
      <Route 
        path="/" 
        element={
          <PublicLandingPage
            isAuthenticated={authState.isAuthenticated}
            user={authState.user}
            onLoginClick={onLoginClick}
            onNavigateToApp={onNavigateToApp}
          />
        } 
      />

      {/* Legacy public routes - redirect to /app equivalents */}
      <Route path="/topics" element={<Navigate to="/app" replace />} />
      <Route path="/experts" element={<Navigate to="/app/experts" replace />} />
      <Route path="/experts/:expertId" element={<Navigate to="/app/expert/:expertId" replace />} />
      <Route path="/topic/:topicId" element={<Navigate to="/app/topic/:topicId" replace />} />
      <Route path="/remedies" element={<Navigate to="/app/remedies" replace />} />
      
      <Route 
        path="/login" 
        element={
          authState.isAuthenticated ? (
            <Navigate to="/app" replace />
          ) : (
            <LoginScreen onLoginSuccess={onLoginSuccess} />
          )
        } 
      />
      
      <Route 
        path="/auth/callback" 
        element={
          <AuthCallback 
            onAuthSuccess={onLoginSuccess}
            onAuthError={onAuthError}
          />
        } 
      />

      {/* Admin Routes */}
      <Route path="/admin/*" element={<AdminDashboard />} />

      {/* Main App Routes - Split into public browse and protected features */}
      <Route 
        path="/app/*" 
        element={
          <PublicAppLayout 
            authState={authState}
            onLogout={onLogout}
            onLoginClick={onLoginClick}
          />
        } 
      />
      
      {/* Catch-all redirect */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
