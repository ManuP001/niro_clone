/**
 * NIRO V5 Onboarding State Hook
 * Manages user selections and flow progression with localStorage persistence
 * 
 * Flow: Splash -> Birth Details -> Pick Topic -> Pick Sub-topic -> Trust -> Choose Pack -> Checkout -> Home
 */

import { useState, useEffect, useCallback } from 'react';

const STORAGE_KEY = 'niro_v5_onboarding_state';

// Default state structure
const DEFAULT_STATE = {
  step: 0, // Current step index
  completedSteps: [],
  birthDetails: {
    name: '',
    dateOfBirth: null,
    timeOfBirth: null,
    placeOfBirth: '',
    skipBirthTime: false
  },
  selectedTopic: null, // 'love' | 'career' | 'health'
  selectedSubtopic: null, // e.g., 'relationship-healing'
  selectedTier: null, // 'Focussed' | 'Supported' | 'Comprehensive'
  trustAcknowledged: false,
  checkoutCompleted: false,
  onboardingCompleted: false,
  lastUpdated: null
};

// Step definitions
export const ONBOARDING_STEPS = {
  SPLASH: 0,
  BIRTH_DETAILS: 1,
  PICK_TOPIC: 2,
  PICK_SUBTOPIC: 3,
  TRUST: 4,
  CHOOSE_PACK: 5,
  CHECKOUT: 6,
  HOME: 7
};

export const STEP_NAMES = [
  'splash',
  'birthDetails',
  'pickTopic',
  'pickSubtopic',
  'trust',
  'choosePack',
  'checkout',
  'home'
];

/**
 * Custom hook for managing V5 onboarding state
 */
export function useOnboardingState() {
  const [state, setState] = useState(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        const parsed = JSON.parse(stored);
        return { ...DEFAULT_STATE, ...parsed };
      }
    } catch (e) {
      console.error('Failed to load onboarding state:', e);
    }
    return DEFAULT_STATE;
  });

  // Persist state to localStorage on changes
  useEffect(() => {
    try {
      const toStore = {
        ...state,
        lastUpdated: new Date().toISOString()
      };
      localStorage.setItem(STORAGE_KEY, JSON.stringify(toStore));
    } catch (e) {
      console.error('Failed to persist onboarding state:', e);
    }
  }, [state]);

  // Navigate to a specific step
  const goToStep = useCallback((step) => {
    setState(prev => ({
      ...prev,
      step,
      completedSteps: prev.step < step 
        ? [...new Set([...prev.completedSteps, prev.step])]
        : prev.completedSteps
    }));
  }, []);

  // Go to next step
  const nextStep = useCallback(() => {
    setState(prev => ({
      ...prev,
      step: Math.min(prev.step + 1, ONBOARDING_STEPS.HOME),
      completedSteps: [...new Set([...prev.completedSteps, prev.step])]
    }));
  }, []);

  // Go to previous step
  const prevStep = useCallback(() => {
    setState(prev => ({
      ...prev,
      step: Math.max(prev.step - 1, ONBOARDING_STEPS.SPLASH)
    }));
  }, []);

  // Update birth details
  const setBirthDetails = useCallback((details) => {
    setState(prev => ({
      ...prev,
      birthDetails: {
        ...prev.birthDetails,
        ...details
      }
    }));
  }, []);

  // Skip birth time (set to null)
  const skipBirthTime = useCallback(() => {
    setState(prev => ({
      ...prev,
      birthDetails: {
        ...prev.birthDetails,
        timeOfBirth: null,
        skipBirthTime: true
      }
    }));
  }, []);

  // Select topic
  const selectTopic = useCallback((topicId) => {
    setState(prev => ({
      ...prev,
      selectedTopic: topicId,
      selectedSubtopic: null // Reset subtopic when topic changes
    }));
  }, []);

  // Select subtopic
  const selectSubtopic = useCallback((subtopicSlug) => {
    setState(prev => ({
      ...prev,
      selectedSubtopic: subtopicSlug
    }));
  }, []);

  // Select tier
  const selectTier = useCallback((tierName) => {
    setState(prev => ({
      ...prev,
      selectedTier: tierName
    }));
  }, []);

  // Acknowledge trust screen
  const acknowledgeTrust = useCallback(() => {
    setState(prev => ({
      ...prev,
      trustAcknowledged: true
    }));
  }, []);

  // Complete checkout
  const completeCheckout = useCallback(() => {
    setState(prev => ({
      ...prev,
      checkoutCompleted: true,
      onboardingCompleted: true
    }));
  }, []);

  // Complete onboarding (mark as done)
  const completeOnboarding = useCallback(() => {
    setState(prev => ({
      ...prev,
      onboardingCompleted: true
    }));
  }, []);

  // Reset all state
  const resetState = useCallback(() => {
    localStorage.removeItem(STORAGE_KEY);
    setState(DEFAULT_STATE);
  }, []);

  // Check if a step is accessible
  const canAccessStep = useCallback((targetStep) => {
    // Always allow going back
    if (targetStep <= state.step) return true;
    
    // Check prerequisites for each step
    switch (targetStep) {
      case ONBOARDING_STEPS.BIRTH_DETAILS:
        return state.step >= ONBOARDING_STEPS.SPLASH;
      case ONBOARDING_STEPS.PICK_TOPIC:
        return state.birthDetails.name && state.birthDetails.dateOfBirth;
      case ONBOARDING_STEPS.PICK_SUBTOPIC:
        return state.selectedTopic !== null;
      case ONBOARDING_STEPS.TRUST:
        return state.selectedSubtopic !== null;
      case ONBOARDING_STEPS.CHOOSE_PACK:
        return state.trustAcknowledged;
      case ONBOARDING_STEPS.CHECKOUT:
        return state.selectedTier !== null;
      case ONBOARDING_STEPS.HOME:
        return state.checkoutCompleted || state.onboardingCompleted;
      default:
        return true;
    }
  }, [state]);

  // Get current step name
  const getCurrentStepName = useCallback(() => {
    return STEP_NAMES[state.step] || 'unknown';
  }, [state.step]);

  // Check if onboarding is complete
  const isOnboardingComplete = state.onboardingCompleted;

  // Get tier ID for checkout (combines subtopic + tier)
  const getTierIdForCheckout = useCallback(() => {
    if (!state.selectedSubtopic || !state.selectedTier) return null;
    // Convert tier name to a format suitable for backend
    const tierLevel = state.selectedTier.toLowerCase();
    return `${state.selectedSubtopic}_${tierLevel}`;
  }, [state.selectedSubtopic, state.selectedTier]);

  return {
    // State
    state,
    currentStep: state.step,
    stepName: getCurrentStepName(),
    birthDetails: state.birthDetails,
    selectedTopic: state.selectedTopic,
    selectedSubtopic: state.selectedSubtopic,
    selectedTier: state.selectedTier,
    trustAcknowledged: state.trustAcknowledged,
    isOnboardingComplete,
    
    // Navigation
    goToStep,
    nextStep,
    prevStep,
    canAccessStep,
    
    // Actions
    setBirthDetails,
    skipBirthTime,
    selectTopic,
    selectSubtopic,
    selectTier,
    acknowledgeTrust,
    completeCheckout,
    completeOnboarding,
    resetState,
    
    // Helpers
    getTierIdForCheckout,
    
    // Constants
    STEPS: ONBOARDING_STEPS,
    STEP_NAMES
  };
}

export default useOnboardingState;
