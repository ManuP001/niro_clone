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
      title: 'Start with one life topic',
      description: 'Choose what's most uncertain right now.',
    },
    {
      icon: UsersIcon,
      title: 'Talk to verified experts',
      description: 'Vedic-first guidance, with follow-ups until clarity.',
    },
    {
      icon: CalendarIcon,
      title: 'Get timing + direction',
      description: 'Understand what phase you're in — and what's next.',
    },
    {
      icon: ChatIcon,
      title: 'Unlimited support (on higher tiers)',
      description: 'Unlimited chat + follow-ups during your journey.',
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
          How Niro helps
        </h1>
        <p 
          className="text-center mb-8"
          style={{ color: 'rgba(255,255,255,0.8)' }}
        >
          Get clarity, timing, and next steps — with real experts.
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
