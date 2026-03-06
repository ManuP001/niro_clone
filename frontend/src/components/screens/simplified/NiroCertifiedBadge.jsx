import React from 'react';

/**
 * NiroCertifiedBadge — gold shield badge shown on all active expert cards and profiles.
 *
 * size="sm"  — compact inline badge for listing cards (shield + text side by side)
 * size="md"  — larger badge for expert profile header (stacked, more prominent)
 */
export default function NiroCertifiedBadge({ size = 'sm' }) {
  if (size === 'md') {
    return (
      <div className="flex flex-col items-center gap-0.5">
        <ShieldIcon size={32} />
        <span
          className="text-[9px] font-bold tracking-widest leading-none"
          style={{ color: '#C9A84C' }}
        >
          NIRO
        </span>
        <span
          className="text-[8px] font-bold tracking-widest leading-none"
          style={{ color: '#C9A84C' }}
        >
          CERTIFIED
        </span>
      </div>
    );
  }

  // size="sm" — horizontal inline
  return (
    <div className="flex items-center gap-1">
      <ShieldIcon size={16} />
      <span
        className="text-[10px] font-bold tracking-wider"
        style={{ color: '#C9A84C' }}
      >
        NIRO CERTIFIED
      </span>
    </div>
  );
}

function ShieldIcon({ size }) {
  return (
    <svg
      width={size}
      height={size * 1.15}
      viewBox="0 0 40 46"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <defs>
        <linearGradient id="niro-gold" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#C9A84C" />
          <stop offset="50%" stopColor="#E8D5A3" />
          <stop offset="100%" stopColor="#B8902A" />
        </linearGradient>
      </defs>
      {/* Shield outline */}
      <path
        d="M20 2L3 9v14c0 10.5 7.3 19.5 17 22 9.7-2.5 17-11.5 17-22V9L20 2z"
        fill="url(#niro-gold)"
        opacity="0.15"
      />
      <path
        d="M20 2L3 9v14c0 10.5 7.3 19.5 17 22 9.7-2.5 17-11.5 17-22V9L20 2z"
        stroke="url(#niro-gold)"
        strokeWidth="2"
        fill="none"
      />
      {/* Inner circle */}
      <circle
        cx="20"
        cy="22"
        r="8"
        stroke="url(#niro-gold)"
        strokeWidth="1.5"
        fill="none"
      />
      {/* Center dot */}
      <circle cx="20" cy="22" r="2.5" fill="url(#niro-gold)" />
    </svg>
  );
}
