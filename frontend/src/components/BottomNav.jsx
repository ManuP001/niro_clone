import React from 'react';
import { Home, MessageCircle, Star, Calendar, Heart } from 'lucide-react';
import { navItems } from '../data/mockData';

const iconMap = {
  home: Home,
  'message-circle': MessageCircle,
  star: Star,
  calendar: Calendar,
  heart: Heart,
};

const BottomNav = ({ activeScreen, onNavigate }) => {
  return (
    <div className="bg-white border-t border-gray-100 px-2 py-2 pb-6">
      <div className="flex justify-around items-center">
        {navItems.map((item) => {
          const Icon = iconMap[item.icon];
          const isActive = activeScreen === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onNavigate(item.id)}
              className={`flex flex-col items-center gap-1 p-2 rounded-xl transition-all duration-200 ${
                isActive
                  ? 'text-amber-600 bg-amber-50'
                  : 'text-gray-400 hover:text-gray-600'
              }`}
            >
              <Icon className={`w-5 h-5 ${isActive ? 'fill-amber-100' : ''}`} />
              <span className="text-[10px] font-medium">{item.label}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
};

export default BottomNav;
