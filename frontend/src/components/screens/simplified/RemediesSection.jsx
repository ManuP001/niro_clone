import React from 'react';
import { colors, shadows } from './theme';
import { GiftIcon, PlusIcon } from './icons';
import { formatPrice } from './tileData';

/**
 * RemediesSection - Paid add-ons display (horizontal slider)
 * Separate from tools - these are upsells
 */
export default function RemediesSection({ remedies, onAddRemedy }) {
  if (!remedies || remedies.length === 0) return null;

  return (
    <div 
      className="py-6"
      style={{ backgroundColor: `${colors.gold.primary}10` }}
    >
      <div className="px-5 mb-4 flex items-center gap-2">
        <GiftIcon className="w-5 h-5" style={{ color: colors.gold.dark }} />
        <div>
          <h3 className="text-lg font-semibold" style={{ color: colors.text.dark }}>
            Optional Remedies
          </h3>
          <p className="text-xs" style={{ color: colors.text.secondary }}>
            Paid add-ons to enhance your journey
          </p>
        </div>
      </div>
      
      <div className="flex overflow-x-auto gap-3 px-5 pb-2 scrollbar-hide">
        {remedies.map((remedy, idx) => (
          <div
            key={idx}
            className="flex-shrink-0 w-56 p-4 rounded-xl"
            style={{ 
              backgroundColor: colors.background.card,
              border: `1px solid ${colors.gold.primary}40`,
              boxShadow: shadows.sm,
            }}
          >
            {/* Icon */}
            <div 
              className="w-10 h-10 rounded-full flex items-center justify-center mb-3"
              style={{ backgroundColor: `${colors.gold.primary}20` }}
            >
              <GiftIcon className="w-5 h-5" style={{ color: colors.gold.dark }} />
            </div>
            
            {/* Content */}
            <h4 
              className="font-semibold text-sm mb-1"
              style={{ color: colors.text.dark }}
            >
              {remedy.name}
            </h4>
            <p 
              className="text-xs mb-3 line-clamp-2"
              style={{ color: colors.text.secondary }}
            >
              {remedy.description}
            </p>
            
            {/* Price & CTA */}
            <div className="flex items-center justify-between">
              <span 
                className="font-semibold text-sm"
                style={{ color: colors.text.dark }}
              >
                {formatPrice(remedy.price)}
              </span>
              <button
                onClick={() => onAddRemedy && onAddRemedy(remedy, idx)}
                className="flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs font-medium transition-all active:scale-[0.97]"
                style={{ 
                  backgroundColor: `${colors.gold.primary}20`,
                  color: colors.gold.dark,
                }}
              >
                <PlusIcon className="w-3.5 h-3.5" />
                Add
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
