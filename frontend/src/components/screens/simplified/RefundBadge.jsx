import React from 'react';
import { colors } from './theme';
import { ShieldIcon } from './icons';

/**
 * RefundBadge - Trust block showing satisfaction guarantee
 */
export default function RefundBadge({ variant = 'default' }) {
  const styles = {
    default: {
      background: `${colors.teal.primary}10`,
      border: `1px solid ${colors.teal.primary}30`,
      color: colors.teal.primary,
      iconColor: colors.teal.primary,
    },
    dark: {
      background: 'rgba(255,255,255,0.1)',
      border: `1px solid rgba(255,255,255,0.2)`,
      color: colors.text.primary,
      iconColor: colors.gold.primary,
    },
    card: {
      background: colors.background.card,
      border: `1px solid ${colors.ui.borderDark}`,
      color: colors.text.dark,
      iconColor: colors.teal.primary,
    },
  };

  const s = styles[variant];

  return (
    <div 
      className="flex items-center gap-3 px-4 py-3 rounded-xl"
      style={{ 
        backgroundColor: s.background,
        border: s.border,
      }}
    >
      <div 
        className="w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0"
        style={{ backgroundColor: `${s.iconColor}15` }}
      >
        <ShieldIcon className="w-5 h-5" style={{ color: s.iconColor }} />
      </div>
      <div>
        <p 
          className="font-semibold text-sm"
          style={{ color: s.color }}
        >
          No questions asked
        </p>
        <p 
          className="text-xs"
          style={{ color: variant === 'dark' ? colors.text.muted : colors.text.secondary }}
        >
          100% satisfaction guaranteed
        </p>
      </div>
    </div>
  );
}
