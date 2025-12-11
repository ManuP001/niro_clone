import React from 'react';
import { Share2, MapPin, Sun, Moon, Sunrise, Sunset, Clock } from 'lucide-react';
import { panchangData } from '../../data/mockData';

const PanchangScreen = () => {
  return (
    <div className="h-full bg-white overflow-y-auto">
      {/* Header */}
      <div className="px-4 pt-2 pb-4 bg-gradient-to-b from-green-50 to-white">
        <div className="flex items-center justify-between mb-2">
          <h1 className="text-lg font-semibold text-gray-800">Panchang</h1>
          <button className="text-gray-500">
            <Share2 className="w-5 h-5" />
          </button>
        </div>
        
        {/* Date & Location */}
        <div className="flex items-center gap-4">
          <div className="bg-amber-500 text-white px-3 py-1.5 rounded-lg text-sm font-medium">
            {panchangData.date}
          </div>
          <div className="flex items-center gap-1 text-gray-600">
            <MapPin className="w-4 h-4" />
            <span className="text-sm">{panchangData.location}</span>
          </div>
        </div>
      </div>

      {/* Main Info Grid */}
      <div className="px-4 mb-4">
        <div className="grid grid-cols-2 gap-3">
          <InfoCard label="Tithi" value={panchangData.tithi} />
          <InfoCard label="Nakshatra" value={panchangData.nakshatra} />
          <InfoCard label="Yoga" value={panchangData.yoga} />
          <InfoCard label="Karana" value={panchangData.karana} />
        </div>
      </div>

      {/* Sun & Moon Times */}
      <div className="px-4 mb-4">
        <div className="bg-gradient-to-r from-orange-50 to-amber-50 rounded-xl p-4">
          <div className="grid grid-cols-2 gap-4 mb-4">
            <TimeCard icon={<Sunrise className="w-4 h-4 text-orange-500" />} label="Sunrise" value={panchangData.sunrise} />
            <TimeCard icon={<Sunset className="w-4 h-4 text-orange-600" />} label="Sunset" value={panchangData.sunset} />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <TimeCard icon={<Sun className="w-4 h-4 text-amber-500" />} label="Sun sign" value={panchangData.sunSign} />
            <TimeCard icon={<Moon className="w-4 h-4 text-indigo-400" />} label="Moon sign" value={panchangData.moonSign} />
          </div>
        </div>
      </div>

      {/* Auspicious Times */}
      <div className="px-4 mb-4">
        <h3 className="text-sm font-semibold text-gray-800 mb-2">Auspicious/Inauspicious</h3>
        <h4 className="text-xs text-gray-500 mb-2">Times</h4>
        
        <div className="space-y-2">
          {panchangData.auspiciousTimes.map((time, i) => (
            <div key={i} className="flex items-center gap-2 bg-green-50 rounded-lg px-3 py-2">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              <span className="text-xs text-gray-700">{time}</span>
            </div>
          ))}
          {panchangData.inauspiciousTimes.map((time, i) => (
            <div key={i} className="flex items-center gap-2 bg-red-50 rounded-lg px-3 py-2">
              <div className="w-2 h-2 bg-red-500 rounded-full"></div>
              <span className="text-xs text-gray-700">{time}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Festivals */}
      <div className="px-4 pb-4">
        <div className="bg-purple-50 rounded-xl p-3">
          <p className="text-xs text-purple-600 font-medium mb-1">Today&apos;s Festival</p>
          <p className="text-sm text-gray-800">{panchangData.festivals[0]}</p>
        </div>
      </div>
    </div>
  );
};

const InfoCard = ({ label, value }) => (
  <div className="bg-gray-50 rounded-xl p-3">
    <p className="text-xs text-gray-500 mb-1">{label}</p>
    <p className="text-sm font-medium text-gray-800 truncate">{value}</p>
  </div>
);

const TimeCard = ({ icon, label, value }) => (
  <div className="flex items-center gap-2">
    <div className="w-8 h-8 bg-white rounded-lg flex items-center justify-center shadow-sm">
      {icon}
    </div>
    <div>
      <p className="text-[10px] text-gray-500">{label}</p>
      <p className="text-xs font-medium text-gray-800">{value}</p>
    </div>
  </div>
);

export default PanchangScreen;
