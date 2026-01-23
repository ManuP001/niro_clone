import React from 'react';

/**
 * NIRO V5 Icon System
 * Consistent stroke-based icons with unique icon per tile
 * All icons: 24x24 viewBox, 1.5px stroke
 */

const iconProps = {
  xmlns: 'http://www.w3.org/2000/svg',
  viewBox: '0 0 24 24',
  fill: 'none',
  stroke: 'currentColor',
  strokeWidth: 1.5,
  strokeLinecap: 'round',
  strokeLinejoin: 'round',
};

// ==========================================
// NAVIGATION ICONS
// ==========================================
export const HomeIcon = ({ className = 'w-6 h-6' }) => (
  <svg className={className} {...iconProps}>
    <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
    <polyline points="9,22 9,12 15,12 15,22" />
  </svg>
);

export const ConsultIcon = ({ className = 'w-6 h-6' }) => (
  <svg className={className} {...iconProps}>
    <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
    <circle cx="9" cy="7" r="4" />
    <path d="M23 21v-2a4 4 0 0 0-3-3.87" />
    <path d="M16 3.13a4 4 0 0 1 0 7.75" />
  </svg>
);

export const ChatIcon = ({ className = 'w-6 h-6' }) => (
  <svg className={className} {...iconProps}>
    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
  </svg>
);

export const RemediesIcon = ({ className = 'w-6 h-6' }) => (
  <svg className={className} {...iconProps}>
    <path d="M12 2L2 7l10 5 10-5-10-5z" />
    <path d="M2 17l10 5 10-5" />
    <path d="M2 12l10 5 10-5" />
  </svg>
);

export const AstroIcon = ({ className = 'w-6 h-6' }) => (
  <svg className={className} {...iconProps}>
    <circle cx="12" cy="12" r="10" />
    <line x1="12" y1="2" x2="12" y2="22" />
    <line x1="2" y1="12" x2="22" y2="12" />
    <path d="M4.93 4.93l14.14 14.14" />
    <path d="M19.07 4.93L4.93 19.07" />
  </svg>
);

export const ProfileIcon = ({ className = 'w-6 h-6' }) => (
  <svg className={className} {...iconProps}>
    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
    <circle cx="12" cy="7" r="4" />
  </svg>
);

// ==========================================
// TILE-SPECIFIC ICONS (15 unique icons)
// ==========================================

// Relationship: Heart
export const HeartIcon = ({ className = 'w-6 h-6' }) => (
  <svg className={className} {...iconProps}>
    <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z" />
  </svg>
);

// Marriage: Ring
export const RingIcon = ({ className = 'w-6 h-6' }) => (
  <svg className={className} {...iconProps}>
    <circle cx="12" cy="12" r="8" />
    <circle cx="12" cy="12" r="4" />
    <path d="M12 4v-2" />
    <path d="M8 5l-1-1.73" />
    <path d="M16 5l1-1.73" />
  </svg>
);

// Healing: Heart with pulse
export const HealingIcon = ({ className = 'w-6 h-6' }) => (
  <svg className={className} {...iconProps}>
    <path d="M19.5 13.5L12 21l-7.5-7.5a5.5 5.5 0 0 1 7.5-8 5.5 5.5 0 0 1 7.5 8z" />
    <path d="M12 13l2-3 2 4 2-3" />
  </svg>
);

// Career: Compass
export const CompassIcon = ({ className = 'w-6 h-6' }) => (
  <svg className={className} {...iconProps}>
    <circle cx="12" cy="12" r="10" />
    <polygon points="16.24,7.76 14.12,14.12 7.76,16.24 9.88,9.88" />
  </svg>
);

// Job: Briefcase
export const BriefcaseIcon = ({ className = 'w-6 h-6' }) => (
  <svg className={className} {...iconProps}>
    <rect x="2" y="7" width="20" height="14" rx="2" ry="2" />
    <path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16" />
  </svg>
);

// Balance: Scale
export const BalanceIcon = ({ className = 'w-6 h-6' }) => (
  <svg className={className} {...iconProps}>
    <path d="M12 3v18" />
    <path d="M5 8l7-2 7 2" />
    <path d="M5 8v6l3 3 2-9" />
    <path d="M19 8v6l-3 3-2-9" />
  </svg>
);

