import React from 'react';

/**
 * AppHeader - Consistent header component for all app screens
 * Includes back button, title, and optional actions
 */

export default function AppHeader({ 
  title, 
  subtitle,
  onBack, 
  onHome,
  rightAction,
  transparent = false,
  sticky = true,
}) {
  return (
    <header 
      className={`${sticky ? 'sticky top-0' : ''} z-40 px-4 md:px-8 py-4 flex items-center gap-3`}
      style={{ 
        backgroundColor: transparent ? 'transparent' : 'rgba(251,248,243,0.95)',
        backdropFilter: transparent ? 'none' : 'blur(20px)',
        borderBottom: transparent ? 'none' : '1px solid rgba(0,0,0,0.06)',
      }}
    >
      {/* Back Button */}
      {onBack && (
        <button 
          onClick={onBack}
          className="p-2 -ml-2 rounded-full hover:bg-black/5 transition-colors"
          data-testid="header-back-btn"
        >
          <svg className="w-5 h-5" style={{ color: '#2D3748' }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
        </button>
      )}
      
      {/* Home Button (optional) */}
      {onHome && !onBack && (
        <button 
          onClick={onHome}
          className="p-2 -ml-2 rounded-full hover:bg-black/5 transition-colors"
          data-testid="header-home-btn"
        >
          <svg className="w-5 h-5" style={{ color: '#2D3748' }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
          </svg>
        </button>
      )}
      
      {/* Title */}
      <div className="flex-1 min-w-0">
        <h1 className="text-lg font-semibold truncate" style={{ color: '#2D3748' }}>
          {title}
        </h1>
        {subtitle && (
          <p className="text-xs truncate" style={{ color: '#5A6C7D' }}>
            {subtitle}
          </p>
        )}
      </div>
      
      {/* Right Action */}
      {rightAction && (
        <div className="flex-shrink-0">
          {rightAction}
        </div>
      )}
    </header>
  );
}
