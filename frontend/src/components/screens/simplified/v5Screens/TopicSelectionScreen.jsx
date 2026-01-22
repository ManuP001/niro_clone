/**
 * NIRO V5 Topic Selection Screen
 * Step 3 in the 8-step onboarding flow
 * User selects from 3 main topics: Love, Career, Health
 */

import React from 'react';
import { colors, shadows, borderRadius } from '../theme';
import { V5_TOPICS } from '../v5Data/landingPageContent';

// Topic card component
const TopicCard = ({ topic, isSelected, onSelect }) => {
  const getIcon = (iconType) => {
    switch (iconType) {
      case 'heart':
        return (
          <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
          </svg>
        );
      case 'briefcase':
        return (
          <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
          </svg>
        );
      case 'heart_pulse':
        return (
          <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12h4l3-9 4 18 3-9h4" />
          </svg>
        );
      default:
        return null;
    }
  };

  return (
    <button
      onClick={() => onSelect(topic.id)}
      className="w-full p-5 rounded-2xl text-left transition-all active:scale-[0.98]"
      style={{
        background: isSelected 
          ? `linear-gradient(135deg, ${colors.teal.primary}15 0%, ${colors.gold.primary}20 100%)`
          : colors.background.card,
        border: `2px solid ${isSelected ? colors.gold.primary : colors.ui.borderDark}`,
        boxShadow: isSelected ? shadows.md : shadows.sm
      }}
      data-testid={`topic-card-${topic.id}`}
    >
      <div className="flex items-start gap-4">
        {/* Icon */}
        <div 
          className="w-14 h-14 rounded-xl flex items-center justify-center flex-shrink-0"
          style={{ 
            background: isSelected 
              ? `linear-gradient(135deg, ${colors.gold.primary} 0%, ${colors.gold.light} 100%)`
              : `${colors.teal.primary}15`,
            color: isSelected ? colors.teal.dark : colors.teal.primary
          }}
        >
          {getIcon(topic.icon)}
        </div>
        
        {/* Content */}
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            <h3 
              className="text-lg font-bold"
              style={{ color: colors.text.dark }}
            >
              {topic.label}
            </h3>
            {isSelected && (
              <span 
                className="w-5 h-5 rounded-full flex items-center justify-center text-xs"
                style={{ background: colors.ui.success, color: 'white' }}
              >
                ✓
              </span>
            )}
          </div>
          <p 
            className="text-sm mb-3"
            style={{ color: colors.text.secondary }}
          >
            {topic.tagline}
          </p>
          
          {/* Subtopics preview */}
          <div className="flex flex-wrap gap-1.5">
            {topic.subtopics.slice(0, 3).map((sub, idx) => (
              <span 
                key={idx}
                className="text-xs px-2 py-1 rounded-full"
                style={{ 
                  background: `${colors.teal.primary}10`,
                  color: colors.teal.primary
                }}
              >
                {sub.label}
              </span>
            ))}
            {topic.subtopics.length > 3 && (
              <span 
                className="text-xs px-2 py-1 rounded-full"
                style={{ 
                  background: `${colors.gold.primary}20`,
                  color: colors.text.secondary
                }}
              >
                +{topic.subtopics.length - 3} more
              </span>
            )}
          </div>
        </div>
      </div>
    </button>
  );
};

export default function TopicSelectionScreen({ 
  selectedTopic, 
  onSelectTopic, 
  onContinue, 
  onBack 
}) {
  return (
    <div 
      className="min-h-screen flex flex-col"
      style={{ background: colors.background.gradient }}
    >
      {/* Header */}
      <div className="px-5 pt-12 pb-6">
        <button 
          onClick={onBack}
          className="flex items-center gap-2 text-sm font-medium mb-6 transition-opacity hover:opacity-70"
          style={{ color: colors.gold.primary }}
          data-testid="topic-back-btn"
        >
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          Back
        </button>
        
        <h1 
          className="text-2xl font-bold mb-2"
          style={{ color: colors.text.primary }}
        >
          What brings you here?
        </h1>
        <p 
          className="text-sm"
          style={{ color: colors.text.muted }}
        >
          Choose the area where you need guidance
        </p>
      </div>

      {/* Topic Cards */}
      <div 
        className="flex-1 px-5 pb-safe space-y-4"
        style={{ paddingBottom: 'calc(env(safe-area-inset-bottom) + 100px)' }}
      >
        {V5_TOPICS.map((topic) => (
          <TopicCard
            key={topic.id}
            topic={topic}
            isSelected={selectedTopic === topic.id}
            onSelect={onSelectTopic}
          />
        ))}
      </div>

      {/* Fixed CTA */}
      <div 
        className="fixed bottom-0 left-0 right-0 p-5 border-t"
        style={{ 
          background: `linear-gradient(to top, ${colors.teal.dark} 0%, ${colors.teal.primary} 100%)`,
          borderColor: colors.ui.border,
          paddingBottom: 'calc(env(safe-area-inset-bottom) + 20px)'
        }}
      >
        <button
          onClick={onContinue}
          disabled={!selectedTopic}
          className="w-full py-4 rounded-xl font-semibold text-base transition-all active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed"
          style={{
            background: selectedTopic ? colors.gold.primary : `${colors.gold.primary}80`,
            color: colors.text.dark,
            boxShadow: selectedTopic ? shadows.md : 'none'
          }}
          data-testid="topic-continue-btn"
        >
          Continue
        </button>
      </div>
    </div>
  );
}
