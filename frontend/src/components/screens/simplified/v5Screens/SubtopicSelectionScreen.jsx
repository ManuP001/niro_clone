/**
 * NIRO V5 Sub-Topic Selection Screen
 * Step 4 in the 8-step onboarding flow
 * User selects from 6 sub-topics within their chosen topic
 */

import React from 'react';
import { colors, shadows } from '../theme';
import { V5_TOPICS, getLandingPageContent } from '../v5Data/landingPageContent';

// Get icon for subtopic
const getSubtopicIcon = (slug) => {
  const icons = {
    // Love
    'relationship-healing': (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
      </svg>
    ),
    'family-relationships': (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
      </svg>
    ),
    'dating-compatibility': (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.828 14.828a4 4 0 01-5.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    ),
    'marriage-planning': (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    ),
    'communication-trust': (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
      </svg>
    ),
    'breakup-closure': (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
      </svg>
    ),
    // Career
    'career-clarity': (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
      </svg>
    ),
    'job-transition': (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
      </svg>
    ),
    'money-stability': (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    ),
    'work-stress': (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M12 12h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    ),
    'office-politics': (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" />
      </svg>
    ),
    'big-decision-timing': (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    ),
    // Health
    'healing-journey': (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
      </svg>
    ),
    'stress-management': (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.828 14.828a4 4 0 01-5.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    ),
    'energy-balance': (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
      </svg>
    ),
    'sleep-reset': (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
      </svg>
    ),
    'emotional-recovery': (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
      </svg>
    ),
    'womens-wellness': (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
      </svg>
    ),
  };
  return icons[slug] || icons['career-clarity'];
};

// Subtopic card component
const SubtopicCard = ({ subtopic, content, isSelected, onSelect }) => {
  const startingPrice = content?.tierCards?.Focussed?.priceInr;
  
  return (
    <button
      onClick={() => onSelect(subtopic.slug)}
      className="w-full p-4 rounded-xl text-left transition-all active:scale-[0.98]"
      style={{
        background: isSelected 
          ? `linear-gradient(135deg, ${colors.teal.primary}15 0%, ${colors.gold.primary}20 100%)`
          : colors.background.card,
        border: `2px solid ${isSelected ? colors.gold.primary : colors.ui.borderDark}`,
        boxShadow: isSelected ? shadows.sm : 'none'
      }}
      data-testid={`subtopic-card-${subtopic.slug}`}
    >
      <div className="flex items-start gap-3">
        {/* Icon */}
        <div 
          className="w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0"
          style={{ 
            background: isSelected 
              ? `linear-gradient(135deg, ${colors.gold.primary} 0%, ${colors.gold.light} 100%)`
              : `${colors.teal.primary}10`,
            color: isSelected ? colors.teal.dark : colors.teal.primary
          }}
        >
          {getSubtopicIcon(subtopic.slug)}
        </div>
        
        {/* Content */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-0.5">
            <h3 
              className="text-sm font-semibold truncate"
              style={{ color: colors.text.dark }}
            >
              {subtopic.label}
            </h3>
            {isSelected && (
              <span 
                className="w-4 h-4 rounded-full flex items-center justify-center text-[10px] flex-shrink-0"
                style={{ background: colors.ui.success, color: 'white' }}
              >
                ✓
              </span>
            )}
          </div>
          
          {/* Short description from pain points */}
          {content?.painPoints?.[0] && (
            <p 
              className="text-xs line-clamp-2"
              style={{ color: colors.text.secondary }}
            >
              {content.painPoints[0]}
            </p>
          )}
          
          {/* Starting price */}
          {startingPrice && (
            <p 
              className="text-xs mt-1 font-medium"
              style={{ color: colors.teal.primary }}
            >
              Starting ₹{startingPrice.toLocaleString('en-IN')}
            </p>
          )}
        </div>
      </div>
    </button>
  );
};

export default function SubtopicSelectionScreen({ 
  selectedTopic, 
  selectedSubtopic, 
  onSelectSubtopic, 
  onContinue, 
  onBack 
}) {
  // Get topic data
  const topic = V5_TOPICS.find(t => t.id === selectedTopic);
  const subtopics = topic?.subtopics || [];

  return (
    <div 
      className="min-h-screen flex flex-col"
      style={{ background: colors.background.gradient }}
    >
      {/* Header */}
      <div className="px-5 pt-12 pb-4">
        <button 
          onClick={onBack}
          className="flex items-center gap-2 text-sm font-medium mb-6 transition-opacity hover:opacity-70"
          style={{ color: colors.gold.primary }}
          data-testid="subtopic-back-btn"
        >
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          Back
        </button>
        
        {/* Topic badge */}
        <div 
          className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium mb-3"
          style={{ 
            background: `${colors.gold.primary}20`,
            color: colors.gold.primary
          }}
        >
          {topic?.label}
        </div>
        
        <h1 
          className="text-2xl font-bold mb-2"
          style={{ color: colors.text.primary }}
        >
          What specifically?
        </h1>
        <p 
          className="text-sm"
          style={{ color: colors.text.muted }}
        >
          Choose the area that best matches your situation
        </p>
      </div>

      {/* Subtopic Cards */}
      <div 
        className="flex-1 px-5 pb-safe overflow-y-auto"
        style={{ paddingBottom: 'calc(env(safe-area-inset-bottom) + 100px)' }}
      >
        <div className="grid grid-cols-1 gap-3">
          {subtopics.map((subtopic) => {
            const content = getLandingPageContent(subtopic.slug);
            return (
              <SubtopicCard
                key={subtopic.slug}
                subtopic={subtopic}
                content={content}
                isSelected={selectedSubtopic === subtopic.slug}
                onSelect={onSelectSubtopic}
              />
            );
          })}
        </div>
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
          disabled={!selectedSubtopic}
          className="w-full py-4 rounded-xl font-semibold text-base transition-all active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed"
          style={{
            background: selectedSubtopic ? colors.gold.primary : `${colors.gold.primary}80`,
            color: colors.text.dark,
            boxShadow: selectedSubtopic ? shadows.md : 'none'
          }}
          data-testid="subtopic-continue-btn"
        >
          Continue
        </button>
      </div>
    </div>
  );
}
