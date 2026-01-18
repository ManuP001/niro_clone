/**
 * NIRO V5 Design System
 * Teal-Gold color scheme based on New UI Guidelines
 */

// ==========================================
// COLOR PALETTE (V5 - Teal/Gold)
// ==========================================
export const colors = {
  // Primary Teal
  teal: {
    primary: '#3E827A',
    dark: '#2D5F59',
    light: '#5A9E96',
    muted: 'rgba(62, 130, 122, 0.6)',
  },
  
  // Gold/Cream Accents
  gold: {
    primary: '#EFE1A9',
    light: '#FFFFC3',
    cream: 'rgba(255, 255, 195, 0.58)',
    dark: '#D4C78E',
  },
  
  // Backgrounds
  background: {
    primary: '#3E827A',
    gradient: 'linear-gradient(180deg, #3E827A 0%, rgba(255, 255, 195, 0.58) 100%)',
    gradientReverse: 'linear-gradient(180deg, rgba(255, 255, 195, 0.58) 0%, #3E827A 100%)',
    card: '#FFFFFF',
    cardDark: 'rgba(255, 255, 255, 0.1)',
    overlay: 'rgba(0, 0, 0, 0.5)',
  },
  
  // Logo Gradient (wordmark only)
  logo: {
    gradient: 'linear-gradient(135deg, #EFE1A9 0%, #FFFFFF 50%, #EFE1A9 100%)',
  },
  
  // Text Colors
  text: {
    primary: '#FFFFFF',
    dark: '#2D2D2D',
    secondary: '#5C5C5C',
    muted: 'rgba(255, 255, 255, 0.7)',
    mutedDark: '#8A8A8A',
    onCard: '#2D2D2D',
  },
  
  // UI Colors
  ui: {
    border: 'rgba(255, 255, 255, 0.2)',
    borderDark: 'rgba(0, 0, 0, 0.1)',
    shadow: 'rgba(0, 0, 0, 0.15)',
    success: '#4CAF50',
    error: '#F44336',
    warning: '#FF9800',
  },
};

// ==========================================
// TYPOGRAPHY
// ==========================================
export const typography = {
  fontFamily: {
    primary: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
    logo: "'Kumbh Sans', 'Inter', sans-serif",
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
  },
  
  fontWeight: {
    normal: 400,
    medium: 500,
    semibold: 600,
    bold: 700,
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
  full: '9999px',
};

// ==========================================
// SHADOWS
// ==========================================
export const shadows = {
  sm: '0 2px 8px rgba(0, 0, 0, 0.1)',
  md: '0 4px 16px rgba(0, 0, 0, 0.12)',
  lg: '0 8px 32px rgba(0, 0, 0, 0.16)',
  glow: '0 0 20px rgba(239, 225, 169, 0.4)',
  card: '0 4px 20px rgba(0, 0, 0, 0.08)',
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
// COMPONENT STYLES
// ==========================================
export const componentStyles = {
  button: {
    primary: {
      background: colors.gold.primary,
      color: colors.text.dark,
      borderRadius: borderRadius.lg,
      padding: '16px 32px',
      fontWeight: typography.fontWeight.semibold,
      boxShadow: shadows.md,
    },
    secondary: {
      background: 'rgba(255, 255, 255, 0.15)',
      color: colors.text.primary,
      border: `1px solid ${colors.ui.border}`,
      borderRadius: borderRadius.lg,
      padding: '14px 28px',
      fontWeight: typography.fontWeight.medium,
    },
    ghost: {
      background: 'transparent',
      color: colors.gold.primary,
      padding: '12px 24px',
      fontWeight: typography.fontWeight.medium,
    },
  },
  
  card: {
    background: colors.background.card,
    borderRadius: borderRadius.lg,
    boxShadow: shadows.card,
    padding: spacing.lg,
  },
  
  cardGlass: {
    background: 'rgba(255, 255, 255, 0.1)',
    backdropFilter: 'blur(10px)',
    borderRadius: borderRadius.lg,
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
};

export default {
  colors,
  typography,
  spacing,
  borderRadius,
  shadows,
  expertImages,
  componentStyles,
};
