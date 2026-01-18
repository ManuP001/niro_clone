import React from 'react';
import { colors, shadows } from './theme';
import { HOME_CATEGORIES, getTilesByCategory } from './tileData';
import { ArrowLeftIcon, ChevronRightIcon, getTileIcon } from './icons';
import TileCard from './TileCard';

/**
 * CategoryListingPage - Shows all tiles for a category or all categories
 * Used for "View all" links and "Talk to human astrologer" CTA
 */
export default function CategoryListingPage({ 
  categoryId = null, // null = show all categories
  onBack, 
  onTileClick,
  showAllCategories = false,
  title = 'Browse Topics'
}) {
  const categories = showAllCategories || !categoryId 
    ? HOME_CATEGORIES 
    : [HOME_CATEGORIES.find(c => c.id === categoryId)].filter(Boolean);

  return (
    <div 
      className="min-h-screen"
      style={{ 
        background: colors.background.gradient,
        paddingTop: 'env(safe-area-inset-top)',
        paddingBottom: 'env(safe-area-inset-bottom)',
      }}
    >
      {/* Header */}
      <div className="px-5 pt-4 pb-6">
        <button 
          onClick={onBack}
          className="flex items-center gap-2 mb-4 transition-colors"
          style={{ color: colors.text.primary }}
        >
          <ArrowLeftIcon className="w-5 h-5" />
          <span className="font-medium">Back</span>
        </button>
        
        <h1 
          className="text-2xl font-bold"
          style={{ color: colors.text.primary }}
        >
          {title}
        </h1>
        {showAllCategories && (
          <p 
            className="text-sm mt-1"
            style={{ color: colors.text.muted }}
          >
            Choose a topic to get started with an expert
          </p>
        )}
      </div>

      {/* Categories & Tiles */}
      <div 
        className="px-5 pb-8 rounded-t-3xl min-h-[60vh]"
        style={{ backgroundColor: colors.background.card }}
      >
        <div className="pt-6">
          {categories.map((category) => (
            <div key={category.id} className="mb-8">
              {/* Category Header */}
              <h2 
                className="text-lg font-semibold mb-4 flex items-center gap-2"
                style={{ color: colors.text.dark }}
              >
                <span 
                  className="w-8 h-8 rounded-full flex items-center justify-center"
                  style={{ backgroundColor: `${colors.teal.primary}15` }}
                >
                  {getTileIcon(category.tiles[0]?.iconType || 'star', 'w-4 h-4')}
                </span>
                {category.title}
              </h2>
              
              {/* Tiles Grid */}
              <div className="grid grid-cols-1 gap-3">
                {category.tiles.map((tile) => (
                  <button
                    key={tile.id}
                    onClick={() => onTileClick(tile.id)}
                    className="flex items-center gap-4 p-4 rounded-xl text-left transition-all active:scale-[0.99] hover:shadow-md"
                    style={{ 
                      backgroundColor: `${colors.teal.primary}05`,
                      border: `1px solid ${colors.ui.borderDark}`,
                    }}
                  >
                    {/* Icon */}
                    <div 
                      className="w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0"
                      style={{ backgroundColor: `${colors.teal.primary}15` }}
                    >
                      <span style={{ color: colors.teal.primary }}>
                        {getTileIcon(tile.iconType, 'w-6 h-6')}
                      </span>
                    </div>
                    
                    {/* Content */}
                    <div className="flex-1 min-w-0">
                      <p 
                        className="font-semibold text-sm mb-0.5"
                        style={{ color: colors.text.dark }}
                      >
                        {tile.title}
                      </p>
                      <p 
                        className="text-xs line-clamp-1"
                        style={{ color: colors.text.secondary }}
                      >
                        {tile.outcomeStatement}
                      </p>
                    </div>
                    
                    {/* Arrow */}
                    <ChevronRightIcon 
                      className="w-5 h-5 flex-shrink-0" 
                      style={{ color: colors.text.mutedDark }} 
                    />
                  </button>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
