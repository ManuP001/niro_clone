import React from 'react';
import { Scroll, Sparkles, Star } from 'lucide-react';
import { features } from '../data/mockData';

const iconMap = {
  scroll: Scroll,
  sparkles: Sparkles,
  star: Star,
};

const FeatureBadges = () => {
  return (
    <section className="bg-white py-8">
      <div className="max-w-6xl mx-auto px-4">
        <div className="flex flex-wrap justify-center gap-4">
          {features.map((feature) => {
            const Icon = iconMap[feature.icon];
            return (
              <div
                key={feature.id}
                className="flex items-center gap-2 bg-amber-50 border border-amber-200 rounded-full px-4 py-2"
              >
                <Icon className="w-4 h-4 text-amber-600" />
                <span className="text-sm text-gray-700">{feature.title}</span>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
};

export default FeatureBadges;
