/**
 * NIRO Design System - V10 (Based on niro-final-marquee_1.html)
 * New teal/peach/cream color scheme with Lexend font
 */

// ==========================================
// COLOR PALETTE (V10 - Teal/Peach/Cream)
// ==========================================
export const colors = {
  // Primary Teal
  teal: {
    primary: '#4A9B8E',
    soft: '#6AB3A6',
    dark: '#2D5C4A',
    muted: 'rgba(74, 155, 142, 0.6)',
    light: '#6AB3A6', // Alias for soft
  },
  
  // Accent Peach/Coral
  peach: {
    primary: '#E8A87C',
    soft: '#F5C9A8',
  },
  
  // Neutral Cream/Sand
  cream: {
    primary: '#FBF8F3',
    warm: '#F5EFE7',
  },
  sand: '#E8DFD1',
  
  // Gold (Legacy - mapped to peach for compatibility)
  gold: {
    primary: '#E8A87C',
    light: '#F5C9A8',
    cream: '#FBF8F3',
    dark: '#D4A574',
  },
  
  // Backgrounds
  background: {
    primary: '#FBF8F3',
    secondary: '#F5EFE7',
    card: '#FFFFFF',
    cardAlt: '#FBF8F3',
    overlay: 'rgba(0, 0, 0, 0.5)',
    gradient: 'linear-gradient(180deg, #4A9B8E 0%, #FBF8F3 100%)',
    gradientReverse: 'linear-gradient(180deg, #FBF8F3 0%, #4A9B8E 100%)',
  },
  
  // Logo
  logo: {
    gradient: 'linear-gradient(135deg, #4A9B8E 0%, #2D5C4A 100%)',
  },
  
  // Text Colors
  text: {
    primary: '#2D3748',
    dark: '#2D3748',
    secondary: '#5A6C7D',
    muted: '#8F9BAA',
    mutedDark: '#5A6C7D',
    light: '#8F9BAA',
    onCard: '#2D3748',
    onDark: '#FFFFFF',
  },
  
  // UI Colors
  ui: {
    border: 'rgba(74, 155, 142, 0.2)',
    borderDark: 'rgba(0, 0, 0, 0.08)',
    borderLight: 'rgba(255, 255, 255, 0.2)',
    shadow: 'rgba(74, 155, 142, 0.15)',
    success: '#4CAF50',
    error: '#F44336',
    warning: '#FF9800',
  },
};

// ==========================================
// TYPOGRAPHY (Lexend-based)
// ==========================================
export const typography = {
  fontFamily: {
    primary: "'Lexend', -apple-system, system-ui, sans-serif",
    logo: "'Lexend', -apple-system, system-ui, sans-serif",
  },
  
  fontSize: {
    xs: '11px',
    sm: '13px',
    base: '15px',
    lg: '17px',
    xl: '20px',
    '2xl': '24px',
    '3xl': '30px',
    '4xl': '36px',
    '5xl': '48px',
  },
  
  fontWeight: {
    light: 300,
    normal: 400,
    medium: 500,
    semibold: 600,
    bold: 700,
    extrabold: 800,
  },
  
  lineHeight: {
    tight: 1.2,
    normal: 1.4,
    relaxed: 1.6,
  },
};

// ==========================================
// SPACING
// ==========================================
export const spacing = {
  xs: '4px',
  sm: '8px',
  md: '16px',
  lg: '24px',
  xl: '32px',
  '2xl': '48px',
  '3xl': '64px',
  
  // Safe areas for mobile
  safeTop: 'env(safe-area-inset-top, 44px)',
  safeBottom: 'env(safe-area-inset-bottom, 34px)',
};

// ==========================================
// BORDER RADIUS
// ==========================================
export const borderRadius = {
  sm: '8px',
  md: '12px',
  lg: '16px',
  xl: '20px',
  '2xl': '24px',
  full: '9999px',
};

// ==========================================
// SHADOWS (New design system)
// ==========================================
export const shadows = {
  sm: '0 4px 12px rgba(74, 155, 142, 0.15)',
  md: '0 8px 24px rgba(74, 155, 142, 0.15)',
  lg: '0 12px 40px rgba(74, 155, 142, 0.2)',
  card: '0 4px 20px rgba(0, 0, 0, 0.04)',
  cardHover: '0 12px 40px rgba(74, 155, 142, 0.2)',
  button: '0 4px 12px rgba(74, 155, 142, 0.25)',
  peach: '0 12px 32px rgba(232, 168, 124, 0.35)',
  glow: '0 0 20px rgba(74, 155, 142, 0.4)',
};

// ==========================================
// EXPERT PLACEHOLDER IMAGES
// ==========================================
export const expertImages = [
  'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=200&h=200&fit=crop&crop=face',
  'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=200&h=200&fit=crop&crop=face',
  'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=200&h=200&fit=crop&crop=face',
  'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=200&h=200&fit=crop&crop=face',
  'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=200&h=200&fit=crop&crop=face',
  'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=200&h=200&fit=crop&crop=face',
];

// ==========================================
// COMPONENT STYLES (Updated for new design)
// ==========================================
export const componentStyles = {
  button: {
    primary: {
      background: colors.teal.primary,
      color: '#FFFFFF',
      borderRadius: borderRadius.full,
      padding: '16px 32px',
      fontWeight: typography.fontWeight.semibold,
      boxShadow: shadows.button,
    },
    secondary: {
      background: colors.peach.primary,
      color: colors.text.dark,
      borderRadius: borderRadius.full,
      padding: '16px 32px',
      fontWeight: typography.fontWeight.semibold,
      boxShadow: shadows.peach,
    },
    ghost: {
      background: 'transparent',
      color: colors.teal.primary,
      padding: '12px 24px',
      fontWeight: typography.fontWeight.medium,
    },
    outline: {
      background: 'transparent',
      color: colors.teal.primary,
      border: `2px solid ${colors.teal.primary}`,
      borderRadius: borderRadius.full,
      padding: '14px 28px',
      fontWeight: typography.fontWeight.medium,
    },
  },
  
  card: {
    background: colors.background.card,
    borderRadius: borderRadius.xl,
    boxShadow: shadows.card,
    padding: spacing.lg,
  },
  
  cardHover: {
    transform: 'translateY(-4px)',
    boxShadow: shadows.cardHover,
  },
  
  cardGlass: {
    background: 'rgba(255, 255, 255, 0.9)',
    backdropFilter: 'blur(12px)',
    borderRadius: borderRadius.xl,
    border: `1px solid ${colors.ui.border}`,
    padding: spacing.lg,
  },
  
  input: {
    background: colors.background.card,
    border: `1px solid ${colors.ui.borderDark}`,
    borderRadius: borderRadius.md,
    padding: '14px 16px',
    fontSize: typography.fontSize.base,
  },
  
  nav: {
    background: 'rgba(255, 255, 255, 0.95)',
    backdropFilter: 'blur(20px)',
    borderBottom: `1px solid ${colors.ui.borderDark}`,
  },
};

// ==========================================
// BREAKPOINTS
// ==========================================
export const breakpoints = {
  sm: '640px',
  md: '768px',
  lg: '1024px',
  xl: '1280px',
  '2xl': '1536px',
};

export default {
  colors,
  typography,
  spacing,
  borderRadius,
  shadows,
  expertImages,
  componentStyles,
  breakpoints,
};