// Business: Chart
export const ChartIcon = ({ className = 'w-6 h-6' }) => (
  <svg className={className} {...iconProps}>
    <line x1="18" y1="20" x2="18" y2="10" />
    <line x1="12" y1="20" x2="12" y2="4" />
    <line x1="6" y1="20" x2="6" y2="14" />
    <path d="M3 20h18" />
  </svg>
);

// Financial: Trending up
export const TrendingIcon = ({ className = 'w-6 h-6' }) => (
  <svg className={className} {...iconProps}>
    <polyline points="23,6 13.5,15.5 8.5,10.5 1,18" />
    <polyline points="17,6 23,6 23,12" />
  </svg>
);

// Timing: Clock
export const ClockIcon = ({ className = 'w-6 h-6' }) => (
  <svg className={className} {...iconProps}>
    <circle cx="12" cy="12" r="10" />
    <polyline points="12,6 12,12 16,14" />
  </svg>
);

// Fertility: Baby
export const BabyIcon = ({ className = 'w-6 h-6' }) => (
  <svg className={className} {...iconProps}>
    <circle cx="12" cy="8" r="5" />
    <path d="M12 13c-4 0-7 2-7 5v2h14v-2c0-3-3-5-7-5z" />
    <path d="M9 6c0-1 .5-2 1.5-2s1.5.5 1.5 1" />
  </svg>
);

// Star
export const StarIcon = ({ className = 'w-6 h-6', filled = false }) => (
  <svg className={className} {...iconProps} fill={filled ? 'currentColor' : 'none'}>
    <polygon points="12,2 15.09,8.26 22,9.27 17,14.14 18.18,21.02 12,17.77 5.82,21.02 7,14.14 2,9.27 8.91,8.26" />
  </svg>
);

// Growth: Plant
export const GrowthIcon = ({ className = 'w-6 h-6' }) => (
  <svg className={className} {...iconProps}>
    <path d="M12 22V12" />
    <path d="M12 12c-4 0-7-3-7-7 4 0 7 3 7 7" />
    <path d="M12 12c4 0 7-3 7-7-4 0-7 3-7 7" />
    <path d="M12 16c-2 0-4 1-4 4h8c0-3-2-4-4-4" />
  </svg>
);

// Health: Heart pulse
export const HeartPulseIcon = ({ className = 'w-6 h-6' }) => (
  <svg className={className} {...iconProps}>
    <path d="M22 12h-4l-3 9L9 3l-3 9H2" />
  </svg>
);

// Sun
export const SunIcon = ({ className = 'w-6 h-6' }) => (
  <svg className={className} {...iconProps}>
    <circle cx="12" cy="12" r="5" />
    <line x1="12" y1="1" x2="12" y2="3" />
    <line x1="12" y1="21" x2="12" y2="23" />
    <line x1="4.22" y1="4.22" x2="5.64" y2="5.64" />
    <line x1="18.36" y1="18.36" x2="19.78" y2="19.78" />
    <line x1="1" y1="12" x2="3" y2="12" />
    <line x1="21" y1="12" x2="23" y2="12" />
    <line x1="4.22" y1="19.78" x2="5.64" y2="18.36" />
    <line x1="18.36" y1="5.64" x2="19.78" y2="4.22" />
  </svg>
);

// Mind
export const MindIcon = ({ className = 'w-6 h-6' }) => (
  <svg className={className} {...iconProps}>
    <path d="M12 2a7 7 0 0 0-7 7c0 3 2 5 4 6.5V18a2 2 0 0 0 2 2h2a2 2 0 0 0 2-2v-2.5c2-1.5 4-3.5 4-6.5a7 7 0 0 0-7-7z" />
    <line x1="9" y1="22" x2="15" y2="22" />
    <path d="M9 9h.01" />
    <path d="M15 9h.01" />
    <path d="M10 13c.5.5 1.5.5 2 0" />
  </svg>
);

// Family
export const FamilyIcon = ({ className = 'w-6 h-6' }) => (
  <svg className={className} {...iconProps}>
    <circle cx="9" cy="7" r="3" />
    <circle cx="17" cy="7" r="2" />
    <path d="M5 21v-2a4 4 0 0 1 4-4h2a4 4 0 0 1 4 4v2" />
    <path d="M17 11a2 2 0 0 1 2 2v2" />
  </svg>
);

