import React, { useState, useEffect } from 'react';
import { colors, shadows } from '../theme';
import { SparklesIcon, ChevronRightIcon, CloseIcon } from '../icons';

/**
 * HomeTourOverlay - Quick tour after onboarding
 * Shows key features on home screen
 * Updated with teal-gold color scheme
 */
export default function HomeTourOverlay({ onComplete }) {
  const [currentStep, setCurrentStep] = useState(0);
  
  const steps = [
    {
      title: 'Chat with Mira',
      description: 'Ask anything to your AI astrologer. She\'s available 24/7.',
      highlight: 'mira-cta',
      position: 'bottom',
    },
    {
      title: 'Talk to Experts',
      description: 'Book sessions with verified human astrologers for deeper guidance.',
      highlight: 'expert-cta',
      position: 'bottom',
    },
    {
      title: 'Browse Topics',
      description: 'Explore specialized guidance for relationships, career, health and more.',
      highlight: 'topics',
      position: 'top',
    },
  ];

  const handleNext = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      onComplete();
    }
  };

  const handleSkip = () => {
    onComplete();
  };

  return (
    <div className="fixed inset-0 z-50">
      {/* Backdrop */}
      <div 
        className="absolute inset-0"
        style={{ backgroundColor: 'rgba(0,0,0,0.6)' }}
        onClick={handleSkip}
      />
      
      {/* Tooltip */}
      <div 
        className={`absolute left-4 right-4 p-4 rounded-xl ${steps[currentStep].position === 'top' ? 'top-32' : 'bottom-36'}`}
        style={{ 
          backgroundColor: '#ffffff',
          boxShadow: shadows.lg,
        }}
      >
        {/* Arrow */}
        <div 
          className={`absolute w-4 h-4 rotate-45 ${steps[currentStep].position === 'top' ? '-bottom-2' : '-top-2'} left-1/2 -translate-x-1/2`}
          style={{ backgroundColor: '#ffffff' }}
        />
        
        {/* Content */}
        <div className="relative">
          {/* Close button */}
          <button 
            onClick={handleSkip}
            className="absolute -top-1 -right-1 p-1"
          >
            <CloseIcon className="w-5 h-5" style={{ color: colors.text.mutedDark }} />
          </button>
          
          <div className="flex items-start gap-3">
            <div 
              className="w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0"
              style={{ backgroundColor: `${colors.teal.primary}15` }}
            >
              <SparklesIcon className="w-5 h-5" style={{ color: colors.teal.primary }} />
            </div>
            <div className="flex-1">
              <h3 className="font-semibold mb-1" style={{ color: colors.text.dark }}>
                {steps[currentStep].title}
              </h3>
              <p className="text-sm mb-4" style={{ color: colors.text.secondary }}>
                {steps[currentStep].description}
              </p>
              
              {/* Progress & Actions */}
              <div className="flex items-center justify-between">
                <div className="flex gap-1">
                  {steps.map((_, idx) => (
                    <div 
                      key={idx}
                      className="w-2 h-2 rounded-full"
                      style={{ 
                        backgroundColor: idx === currentStep ? colors.teal.primary : colors.ui.borderDark,
                      }}
                    />
                  ))}
                </div>
                <button
                  onClick={handleNext}
                  className="flex items-center gap-1 px-4 py-2 rounded-lg font-medium text-sm"
                  style={{ backgroundColor: colors.gold.primary, color: colors.text.dark }}
                >
                  {currentStep < steps.length - 1 ? 'Next' : 'Got it!'}
                  <ChevronRightIcon className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
