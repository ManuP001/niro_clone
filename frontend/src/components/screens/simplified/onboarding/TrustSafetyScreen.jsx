import React from 'react';
import { colors, shadows } from '../theme';
import { ShieldIcon, CheckIcon, LockIcon, ArrowRightIcon } from '../icons';

/**
 * TrustSafetyScreen - Onboarding Step 3
 * Trust indicators + Privacy assurance
 * Updated with teal-gold color scheme
 */
export default function TrustSafetyScreen({ onComplete, onBack }) {
  const trustPoints = [
    {
      icon: ShieldIcon,
      title: '100% Verified Experts',
      description: 'Every astrologer is background verified',
    },
    {
      icon: LockIcon,
      title: 'Your Privacy Protected',
      description: 'All conversations are encrypted and secure',
    },
    {
      icon: CheckIcon,
      title: '100% Satisfaction Guaranteed',
      description: "Your satisfaction is our priority",
    },
  ];

  return (
    <div 
      className="fixed inset-0 flex flex-col px-6"
      style={{ 
        background: colors.background.gradient,
        paddingTop: 'env(safe-area-inset-top)',
        paddingBottom: 'env(safe-area-inset-bottom)',
      }}
    >
      {/* Back button */}
      <div className="pt-4">
        <button 
          onClick={onBack}
          className="text-sm font-medium"
          style={{ color: 'rgba(255,255,255,0.8)' }}
        >
          ← Back
        </button>
      </div>

      {/* Content */}
      <div className="flex-1 flex flex-col justify-center py-6">
        <h1 
          className="text-2xl font-bold mb-2 text-center"
          style={{ 
            fontFamily: "'Kumbh Sans', 'Inter', sans-serif",
            background: colors.logo.gradient,
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            backgroundClip: 'text',
          }}
        >
          Trust & Safety
        </h1>
        <p 
          className="text-center mb-8"
          style={{ color: 'rgba(255,255,255,0.8)' }}
        >
          Your peace of mind is our priority
        </p>
        
        {/* Trust cards */}
        <div className="space-y-4">
          {trustPoints.map((point, idx) => (
            <div 
              key={idx}
              className="flex items-start gap-4 p-4 rounded-xl"
              style={{ 
                backgroundColor: 'rgba(255,255,255,0.95)',
                boxShadow: shadows.sm,
              }}
            >
              <div 
                className="w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0"
                style={{ backgroundColor: `${colors.teal.primary}15` }}
              >
                <point.icon className="w-5 h-5" style={{ color: colors.teal.primary }} />
              </div>
              <div>
                <h3 className="font-semibold text-sm mb-0.5" style={{ color: colors.text.dark }}>
                  {point.title}
                </h3>
                <p className="text-xs" style={{ color: colors.text.secondary }}>
                  {point.description}
                </p>
              </div>
            </div>
          ))}
        </div>
        
        {/* 10K users badge */}
        <div className="mt-6 text-center">
          <p className="text-sm" style={{ color: 'rgba(255,255,255,0.9)' }}>
            Join <span className="font-semibold" style={{ color: colors.gold.primary }}>10,000+</span> users who found clarity
          </p>
        </div>
      </div>

      {/* CTA */}
      <div className="pb-8">
        <button
          onClick={onComplete}
          className="w-full py-4 rounded-xl font-semibold text-base transition-all flex items-center justify-center gap-2 active:scale-[0.98]"
          style={{ 
            backgroundColor: colors.gold.primary,
            color: colors.text.dark,
            boxShadow: shadows.md,
          }}
        >
          Start Exploring
          <ArrowRightIcon className="w-5 h-5" />
        </button>
      </div>
    </div>
  );
}
