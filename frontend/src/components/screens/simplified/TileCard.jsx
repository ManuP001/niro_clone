import React from 'react';
import { colors, shadows, borderRadius } from './theme';
import { getTileIcon } from './icons';

/**
 * TileCard - Reusable tile with unique icon and text overflow handling
 * Max 2 lines with ellipsis, uses shortTitle if available
 */
export default function TileCard({ tile, onClick, size = 'normal' }) {
  // Use shortTitle if title is too long
  const displayTitle = tile.shortTitle || tile.title;
  
  const sizeStyles = {
    normal: {
      height: 'h-24',
      iconSize: 'w-8 h-8',
      iconWrapper: 'w-12 h-12',
      fontSize: 'text-xs',
      padding: 'p-3',
    },
    large: {
      height: 'h-28',
      iconSize: 'w-10 h-10',
      iconWrapper: 'w-14 h-14',
      fontSize: 'text-sm',
      padding: 'p-4',
    },
  };
  
  const s = sizeStyles[size];

  return (
    <button
      onClick={() => onClick(tile.id)}
      data-testid={`tile-${tile.id}`}
      className={`flex-shrink-0 w-28 ${s.height} rounded-xl ${s.padding} flex flex-col items-center justify-center text-center transition-all active:scale-[0.97] hover:shadow-md`}
      style={{ 
        backgroundColor: colors.background.card,
        boxShadow: shadows.sm,
      }}
    >
      {/* Icon */}
      <div 
        className={`${s.iconWrapper} rounded-full flex items-center justify-center mb-2`}
        style={{ backgroundColor: `${colors.teal.primary}15` }}
      >
        <span style={{ color: colors.teal.primary }}>
          {getTileIcon(tile.iconType, s.iconSize)}
        </span>
      </div>
      
      {/* Title - max 2 lines with ellipsis */}
      <p 
        className={`${s.fontSize} font-medium leading-tight line-clamp-2`}
        style={{ 
          color: colors.text.dark,
          display: '-webkit-box',
          WebkitLineClamp: 2,
          WebkitBoxOrient: 'vertical',
          overflow: 'hidden',
        }}
      >
        {displayTitle}
      </p>
    </button>
  );
}
