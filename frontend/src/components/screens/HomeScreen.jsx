import React from 'react';
import { Sun, Bell, Grid3X3, MessageSquare, ChevronRight } from 'lucide-react';
import { userData, todayInsights, quickQuestions } from '../../data/mockData';

const HomeScreen = ({ onNavigate }) => {
  return (
    <div className="h-full bg-gradient-to-b from-amber-50 to-white">
      {/* Header */}
      <div className="px-4 pt-2 pb-4">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-1">
            <span className="text-lg font-semibold text-gray-800">Astro</span>
            <Sun className="w-5 h-5 text-amber-500" />
            <span className="text-lg font-semibold text-gray-800">Sure</span>
            <span className="text-lg text-gray-400">.ai</span>
          </div>
          <div className="flex items-center gap-3">
            <button className="text-red-500 relative">
              <Bell className="w-5 h-5" />
              <span className="absolute -top-1 -right-1 w-2 h-2 bg-red-500 rounded-full"></span>
            </button>
            <button className="text-gray-600">
              <Grid3X3 className="w-5 h-5" />
            </button>
            <img
              src={userData.avatar}
              alt="Profile"
              className="w-8 h-8 rounded-full border-2 border-amber-400"
            />
          </div>
        </div>

        {/* Greeting */}
        <h1 className="text-xl font-semibold text-gray-800 mb-4">
          Namaste {userData.name}
        </h1>

        {/* Chat Input */}
        <button
          onClick={() => onNavigate('chat')}
          className="w-full bg-gradient-to-r from-amber-400 to-amber-500 rounded-full px-4 py-3 flex items-center gap-3 shadow-lg shadow-amber-200"
        >
          <MessageSquare className="w-5 h-5 text-white" />
          <span className="text-white text-sm flex-1 text-left">Ask Agastyaa anything...</span>
          <div className="flex items-center gap-1">
            <span className="w-6 h-6 bg-white/30 rounded-full flex items-center justify-center">
              <span className="text-white text-xs">✨</span>
            </span>
            <span className="w-6 h-6 bg-white/30 rounded-full flex items-center justify-center">
              <span className="text-white text-xs">🎤</span>
            </span>
          </div>
        </button>
      </div>

      {/* Date Tabs */}
      <div className="px-4 mb-4">
        <div className="flex gap-2">
          <button className="px-4 py-1.5 text-xs text-gray-500">Yesterday</button>
          <button className="px-4 py-1.5 text-xs bg-amber-500 text-white rounded-full font-medium">Today</button>
          <button className="px-4 py-1.5 text-xs text-gray-500">Tomorrow</button>
        </div>
      </div>

      {/* Lucky Info */}
      <div className="px-4 mb-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-xs text-gray-500 mb-1">Lucky Color</p>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 bg-red-500 rounded-full"></div>
              <span className="text-sm font-medium text-gray-800">Red</span>
            </div>
          </div>
          <div>
            <p className="text-xs text-gray-500 mb-1">Lucky Number</p>
            <div className="flex items-center gap-2">
              {['😊', '😌', '⚡'].map((emoji, i) => (
                <span key={i} className="text-lg">{emoji}</span>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Cosmic Info Cards */}
      <div className="px-4 space-y-3 mb-4">
        <div className="bg-white rounded-xl p-3 shadow-sm border border-gray-100">
          <div className="flex justify-between items-center">
            <div>
              <p className="text-xs text-gray-500">Masar &gt;</p>
              <p className="text-sm text-gray-700">In Sagittarius</p>
            </div>
            <div className="text-right">
              <p className="text-xs text-gray-500">Auspicious time &gt;</p>
              <p className="text-sm text-gray-700">5/45 - 18:30</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl p-3 shadow-sm border border-gray-100">
          <div className="flex justify-between items-center">
            <div>
              <p className="text-xs text-gray-500">Ascendant &gt;</p>
              <p className="text-sm text-gray-700">In Cancer</p>
            </div>
            <div className="text-right">
              <p className="text-xs text-gray-500">Danger/loss time &gt;</p>
              <p className="text-sm text-red-500">09:45 - 11:05</p>
            </div>
          </div>
        </div>
      </div>

      {/* Day Message */}
      <div className="px-4 mb-4">
        <div className="bg-gradient-to-r from-amber-100 to-orange-100 rounded-xl p-4">
          <p className="text-sm text-gray-700 italic">
            &quot;{todayInsights.message}&quot;
          </p>
        </div>
      </div>

      {/* Quick Questions */}
      <div className="px-4 pb-4">
        <p className="text-xs text-gray-500 mb-2">Quick questions</p>
        <div className="flex flex-wrap gap-2">
          {quickQuestions.slice(0, 3).map((q, i) => (
            <button
              key={i}
              onClick={() => onNavigate('chat')}
              className="text-xs bg-white border border-gray-200 rounded-full px-3 py-1.5 text-gray-600 hover:bg-amber-50 hover:border-amber-200 transition-colors"
            >
              {q}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

export default HomeScreen;
