import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';

// Public pages
import PublicLandingPage from '../components/screens/simplified/PublicLandingPage';
import PublicExpertsPage from '../components/screens/simplified/PublicExpertsPage';
import PublicExpertProfilePage from '../components/screens/simplified/PublicExpertProfilePage';
import PublicTopicsPage from '../components/screens/simplified/PublicTopicsPage';
import LoginScreen from '../components/screens/LoginScreen';
import AuthCallback from '../components/screens/AuthCallback';

// Protected app pages
import AppLayout from './AppLayout';
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

// Admin
import AdminDashboard from '../components/admin/AdminDashboard';

/**
 * AppRoutes - Central routing configuration using React Router v7
 * 
 * Public Routes (no login required):
 * - / : Landing page (PublicLandingPage)
 * - /experts : Public experts listing
 * - /experts/:expertId : Public expert profile
 * - /topics : Public life topics page
 * - /login : Login screen
 * - /auth/callback : OAuth callback handler
 * 
 * Protected Routes (require auth):
 * - /app : Home screen
 * - /app/topic/:topicId : Topic landing page
 * - /app/package/:packageId : Package landing page  
 * - /app/checkout : Checkout screen
 * - /app/plan/:planId : Plan dashboard
 * - /app/mypack : My Pack screen
 * - /app/experts : Experts listing
 * - /app/expert/:expertId : Expert profile
 * - /app/mira : Ask Mira chat
 * - /app/profile : User profile
 * - /app/astro : Kundli/Astro screen
 * - /app/remedies : Remedies screen
 * - /app/schedule : Schedule call screen
 * - /app/categories : Category listing
 * 
 * Admin Routes:
 * - /admin/* : Admin dashboard
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
      {/* Public Routes */}
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
