import React, { useState } from 'react';
import { Home, MessageCircle, Star, Calendar, LogOut, Grid3x3, Activity } from 'lucide-react';
import { navItems } from '../data/mockData';

const iconMap = {
  home: Home,
  'message-circle': MessageCircle,
  star: Star,
  calendar: Calendar,
  kundli: Grid3x3,
  activity: Activity,
};

const BottomNav = ({ activeScreen, onNavigate, onLogout }) => {
  const [showLogout, setShowLogout] = useState(false);

  return (
    <div className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-100 px-2 py-2 pb-6 z-40 lg:relative lg:bottom-auto">
      <div className="flex justify-around items-center max-w-[840px] mx-auto">
        {navItems.map((item) => {
          const Icon = iconMap[item.icon];
          const isActive = activeScreen === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onNavigate(item.id)}
              className={`flex flex-col items-center gap-1 p-2 rounded-xl transition-all duration-200 ${
                isActive
                  ? 'text-emerald-600 bg-emerald-50'
                  : 'text-gray-400 hover:text-gray-600'
              }`}
            >
              <Icon className={`w-5 h-5 ${isActive ? 'fill-emerald-100' : ''}`} />
              <span className="text-[10px] font-medium">{item.label}</span>
            </button>
          );
        })}
        
        {/* Logout button */}
        <div className="relative">
          <button
            onClick={() => setShowLogout(!showLogout)}
            className="flex flex-col items-center gap-1 p-2 rounded-xl transition-all duration-200 text-gray-400 hover:text-gray-600"
          >
            <LogOut className="w-5 h-5" />
            <span className="text-[10px] font-medium">Logout</span>
          </button>

          {/* Logout confirmation */}
          {showLogout && (
            <div className="absolute bottom-12 right-0 bg-white border border-gray-200 rounded-lg shadow-lg p-3 z-20">
              <p className="text-xs text-gray-700 mb-3 whitespace-nowrap">Logout?</p>
              <div className="flex gap-2">
                <button
                  onClick={() => {
                    setShowLogout(false);
                    onLogout();
                  }}
                  className="px-3 py-1 bg-red-600 text-white text-xs rounded font-medium hover:bg-red-700"
                >
                  Yes
                </button>
                <button
                  onClick={() => setShowLogout(false)}
                  className="px-3 py-1 bg-gray-200 text-gray-700 text-xs rounded font-medium hover:bg-gray-300"
                >
                  No
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default BottomNav;
