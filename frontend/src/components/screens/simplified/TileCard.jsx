import React from 'react';
import { colors, shadows, borderRadius } from './theme';
import { getTileIcon } from './icons';

/**
 * TileCard V2 - Refined tile with teal/cream theme
 * Max 2 lines with ellipsis, uses shortTitle if available
 */
export default function TileCard({ tile, onClick, size = 'normal' }) {
  // Use shortTitle if title is too long
  const displayTitle = tile.shortTitle || tile.title;
  
  const sizeStyles = {
    normal: {
      height: 'h-24 md:h-28',
      iconSize: 'w-8 h-8 md:w-9 md:h-9',
      iconWrapper: 'w-12 h-12 md:w-14 md:h-14',
      fontSize: 'text-xs md:text-sm',
      padding: 'p-3 md:p-4',
      width: 'w-28 md:w-32',
    },
    large: {
      height: 'h-28 md:h-32',
      iconSize: 'w-10 h-10 md:w-11 md:h-11',
      iconWrapper: 'w-14 h-14 md:w-16 md:h-16',
      fontSize: 'text-sm md:text-base',
      padding: 'p-4 md:p-5',
      width: 'w-32 md:w-36',
    },
  };
  
  const s = sizeStyles[size];

  return (
    <button
      onClick={() => onClick(tile.id)}
      data-testid={`tile-${tile.id}`}
      className={`flex-shrink-0 ${s.width} ${s.height} rounded-xl ${s.padding} flex flex-col items-center justify-center text-center transition-all active:scale-[0.97] hover:shadow-lg hover:-translate-y-0.5`}
      style={{ 
        backgroundColor: '#FFFFFF',
        boxShadow: shadows.sm,
        border: `1px solid ${colors.ui.borderDark}`,
      }}
    >
      {/* Icon */}
      <div 
        className={`${s.iconWrapper} rounded-full flex items-center justify-center mb-2`}
        style={{ backgroundColor: `${colors.teal.primary}12` }}
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
