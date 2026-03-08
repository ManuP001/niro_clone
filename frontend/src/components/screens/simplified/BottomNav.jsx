import React from 'react';
import { colors } from './theme';
import { HomeIcon, ConsultIcon, RemediesIcon, ProfileIcon } from './icons';

/**
 * BottomNav - Always 4 static tabs: Home, Consult, Remedies, Account
 * Account tab shows login prompt when logged out, full profile when logged in.
 * Only shown on mobile (< 768px) - Desktop uses DesktopNav
 */

const tabs = [
  { id: 'home', label: 'Home', Icon: HomeIcon },
  { id: 'consult', label: 'Consult', Icon: ConsultIcon },
  { id: 'remedies', label: 'Remedies', Icon: RemediesIcon },
  { id: 'account', label: 'Account', Icon: ProfileIcon },
];

export default function BottomNav({ activeTab, onTabChange }) {
  return (
    <nav
      className="fixed bottom-0 left-0 right-0 border-t z-50 md:hidden"
      style={{
        backgroundColor: '#ffffff',
        borderColor: colors.ui.borderDark,
        paddingBottom: 'env(safe-area-inset-bottom, 0px)',
        boxShadow: '0 -4px 20px rgba(0, 0, 0, 0.05)',
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
                  style={{ color: isActive ? colors.teal.primary : colors.text.muted }}
                />
              </div>
              <span
                className="text-[10px] font-medium"
                style={{ color: isActive ? colors.teal.primary : colors.text.muted }}
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
