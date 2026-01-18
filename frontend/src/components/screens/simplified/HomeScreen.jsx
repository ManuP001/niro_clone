import React, { useState, useEffect, useRef } from 'react';
import { colors, shadows } from './theme';
import { HOME_CATEGORIES } from './tileData';
import { ChevronRightIcon, SendIcon } from './icons';
import { trackEvent } from './utils';
import HeroSection from './HeroSection';
import TileCard from './TileCard';

/**
 * HomeScreen V5 - New design with hero section and horizontal tile carousels
 */
export default function HomeScreen({ 
  token, 
  userId, 
  userState, 
  userName, 
  hasBottomNav, 
  onNavigate, 
  onOpenProfile,
  onChatWithMira,
  onTalkToHuman,
}) {
  const [askInput, setAskInput] = useState('');

  useEffect(() => {
    trackEvent('home_viewed', { flow_version: 'v5' }, token);
  }, [token]);

  const handleTileClick = (tileId) => {
    trackEvent('tile_clicked', { tile_id: tileId }, token);
    onNavigate('topic', { topicId: tileId });
  };

  const handleViewAll = (categoryId) => {
    trackEvent('view_all_clicked', { category_id: categoryId }, token);
    onNavigate('categoryListing', { categoryId });
  };

  const handleAskMira = () => {
    if (askInput.trim()) {
      onNavigate('mira', { initialMessage: askInput.trim() });
    } else {
      onNavigate('mira', {});
    }
  };

  return (
    <div 
      className={`min-h-screen ${hasBottomNav ? 'pb-20' : ''}`}
      style={{ 
        background: colors.background.gradient,
      }}
    >
      {/* Hero Section */}
      <HeroSection 
        onChatWithMira={onChatWithMira}
        onTalkToHuman={onTalkToHuman}
      />

      {/* Categories Section */}
      <div 
        className="px-0 pt-6 pb-4 rounded-t-3xl -mt-4"
        style={{ backgroundColor: colors.background.card }}
      >
        {/* Section Header */}
        <div className="px-5 mb-4">
          <h2 
            className="text-lg font-semibold"
            style={{ color: colors.text.dark }}
          >
            Explore by topic
          </h2>
          <p 
            className="text-sm"
            style={{ color: colors.text.secondary }}
          >
            Choose a life area to get started
          </p>
        </div>

        {/* Category Carousels */}
        {HOME_CATEGORIES.map((category) => (
          <div key={category.id} className="mb-6">
            {/* Category Header with View All */}
            <div className="px-5 flex items-center justify-between mb-3">
              <h3 
                className="text-sm font-semibold"
                style={{ color: colors.text.dark }}
              >
                {category.title}
              </h3>
              <button
                onClick={() => handleViewAll(category.id)}
                className="flex items-center gap-1 text-xs font-medium transition-colors"
                style={{ color: colors.teal.primary }}
              >
                View all
                <ChevronRightIcon className="w-4 h-4" />
              </button>
            </div>
            
            {/* Horizontal Tile Carousel */}
            <div 
              className="flex overflow-x-auto gap-3 px-5 pb-2 scrollbar-hide"
              style={{ scrollbarWidth: 'none', msOverflowStyle: 'none' }}
            >
              {category.tiles.map((tile) => (
                <TileCard 
                  key={tile.id}
                  tile={tile}
                  onClick={handleTileClick}
                />
              ))}
            </div>
          </div>
        ))}

        {/* Extra scroll padding */}
        <div className="h-4" />
      </div>

      {/* Ask Mira Section - Fixed at bottom */}
      <div 
        className="fixed left-0 right-0 px-5 py-4 border-t z-40"
        style={{ 
          bottom: hasBottomNav ? '64px' : '0',
          backgroundColor: colors.background.card,
          borderColor: colors.ui.borderDark,
          paddingBottom: hasBottomNav ? '16px' : 'max(16px, env(safe-area-inset-bottom))',
        }}
      >
        <div 
          className="rounded-xl p-3 flex items-center"
          style={{ 
            backgroundColor: `${colors.teal.primary}08`,
            border: `1px solid ${colors.ui.borderDark}`,
          }}
        >
          <input
            type="text"
            value={askInput}
            onChange={(e) => setAskInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleAskMira()}
            placeholder="Ask Mira anything..."
            className="flex-1 bg-transparent text-sm focus:outline-none"
            style={{ color: colors.text.dark }}
          />
          <button
            onClick={handleAskMira}
            className="p-2 rounded-lg transition-all ml-2 active:scale-[0.95]"
            style={{ backgroundColor: colors.teal.primary }}
          >
            <SendIcon className="w-4 h-4" style={{ color: '#fff' }} />
          </button>
        </div>
        <p 
          className="text-center text-xs mt-2"
          style={{ color: colors.text.mutedDark }}
        >
          Free AI Chat with Mira
        </p>
      </div>
    </div>
  );
}
