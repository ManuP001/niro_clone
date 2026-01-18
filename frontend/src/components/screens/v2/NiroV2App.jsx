import React, { useState, useEffect } from 'react';
import HomeScreenV2 from './HomeScreenV2';
import IntakeScreen from './IntakeScreen';
import RecommendationsScreen from './RecommendationsScreen';
import PackageLandingScreen from './PackageLandingScreen';
import CheckoutScreen from './CheckoutScreen';
import PlanDashboardScreen from './PlanDashboardScreen';
import RemedyCatalogScreen from './RemedyCatalogScreen';
import ProfileScreenV2 from './ProfileScreenV2';

/**
 * NiroV2App - Main navigation controller for NIRO V2
 * 
 * Flow:
 * Home -> Intake -> Recommendations -> Package Landing -> Checkout -> Plan Dashboard
 *                                                     -> Remedy Catalog (optional)
 */
export default function NiroV2App({ token, userId, existingChat }) {
  const [screen, setScreen] = useState('home');
  const [screenParams, setScreenParams] = useState({});
  const [navigationStack, setNavigationStack] = useState(['home']);

  const navigate = (newScreen, params = {}) => {
    setNavigationStack(prev => [...prev, newScreen]);
    setScreen(newScreen);
    setScreenParams(params);
  };

  const goBack = () => {
    if (navigationStack.length > 1) {
      const newStack = [...navigationStack];
      newStack.pop();
      const previousScreen = newStack[newStack.length - 1];
      setNavigationStack(newStack);
      setScreen(previousScreen);
      setScreenParams({});
    }
  };

  const resetToHome = () => {
    setNavigationStack(['home']);
    setScreen('home');
    setScreenParams({});
  };

  // Handle intake completion -> go to recommendations
  const handleIntakeComplete = (intakeId, intakeData) => {
    navigate('recommendations', { intakeId, intakeData });
  };

  // Handle package selection -> go to package landing
  const handleSelectPackage = (packageId, recommendationId) => {
    navigate('package', { packageId, recommendationId });
  };

  // Handle checkout initiation
  const handleCheckout = (packageId, selectedRemedyIds, recommendationId) => {
    navigate('checkout', { packageId, selectedRemedyIds, recommendationId });
  };

  // Handle purchase success -> go to plan dashboard
  const handlePurchaseSuccess = (planId) => {
    setNavigationStack(['home', 'plan']);
    setScreen('plan');
    setScreenParams({ planId, isNew: true });
  };

  // Handle remedy purchase
  const handleRemedyPurchase = (remedyId, planId) => {
    // In full implementation, this would open checkout for the remedy
    console.log('Purchase remedy:', remedyId, 'for plan:', planId);
    alert('Remedy purchase flow - would open payment');
  };

  // Render current screen
  const renderScreen = () => {
    switch (screen) {
      case 'home':
        return (
          <HomeScreenV2 
            token={token} 
            userId={userId}
            onNavigate={(dest, params) => {
              if (dest === 'intake') {
                navigate('intake', params);
              } else if (dest === 'plan') {
                navigate('plan', params);
              } else if (dest === 'profile') {
                navigate('profile');
              } else if (dest === 'chat' && existingChat) {
                // Navigate to existing chat if available
                existingChat();
              }
            }}
          />
        );

      case 'intake':
        return (
          <IntakeScreen 
            token={token}
            initialTopic={screenParams.topic}
            onComplete={handleIntakeComplete}
            onBack={goBack}
          />
        );

      case 'recommendations':
        return (
          <RecommendationsScreen 
            token={token}
            intakeId={screenParams.intakeId}
            intakeData={screenParams.intakeData}
            onSelectPackage={handleSelectPackage}
            onBack={goBack}
          />
        );

      case 'package':
        return (
          <PackageLandingScreen 
            token={token}
            packageId={screenParams.packageId}
            recommendationId={screenParams.recommendationId}
            onCheckout={handleCheckout}
            onBack={goBack}
          />
        );

      case 'checkout':
        return (
          <CheckoutScreen 
            token={token}
            packageId={screenParams.packageId}
            selectedRemedyIds={screenParams.selectedRemedyIds || []}
            recommendationId={screenParams.recommendationId}
            onSuccess={handlePurchaseSuccess}
            onBack={goBack}
          />
        );

      case 'plan':
        return (
          <PlanDashboardScreen 
            token={token}
            planId={screenParams.planId}
            onBack={resetToHome}
            onNavigate={(dest, params) => {
              if (dest === 'remedies') {
                navigate('remedies', params);
              } else if (dest === 'chat' && existingChat) {
                existingChat();
              }
            }}
          />
        );

      case 'remedies':
        return (
          <RemedyCatalogScreen 
            token={token}
            planId={screenParams.planId}
            onPurchase={handleRemedyPurchase}
            onBack={goBack}
          />
        );

      case 'profile':
        return (
          <ProfileScreenV2 
            token={token}
            userId={userId}
            onNavigate={(dest, params) => {
              if (dest === 'plan') {
                navigate('plan', params);
              }
            }}
            onBack={goBack}
          />
        );

      default:
        return (
          <HomeScreenV2 
            token={token} 
            userId={userId}
            onNavigate={(dest, params) => navigate(dest, params)}
          />
        );
    }
  };

  return (
    <div className="niro-v2-app">
      {renderScreen()}
    </div>
  );
}
