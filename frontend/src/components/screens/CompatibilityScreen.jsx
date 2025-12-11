import React from 'react';
import { Share2, ThumbsUp, Plus } from 'lucide-react';
import { compatibilityData } from '../../data/mockData';

const CompatibilityScreen = () => {
  return (
    <div className="h-full bg-white overflow-y-auto">
      {/* Header */}
      <div className="px-4 pt-2 pb-4 bg-gradient-to-b from-pink-50 to-white">
        <div className="flex items-center justify-between mb-2">
          <h1 className="text-lg font-semibold text-gray-800">Compatibility report</h1>
          <button className="text-gray-500">
            <Share2 className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Profile Avatars */}
      <div className="px-4 mb-6">
        <div className="flex items-center justify-center gap-4">
          {/* User Profile */}
          <div className="text-center">
            <div className="relative">
              <img
                src={compatibilityData.user.avatar}
                alt={compatibilityData.user.name}
                className="w-16 h-16 rounded-full border-4 border-amber-400"
              />
              <span className="absolute -bottom-1 left-1/2 -translate-x-1/2 bg-amber-500 text-white text-[10px] px-2 py-0.5 rounded-full">
                {compatibilityData.user.name}
              </span>
            </div>
          </div>

          {/* Compatibility Circles */}
          <div className="flex items-center gap-1">
            {['AR', 'AK', 'KR', 'VK'].map((initials, i) => (
              <div
                key={i}
                className={`w-10 h-10 rounded-full flex items-center justify-center text-white text-xs font-medium ${
                  i === 0 ? 'bg-amber-500' :
                  i === 1 ? 'bg-orange-500' :
                  i === 2 ? 'bg-green-500' : 'bg-blue-500'
                }`}
              >
                {initials}
              </div>
            ))}
          </div>

          {/* Partner Profile */}
          <div className="text-center">
            <div className="relative">
              <img
                src={compatibilityData.partner.avatar}
                alt={compatibilityData.partner.name}
                className="w-16 h-16 rounded-full border-4 border-pink-400"
              />
              <span className="absolute -bottom-1 left-1/2 -translate-x-1/2 bg-pink-500 text-white text-[10px] px-2 py-0.5 rounded-full">
                {compatibilityData.partner.name}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Parameters */}
      <div className="px-4 mb-4">
        <div className="flex items-center justify-between text-xs text-gray-500 mb-3">
          <span>Parameters</span>
          <span>Gund & kaal daya.</span>
          <span>Remedies</span>
          <span>Puja</span>
        </div>
      </div>

      {/* Match Score */}
      <div className="px-4 mb-6">
        <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-2xl p-6 text-center relative overflow-hidden">
          {/* Decorative elements */}
          <div className="absolute top-2 right-2 w-20 h-20 bg-green-100 rounded-full opacity-50"></div>
          <div className="absolute bottom-2 left-2 w-16 h-16 bg-emerald-100 rounded-full opacity-50"></div>
          
          <div className="relative z-10">
            <div className="flex items-center justify-center gap-2 mb-2">
              <span className="text-5xl font-bold text-green-600">{compatibilityData.overallMatch}%</span>
              <ThumbsUp className="w-8 h-8 text-green-500" />
            </div>
            <p className="text-lg font-medium text-gray-800">
              {compatibilityData.user.name} & {compatibilityData.partner.name}
            </p>
            <p className="text-sm text-gray-600">are a good match</p>
            
            <button className="mt-4 text-xs text-green-600 font-medium flex items-center gap-1 mx-auto">
              <Plus className="w-4 h-4" />
              Invite Alia to see this report
            </button>
          </div>
        </div>
      </div>

      {/* Compatibility based on parameters */}
      <div className="px-4 pb-4">
        <p className="text-xs text-gray-500 mb-3">Compatibility based on parameters</p>
        
        <div className="space-y-3">
          {compatibilityData.detailedScores.map((score, i) => (
            <div key={i} className="flex items-center gap-3">
              <span className="text-xs text-gray-600 w-16">{score.category}</span>
              <div className="flex-1 h-2 bg-gray-100 rounded-full overflow-hidden">
                <div
                  className={`h-full rounded-full transition-all duration-500 ${
                    score.score >= 90 ? 'bg-green-500' :
                    score.score >= 80 ? 'bg-amber-500' : 'bg-orange-500'
                  }`}
                  style={{ width: `${score.score}%` }}
                ></div>
              </div>
              <span className="text-xs font-medium text-gray-700 w-10">{score.score}%</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default CompatibilityScreen;
