import React from 'react';
import { colors, shadows } from './theme';
import { ToolIcon, LockIcon, UnlockIcon, ChevronRightIcon } from './icons';

/**
 * ToolsSection - Included tools display (3 horizontal cards)
 * Shows lock badge before purchase
 */
export default function ToolsSection({ tools, isPurchased = false, onToolClick }) {
  if (!tools || tools.length === 0) return null;

  return (
    <div className="py-6">
      <div className="px-5 mb-4 flex items-center gap-2">
        <ToolIcon className="w-5 h-5" style={{ color: colors.teal.primary }} />
        <h3 className="text-lg font-semibold" style={{ color: colors.text.dark }}>
          Included Tools
        </h3>
      </div>
      
      <div className="flex overflow-x-auto gap-3 px-5 pb-2 scrollbar-hide">
        {tools.map((tool, idx) => (
          <div
            key={idx}
            className="flex-shrink-0 w-64 p-4 rounded-xl"
            style={{ 
              backgroundColor: colors.background.card,
              border: `1px solid ${colors.ui.borderDark}`,
              boxShadow: shadows.sm,
            }}
          >
            {/* Header with lock status */}
            <div className="flex items-start justify-between mb-2">
              <div 
                className="w-10 h-10 rounded-full flex items-center justify-center"
                style={{ backgroundColor: `${colors.teal.primary}15` }}
              >
                <ToolIcon className="w-5 h-5" style={{ color: colors.teal.primary }} />
              </div>
              {!isPurchased && (
                <div 
                  className="flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium"
                  style={{ 
                    backgroundColor: `${colors.gold.primary}20`,
                    color: colors.gold.dark,
                  }}
                >
                  <LockIcon className="w-3 h-3" />
                  Unlock
                </div>
              )}
            </div>
            
            {/* Content */}
            <h4 
              className="font-semibold text-sm mb-1"
              style={{ color: colors.text.dark }}
            >
              {tool.name}
            </h4>
            <p 
              className="text-xs mb-3 line-clamp-2"
              style={{ color: colors.text.secondary }}
            >
              {tool.description}
            </p>
            
            {/* CTA */}
            <button
              onClick={() => onToolClick && onToolClick(tool, idx)}
              className="flex items-center gap-1 text-sm font-medium transition-colors"
              style={{ color: colors.teal.primary }}
              disabled={!isPurchased}
            >
              {isPurchased ? (
                <>
                  {tool.cta || 'Open'}
                  <ChevronRightIcon className="w-4 h-4" />
                </>
              ) : (
                <>
                  <LockIcon className="w-4 h-4" />
                  Buy pack to unlock
                </>
              )}
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
