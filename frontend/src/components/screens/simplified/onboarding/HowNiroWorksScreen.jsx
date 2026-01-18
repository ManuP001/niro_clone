import React from 'react';
import { colors, shadows } from '../theme';
import { SparklesIcon, CalendarIcon, UsersIcon, ChatIcon, ArrowRightIcon } from '../icons';

/**
 * HowNiroWorksScreen - Onboarding Step 2
 * 4 value props with icons
 * Updated with teal-gold color scheme
 */
export default function HowNiroWorksScreen({ onNext, onBack }) {
  const features = [
    {
      icon: SparklesIcon,
      title: 'AI-Powered Insights',
      description: 'Get personalized guidance from Mira, our AI astrologer',
    },
    {
      icon: UsersIcon,
      title: 'Expert Astrologers',
      description: 'Connect with verified Vedic astrologers anytime',
    },
    {
      icon: CalendarIcon,
      title: 'Timing Guidance',
      description: 'Know the best times for important decisions',
    },
    {
      icon: ChatIcon,
      title: 'Unlimited Support',
      description: '24/7 chat access with your dedicated expert',
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
          How Niro Works
        </h1>
        <p 
          className="text-center mb-8"
          style={{ color: 'rgba(255,255,255,0.8)' }}
        >
          Your personal astrology companion
        </p>
        
        {/* Feature cards */}
        <div className="space-y-3">
          {features.map((feature, idx) => (
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
                <feature.icon className="w-5 h-5" style={{ color: colors.teal.primary }} />
              </div>
              <div>
                <h3 className="font-semibold text-sm mb-0.5" style={{ color: colors.text.dark }}>
                  {feature.title}
                </h3>
                <p className="text-xs" style={{ color: colors.text.secondary }}>
                  {feature.description}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* CTA */}
      <div className="pb-8">
        <button
          onClick={onNext}
          className="w-full py-4 rounded-xl font-semibold text-base transition-all flex items-center justify-center gap-2 active:scale-[0.98]"
          style={{ 
            backgroundColor: colors.gold.primary,
            color: colors.text.dark,
            boxShadow: shadows.md,
          }}
        >
          Continue
          <ArrowRightIcon className="w-5 h-5" />
        </button>
      </div>
    </div>
  );
}
