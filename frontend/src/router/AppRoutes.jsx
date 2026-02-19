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

      {/* Public Experts Page - No login required */}
      <Route 
        path="/experts" 
        element={
          <PublicExpertsPage
            isAuthenticated={authState.isAuthenticated}
            onLoginClick={onLoginClick}
          />
        } 
      />

      {/* Public Expert Profile - No login required */}
      <Route 
        path="/experts/:expertId" 
        element={
          <PublicExpertProfilePage
            isAuthenticated={authState.isAuthenticated}
            onLoginClick={onLoginClick}
          />
        } 
      />

      {/* Public Topics Page - No login required */}
      <Route 
        path="/topics" 
        element={
          <PublicTopicsPage
            isAuthenticated={authState.isAuthenticated}
          />
        } 
      />

      {/* Public Topic Landing Page - No login required, only checkout requires login */}
      <Route 
        path="/topic/:topicId" 
        element={
          <PublicTopicLandingPage
            isAuthenticated={authState.isAuthenticated}
          />
        } 
      />

      {/* Public Remedies Page - No login required, only purchase requires login */}
      <Route 
        path="/remedies" 
        element={
          <PublicRemediesPage
            isAuthenticated={authState.isAuthenticated}
          />
        } 
      />
      
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

      {/* Protected App Routes */}
      <Route 
        path="/app/*" 
        element={
          authState.isAuthenticated ? (
            <AppLayout 
              authState={authState}
              onLogout={onLogout}
            />
          ) : (
            <Navigate to="/login" replace />
          )
        } 
      />
      
      {/* Catch-all redirect */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
