import React, { useState } from 'react';
import { colors } from './theme';
import { RefreshIcon } from './icons';

/**
 * DevToggle - Dev controls for New/Returning mode + Reset
 * ALWAYS VISIBLE at top-left corner
 */

const USER_STATE_KEY = 'niro_user_state';
const ONBOARDING_KEY = 'niro_onboarding_completed';
const HOME_TOUR_KEY = 'niro_home_tour_completed';

export default function DevToggle({ userMode, onModeChange, onReset }) {
  const handleReset = () => {
    localStorage.removeItem(USER_STATE_KEY);
    localStorage.removeItem(ONBOARDING_KEY);
    localStorage.removeItem(HOME_TOUR_KEY);
    onReset();
  };

  return (
    <div 
      className="fixed top-2 left-2 z-50 flex gap-1 rounded-lg p-1 shadow-md"
      style={{ 
        backgroundColor: 'rgba(255,255,255,0.95)',
        border: '1px solid rgba(0,0,0,0.1)',
      }}
    >
      <button 
        onClick={() => onModeChange('NEW')}
        className={`text-xs px-2 py-1 rounded transition-all font-medium`}
        style={{ 
          backgroundColor: userMode === 'NEW' ? colors.teal.primary : 'rgba(0,0,0,0.05)',
          color: userMode === 'NEW' ? '#fff' : colors.text.secondary,
        }}
      >
        New
      </button>
      <button 
        onClick={() => onModeChange('RETURNING')}
        className={`text-xs px-2 py-1 rounded transition-all font-medium`}
        style={{ 
          backgroundColor: userMode === 'RETURNING' ? colors.teal.primary : 'rgba(0,0,0,0.05)',
          color: userMode === 'RETURNING' ? '#fff' : colors.text.secondary,
        }}
      >
        Returning
      </button>
      <button 
        onClick={handleReset}
        className="text-xs px-2 py-1 rounded transition-all flex items-center gap-1"
        style={{ 
          backgroundColor: 'rgba(244,67,54,0.1)',
          color: colors.ui.error,
        }}
        title="Reset onboarding"
      >
        <RefreshIcon className="w-3 h-3" />
        Reset
      </button>
    </div>
  );
}