// Wallet
export const WalletIcon = ({ className = 'w-6 h-6' }) => (
  <svg className={className} {...iconProps}>
    <path d="M20 12V8H6a2 2 0 0 1-2-2c0-1.1.9-2 2-2h12v4" />
    <path d="M4 6v12a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2H6" />
    <circle cx="18" cy="14" r="1" />
  </svg>
);

// ==========================================
// ACTION ICONS
// ==========================================
export const ArrowLeftIcon = ({ className = 'w-6 h-6' }) => (
  <svg className={className} {...iconProps}>
    <line x1="19" y1="12" x2="5" y2="12" />
    <polyline points="12,19 5,12 12,5" />
  </svg>
);

export const ArrowRightIcon = ({ className = 'w-6 h-6' }) => (
  <svg className={className} {...iconProps}>
    <line x1="5" y1="12" x2="19" y2="12" />
    <polyline points="12,5 19,12 12,19" />
  </svg>
);

export const ChevronRightIcon = ({ className = 'w-6 h-6' }) => (
  <svg className={className} {...iconProps}>
    <polyline points="9,18 15,12 9,6" />
  </svg>
);

export const ChevronDownIcon = ({ className = 'w-6 h-6' }) => (
  <svg className={className} {...iconProps}>
    <polyline points="6,9 12,15 18,9" />
  </svg>
);

export const CheckIcon = ({ className = 'w-6 h-6' }) => (
  <svg className={className} {...iconProps}>
    <polyline points="20,6 9,17 4,12" />
  </svg>
);

export const LockIcon = ({ className = 'w-6 h-6' }) => (
  <svg className={className} {...iconProps}>
    <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
    <path d="M7 11V7a5 5 0 0 1 10 0v4" />
  </svg>
);

export const UnlockIcon = ({ className = 'w-6 h-6' }) => (
  <svg className={className} {...iconProps}>
    <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
    <path d="M7 11V7a5 5 0 0 1 9.9-1" />
  </svg>
);

export const ShieldIcon = ({ className = 'w-6 h-6' }) => (
  <svg className={className} {...iconProps}>
    <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
  </svg>
);

export const SendIcon = ({ className = 'w-6 h-6' }) => (
  <svg className={className} {...iconProps}>
    <line x1="22" y1="2" x2="11" y2="13" />
    <polygon points="22,2 15,22 11,13 2,9" />
  </svg>
);

export const CalendarIcon = ({ className = 'w-6 h-6' }) => (
  <svg className={className} {...iconProps}>
    <rect x="3" y="4" width="18" height="18" rx="2" ry="2" />
    <line x1="16" y1="2" x2="16" y2="6" />
    <line x1="8" y1="2" x2="8" y2="6" />
    <line x1="3" y1="10" x2="21" y2="10" />
  </svg>
);

export const DocumentIcon = ({ className = 'w-6 h-6' }) => (
  <svg className={className} {...iconProps}>
    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
    <polyline points="14,2 14,8 20,8" />
    <line x1="16" y1="13" x2="8" y2="13" />
    <line x1="16" y1="17" x2="8" y2="17" />
  </svg>
);

export const GiftIcon = ({ className = 'w-6 h-6' }) => (
  <svg className={className} {...iconProps}>
    <polyline points="20,12 20,22 4,22 4,12" />
    <rect x="2" y="7" width="20" height="5" />
    <line x1="12" y1="22" x2="12" y2="7" />
    <path d="M12 7H7.5a2.5 2.5 0 0 1 0-5C11 2 12 7 12 7z" />
    <path d="M12 7h4.5a2.5 2.5 0 0 0 0-5C13 2 12 7 12 7z" />
  </svg>
);

export const PhoneIcon = ({ className = 'w-6 h-6' }) => (
  <svg className={className} {...iconProps}>
    <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z" />
  </svg>
);

export const QuoteIcon = ({ className = 'w-6 h-6' }) => (
  <svg className={className} {...iconProps}>
    <path d="M3 21c3 0 7-1 7-8V5c0-1.25-.756-2.017-2-2H4c-1.25 0-2 .75-2 1.972V11c0 1.25.75 2 2 2 1 0 1 0 1 1v1c0 1-1 2-2 2s-1 .008-1 1.031V21c0 1 0 1 1 1z" />
    <path d="M15 21c3 0 7-1 7-8V5c0-1.25-.757-2.017-2-2h-4c-1.25 0-2 .75-2 1.972V11c0 1.25.75 2 2 2h.75c0 2.25.25 4-2.75 4v3c0 1 0 1 1 1z" />
  </svg>
);

