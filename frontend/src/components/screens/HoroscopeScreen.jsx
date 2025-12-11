import React, { useState } from 'react';
import { ChevronDown, ChevronUp, Briefcase, Heart, Users, Wallet, Activity } from 'lucide-react';
import { horoscopeCategories, userData } from '../../data/mockData';

const iconMap = {
  briefcase: Briefcase,
  heart: Heart,
  users: Users,
  wallet: Wallet,
  activity: Activity,
};

const HoroscopeScreen = () => {
  const [expandedCategory, setExpandedCategory] = useState('love');

  return (
    <div className="h-full bg-white">
      {/* Header */}
      <div className="px-4 pt-2 pb-4 bg-gradient-to-b from-amber-50 to-white">
        <h1 className="text-lg font-semibold text-gray-800 mb-1">Detailed horoscopes</h1>
        <p className="text-xs text-gray-500">for everyone</p>
      </div>

      {/* Zodiac Selector */}
      <div className="px-4 mb-4">
        <div className="bg-gray-50 rounded-xl p-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-amber-100 rounded-full flex items-center justify-center">
              <span className="text-xl">♌</span>
            </div>
            <div>
              <p className="text-sm font-medium text-gray-800">{userData.zodiacSign}</p>
              <p className="text-xs text-gray-500">Jul 23 - Aug 22</p>
            </div>
          </div>
          <ChevronDown className="w-5 h-5 text-gray-400" />
        </div>
      </div>

      {/* Categories */}
      <div className="px-4 space-y-3 pb-4">
        {horoscopeCategories.map((category) => {
          const isExpanded = expandedCategory === category.id;
          const Icon = iconMap[category.icon] || Heart;
          
          return (
            <div
              key={category.id}
              className={`bg-white border rounded-xl overflow-hidden transition-all duration-300 ${
                isExpanded ? 'border-amber-300 shadow-md' : 'border-gray-200'
              }`}
            >
              <button
                onClick={() => setExpandedCategory(isExpanded ? null : category.id)}
                className="w-full px-4 py-3 flex items-center justify-between"
              >
                <div className="flex items-center gap-3">
                  <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${
                    isExpanded ? 'bg-amber-100' : 'bg-gray-100'
                  }`}>
                    <Icon className={`w-4 h-4 ${isExpanded ? 'text-amber-600' : 'text-gray-500'}`} />
                  </div>
                  <span className={`font-medium ${isExpanded ? 'text-amber-700' : 'text-gray-700'}`}>
                    {category.title}
                  </span>
                </div>
                {isExpanded ? (
                  <ChevronUp className="w-5 h-5 text-amber-500" />
                ) : (
                  <ChevronDown className="w-5 h-5 text-gray-400" />
                )}
              </button>
              
              {isExpanded && (
                <div className="px-4 pb-4">
                  <div className="pt-2 border-t border-gray-100">
                    {/* Score indicator */}
                    <div className="flex items-center gap-2 mb-3">
                      <div className="flex-1 h-2 bg-gray-100 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-gradient-to-r from-amber-400 to-amber-500 rounded-full transition-all duration-500"
                          style={{ width: `${category.score}%` }}
                        ></div>
                      </div>
                      <span className="text-sm font-medium text-amber-600">{category.score}%</span>
                    </div>
                    
                    <p className="text-sm text-gray-600 leading-relaxed">
                      {category.content}
                    </p>
                    
                    <button className="mt-3 text-xs text-amber-600 font-medium">
                      Read more
                    </button>
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default HoroscopeScreen;
