/**
 * NIRO V5 Home Screen
 * Step 8 (final) in the onboarding flow - Post-purchase dashboard
 * Shows 3 topic categories with horizontally-scrolling sub-topic rows
 */

import React, { useState } from 'react';
import { colors, shadows } from '../theme';
import { V5_TOPICS, getLandingPageContent, formatPriceInr } from '../v5Data/landingPageContent';

// ==========================================
// HERO SECTION
// ==========================================
const HeroSection = ({ userName }) => (
  <div 
    className="px-5 pt-12 pb-8"
    style={{ background: colors.background.gradient }}
  >
    {/* Logo/Brand */}
    <div className="flex items-center justify-between mb-8">
      <h1 
        className="text-2xl font-bold"
        style={{ 
          background: colors.logo.gradient,
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          backgroundClip: 'text',
        }}
      >
        NIRO
      </h1>
      <button 
        className="w-10 h-10 rounded-full flex items-center justify-center"
        style={{ background: 'rgba(255,255,255,0.15)' }}
        data-testid="home-profile-btn"
      >
        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke={colors.text.primary}>
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
        </svg>
      </button>
    </div>

    {/* Welcome message */}
    <div className="mb-6">
      <p 
        className="text-sm mb-1"
        style={{ color: colors.text.muted }}
      >
        Welcome back,
      </p>
      <h2 
        className="text-xl font-bold"
        style={{ color: colors.text.primary }}
      >
        {userName || 'User'}
      </h2>
    </div>

    {/* AI chat prompt card */}
    <div 
      className="p-4 rounded-2xl"
      style={{ 
        background: 'rgba(255,255,255,0.95)',
        boxShadow: shadows.md
      }}
    >
      <div className="flex items-center gap-3 mb-3">
        <div 
          className="w-10 h-10 rounded-full flex items-center justify-center"
          style={{ background: `linear-gradient(135deg, ${colors.gold.primary} 0%, ${colors.gold.light} 100%)` }}
        >
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke={colors.teal.dark}>
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
          </svg>
        </div>
        <div>
          <p 
            className="text-sm font-semibold"
            style={{ color: colors.text.dark }}
          >
            Ask Mira
          </p>
          <p 
            className="text-xs"
            style={{ color: colors.text.secondary }}
          >
            Your AI astrology assistant
          </p>
        </div>
      </div>
      <button 
        className="w-full p-3 rounded-xl text-left text-sm flex items-center gap-2"
        style={{ 
          background: `${colors.teal.primary}08`,
          color: colors.text.secondary
        }}
        data-testid="home-ask-mira-btn"
      >
        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
        What&apos;s on your mind today?
      </button>
    </div>
  </div>
);

// ==========================================
// SUBTOPIC TILE COMPONENT
// ==========================================
const SubtopicTile = ({ subtopic, onSelect }) => {
  const content = getLandingPageContent(subtopic.slug);
  const startingPrice = content?.tierCards?.Focussed?.priceInr;

  return (
    <button
      onClick={() => onSelect(subtopic.slug)}
      className="flex-shrink-0 w-44 p-4 rounded-xl text-left transition-all active:scale-[0.98]"
      style={{ 
        background: colors.background.card,
        boxShadow: shadows.sm
      }}
      data-testid={`home-tile-${subtopic.slug}`}
    >
      <h4 
        className="text-sm font-semibold mb-1 line-clamp-2"
        style={{ color: colors.text.dark }}
      >
        {subtopic.label}
      </h4>
      <p 
        className="text-xs mb-3 line-clamp-2"
        style={{ color: colors.text.secondary }}
      >
        {content?.painPoints?.[0]?.substring(0, 50)}...
      </p>
      {startingPrice && (
        <p 
          className="text-xs font-medium"
          style={{ color: colors.teal.primary }}
        >
          From {formatPriceInr(startingPrice)}
        </p>
      )}
    </button>
  );
};

// ==========================================
// TOPIC ROW COMPONENT
// ==========================================
const TopicRow = ({ topic, onSelectSubtopic }) => {
  const getTopicIcon = (iconType) => {
    switch (iconType) {
      case 'heart':
        return (
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
          </svg>
        );
      case 'briefcase':
        return (
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
          </svg>
        );
      case 'heart_pulse':
        return (
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
          </svg>
        );
      default:
        return null;
    }
  };

  return (
    <div className="mb-8">
      {/* Topic header */}
      <div className="flex items-center justify-between px-5 mb-3">
        <div className="flex items-center gap-2">
          <div 
            className="w-8 h-8 rounded-lg flex items-center justify-center"
            style={{ 
              background: `${colors.teal.primary}15`,
              color: colors.teal.primary
            }}
          >
            {getTopicIcon(topic.icon)}
          </div>
          <div>
            <h3 
              className="text-base font-bold"
              style={{ color: colors.text.dark }}
            >
              {topic.label}
            </h3>
            <p 
              className="text-xs"
              style={{ color: colors.text.secondary }}
            >
              {topic.tagline}
            </p>
          </div>
        </div>
        <button 
          className="text-xs font-medium"
          style={{ color: colors.teal.primary }}
        >
          See all
        </button>
      </div>

      {/* Horizontal scroll of subtopics */}
      <div 
        className="flex gap-3 overflow-x-auto px-5 pb-2 scrollbar-hide"
        style={{ scrollbarWidth: 'none' }}
      >
        {topic.subtopics.map((subtopic) => (
          <SubtopicTile 
            key={subtopic.slug}
            subtopic={subtopic}
            onSelect={onSelectSubtopic}
          />
        ))}
      </div>
    </div>
  );
};

// ==========================================
// MAIN HOME SCREEN COMPONENT
// ==========================================
export default function HomeScreenV5({ 
  userName,
  onSelectSubtopic,
  onNavigateToChat
}) {
  return (
    <div 
      className="min-h-screen"
      style={{ background: colors.background.card }}
    >
      {/* Hero section with teal gradient */}
      <HeroSection userName={userName} />

      {/* Main content area */}
      <div className="pt-6 pb-20">
        {/* Section header */}
        <div className="px-5 mb-6">
          <h2 
            className="text-lg font-bold mb-1"
            style={{ color: colors.text.dark }}
          >
            Explore Services
          </h2>
          <p 
            className="text-sm"
            style={{ color: colors.text.secondary }}
          >
            Get expert guidance in any area of life
          </p>
        </div>

        {/* Topic rows with horizontal scrolling subtopics */}
        {V5_TOPICS.map((topic) => (
          <TopicRow 
            key={topic.id}
            topic={topic}
            onSelectSubtopic={onSelectSubtopic}
          />
        ))}

        {/* Quick links */}
        <div className="px-5 mt-8">
          <div 
            className="p-4 rounded-xl"
            style={{ background: `${colors.teal.primary}08` }}
          >
            <h4 
              className="text-sm font-semibold mb-3"
              style={{ color: colors.text.dark }}
            >
              Quick Actions
            </h4>
            <div className="grid grid-cols-2 gap-3">
              <button 
                className="p-3 rounded-lg text-left text-sm flex items-center gap-2"
                style={{ background: colors.background.card }}
              >
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke={colors.teal.primary}>
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
                <span style={{ color: colors.text.dark }}>My Sessions</span>
              </button>
              <button 
                className="p-3 rounded-lg text-left text-sm flex items-center gap-2"
                style={{ background: colors.background.card }}
              >
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke={colors.teal.primary}>
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
                <span style={{ color: colors.text.dark }}>My Orders</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