export const SparklesIcon = ({ className = 'w-6 h-6' }) => (
  <svg className={className} {...iconProps}>
    <path d="M12 3l1.5 4.5L18 9l-4.5 1.5L12 15l-1.5-4.5L6 9l4.5-1.5L12 3z" />
    <path d="M5 19l.5 1.5L7 21l-1.5.5L5 23l-.5-1.5L3 21l1.5-.5L5 19z" />
    <path d="M19 5l.5 1.5L21 7l-1.5.5L19 9l-.5-1.5L17 7l1.5-.5L19 5z" />
  </svg>
);

export const RefreshIcon = ({ className = 'w-6 h-6' }) => (
  <svg className={className} {...iconProps}>
    <polyline points="23,4 23,10 17,10" />
    <polyline points="1,20 1,14 7,14" />
    <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15" />
  </svg>
);

export const ToolIcon = ({ className = 'w-6 h-6' }) => (
  <svg className={className} {...iconProps}>
    <path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z" />
  </svg>
);

export const PlusIcon = ({ className = 'w-6 h-6' }) => (
  <svg className={className} {...iconProps}>
    <line x1="12" y1="5" x2="12" y2="19" />
    <line x1="5" y1="12" x2="19" y2="12" />
  </svg>
);

export const MenuIcon = ({ className = 'w-6 h-6' }) => (
  <svg className={className} {...iconProps}>
    <line x1="3" y1="12" x2="21" y2="12" />
    <line x1="3" y1="6" x2="21" y2="6" />
    <line x1="3" y1="18" x2="21" y2="18" />
  </svg>
);

export const CloseIcon = ({ className = 'w-6 h-6' }) => (
  <svg className={className} {...iconProps}>
    <line x1="18" y1="6" x2="6" y2="18" />
    <line x1="6" y1="6" x2="18" y2="18" />
  </svg>
);

export const UsersIcon = ({ className = 'w-6 h-6' }) => (
  <svg className={className} {...iconProps}>
    <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
    <circle cx="9" cy="7" r="4" />
    <path d="M23 21v-2a4 4 0 0 0-3-3.87" />
    <path d="M16 3.13a4 4 0 0 1 0 7.75" />
  </svg>
);

// ==========================================
// TILE ICON MAPPER
// ==========================================
export const getTileIcon = (iconType, className = 'w-6 h-6') => {
  const icons = {
    heart: <HeartIcon className={className} />,
    ring: <RingIcon className={className} />,
    rings: <RingIcon className={className} />,
    healing: <HealingIcon className={className} />,
    compass: <CompassIcon className={className} />,
    briefcase: <BriefcaseIcon className={className} />,
    balance: <BalanceIcon className={className} />,
    chart: <ChartIcon className={className} />,
    trending: <TrendingIcon className={className} />,
    clock: <ClockIcon className={className} />,
    baby: <BabyIcon className={className} />,
    star: <StarIcon className={className} />,
    growth: <GrowthIcon className={className} />,
    heart_pulse: <HeartPulseIcon className={className} />,
    sun: <SunIcon className={className} />,
    mind: <MindIcon className={className} />,
    family: <FamilyIcon className={className} />,
    wallet: <WalletIcon className={className} />,
  };
  return icons[iconType] || <StarIcon className={className} />;
};

export default {
  HomeIcon,
  ConsultIcon,
  ChatIcon,
  RemediesIcon,
  AstroIcon,
  ProfileIcon,
  HeartIcon,
  RingIcon,
  HealingIcon,
  CompassIcon,
  BriefcaseIcon,
  BalanceIcon,
  ChartIcon,
  TrendingIcon,
  ClockIcon,
  BabyIcon,
  StarIcon,
  GrowthIcon,
  HeartPulseIcon,
  SunIcon,
  MindIcon,
  ArrowLeftIcon,
  ArrowRightIcon,
  ChevronRightIcon,
  ChevronDownIcon,
  CheckIcon,
  LockIcon,
  UnlockIcon,
  ShieldIcon,
  SendIcon,
  CalendarIcon,
  DocumentIcon,
  GiftIcon,
  SparklesIcon,
  RefreshIcon,
  ToolIcon,
  PlusIcon,
  MenuIcon,
  CloseIcon,
  getTileIcon,
};
