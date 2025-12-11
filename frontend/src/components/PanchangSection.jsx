import React from 'react';
import { panchangData } from '../data/mockData';
import { Calendar, Sunrise, Sunset, Moon, Clock } from 'lucide-react';

const PanchangSection = () => {
  return (
    <section className="bg-gradient-to-b from-amber-50 to-white py-20">
      <div className="max-w-6xl mx-auto px-4">
        <div className="grid md:grid-cols-2 gap-12 items-center">
          {/* Left Content */}
          <div>
            <p className="text-amber-600 font-medium mb-2">Panchang</p>
            <h2 className="text-4xl md:text-5xl font-serif text-gray-900 mb-6">
              Your calendar for <span className="italic">everything</span>
            </h2>
            <p className="text-gray-600 text-lg leading-relaxed">
              Your ultimate guide to choosing the most auspicious moments. Whether you&apos;re planning 
              a big event, a business deal, or just a fresh start. Navigate life&apos;s biggest 
              decisions with ease and precision!
            </p>
          </div>

          {/* Right - Panchang Card */}
          <div className="bg-white rounded-3xl shadow-xl p-6 border border-gray-100">
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-2">
                <Calendar className="w-5 h-5 text-amber-500" />
                <span className="font-semibold text-gray-900">{panchangData.date}</span>
              </div>
              <span className="text-xs bg-amber-100 text-amber-700 px-3 py-1 rounded-full">
                Today&apos;s Panchang
              </span>
            </div>

            <div className="grid grid-cols-2 gap-4 mb-6">
              <div className="bg-gray-50 rounded-xl p-4">
                <p className="text-xs text-gray-500 mb-1">Tithi</p>
                <p className="font-medium text-gray-900 text-sm">{panchangData.tithi}</p>
              </div>
              <div className="bg-gray-50 rounded-xl p-4">
                <p className="text-xs text-gray-500 mb-1">Nakshatra</p>
                <p className="font-medium text-gray-900 text-sm">{panchangData.nakshatra}</p>
              </div>
              <div className="bg-gray-50 rounded-xl p-4">
                <p className="text-xs text-gray-500 mb-1">Yoga</p>
                <p className="font-medium text-gray-900 text-sm">{panchangData.yoga}</p>
              </div>
              <div className="bg-gray-50 rounded-xl p-4">
                <p className="text-xs text-gray-500 mb-1">Karana</p>
                <p className="font-medium text-gray-900 text-sm">{panchangData.karana}</p>
              </div>
            </div>

            <div className="border-t border-gray-100 pt-4">
              <div className="flex justify-between items-center mb-3">
                <div className="flex items-center gap-2">
                  <Sunrise className="w-4 h-4 text-orange-500" />
                  <span className="text-sm text-gray-600">Sunrise</span>
                </div>
                <span className="text-sm font-medium text-gray-900">{panchangData.sunrise}</span>
              </div>
              <div className="flex justify-between items-center mb-3">
                <div className="flex items-center gap-2">
                  <Sunset className="w-4 h-4 text-orange-600" />
                  <span className="text-sm text-gray-600">Sunset</span>
                </div>
                <span className="text-sm font-medium text-gray-900">{panchangData.sunset}</span>
              </div>
              <div className="flex justify-between items-center mb-3">
                <div className="flex items-center gap-2">
                  <Moon className="w-4 h-4 text-indigo-500" />
                  <span className="text-sm text-gray-600">Moonrise</span>
                </div>
                <span className="text-sm font-medium text-gray-900">{panchangData.moonrise}</span>
              </div>
              <div className="flex justify-between items-center">
                <div className="flex items-center gap-2">
                  <Clock className="w-4 h-4 text-red-500" />
                  <span className="text-sm text-gray-600">Rahu Kaal</span>
                </div>
                <span className="text-sm font-medium text-red-600">{panchangData.rahuKaal}</span>
              </div>
            </div>

            <div className="mt-4 pt-4 border-t border-gray-100 flex justify-between">
              <div>
                <p className="text-xs text-gray-500">Lucky Color</p>
                <p className="font-medium text-gray-900">{panchangData.luckyColor}</p>
              </div>
              <div className="text-right">
                <p className="text-xs text-gray-500">Lucky Number</p>
                <p className="font-medium text-gray-900">{panchangData.luckyNumber}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default PanchangSection;
