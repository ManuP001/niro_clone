import React from 'react';
import { colors } from './theme';
import { HomeIcon, ConsultIcon, ChatIcon, RemediesIcon, AstroIcon, PackageIcon } from './icons';

/**
 * BottomNav - Navigation with teal color scheme (V6)
 * New users: Home, Consult, Remedies, Astro (4 tabs)
 * Returning users: Home, Consult, Remedies, My Pack, Astro (5 tabs)
 * Mira removed from nav — accessible from homepage
 */

// Base tabs for all users (Mira removed)
const baseTabs = [
  { id: 'home', label: 'Home', Icon: HomeIcon },
  { id: 'consult', label: 'Consult', Icon: ConsultIcon },
  { id: 'remedies', label: 'Remedies', Icon: RemediesIcon },
];

// Tab for returning users with active plans
const myPackTab = { id: 'mypack', label: 'My Pack', Icon: PackageIcon };

// End tabs
const endTabs = [
  { id: 'astro', label: 'Astro', Icon: AstroIcon },
];

export default function BottomNav({ activeTab, onTabChange, hasActivePlan = false }) {
  // Build tabs based on user state
  // New users: Home, Consult, Remedies, Astro (4 tabs)
  // Returning users: Home, Consult, Remedies, My Pack, Astro (5 tabs)
  const tabs = hasActivePlan 
    ? [...baseTabs, myPackTab, ...endTabs]
    : [...baseTabs, ...endTabs];
  
  return (
    <nav 
      className="fixed bottom-0 left-0 right-0 border-t z-50"
      style={{ 
        backgroundColor: '#ffffff',
        borderColor: colors.ui.borderDark,
        paddingBottom: 'env(safe-area-inset-bottom, 0px)',
      }}
    >
      <div className="flex items-center justify-around h-16 max-w-lg mx-auto">
        {tabs.map((tab) => {
          const isActive = activeTab === tab.id;
          const { Icon } = tab;
          return (
            <button
              key={tab.id}
              onClick={() => onTabChange(tab.id)}
              className="flex flex-col items-center justify-center flex-1 h-full transition-all relative"
              data-testid={`nav-tab-${tab.id}`}
            >
              {/* Icon container */}
              <div 
                className={`w-10 h-10 rounded-full flex items-center justify-center mb-0.5 transition-all ${isActive ? 'scale-105' : ''}`}
                style={{ 
                  backgroundColor: isActive ? `${colors.teal.primary}15` : 'transparent',
                }}
              >
                <Icon 
                  className="w-5 h-5" 
                  style={{ color: isActive ? colors.teal.primary : colors.text.mutedDark }}
                />
              </div>
              <span 
                className="text-[10px] font-medium"
                style={{ color: isActive ? colors.teal.primary : colors.text.mutedDark }}
              >
                {tab.label}
              </span>
              {isActive && (
                <div 
                  className="absolute bottom-0 w-8 h-0.5 rounded-t-full"
                  style={{ backgroundColor: colors.teal.primary }}
                />
              )}
            </button>
          );
        })}
      </div>
    </nav>
  );
}
