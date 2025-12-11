import React from 'react';
import { whyAstrosureFeatures } from '../data/mockData';
import { Clock, User, Zap, Shield, Users } from 'lucide-react';

const iconMap = {
  clock: Clock,
  user: User,
  zap: Zap,
  shield: Shield,
  users: Users,
};

const WhyAstrosureSection = () => {
  return (
    <section className="bg-gradient-to-b from-gray-50 to-white py-20">
      <div className="max-w-6xl mx-auto px-4">
        <div className="grid md:grid-cols-2 gap-12 items-start">
          {/* Left - QR Code and Download */}
          <div className="bg-white rounded-3xl p-8 shadow-xl">
            <h2 className="text-3xl md:text-4xl font-serif text-gray-900 mb-8">
              Why <span className="text-amber-500">AstroSure.ai</span>
            </h2>
            
            <div className="flex items-center gap-6 mb-8">
              <div className="bg-gray-100 p-4 rounded-2xl">
                <div className="w-24 h-24 bg-gray-800 rounded-xl flex items-center justify-center">
                  <svg viewBox="0 0 100 100" className="w-20 h-20">
                    {/* Simplified QR code representation */}
                    <rect x="10" y="10" width="20" height="20" fill="white"/>
                    <rect x="70" y="10" width="20" height="20" fill="white"/>
                    <rect x="10" y="70" width="20" height="20" fill="white"/>
                    <rect x="40" y="40" width="20" height="20" fill="white"/>
                    <rect x="15" y="15" width="10" height="10" fill="#1a1a1a"/>
                    <rect x="75" y="15" width="10" height="10" fill="#1a1a1a"/>
                    <rect x="15" y="75" width="10" height="10" fill="#1a1a1a"/>
                  </svg>
                </div>
              </div>
              <a
                href="#"
                className="text-amber-600 hover:text-amber-700 font-medium underline underline-offset-4"
              >
                Try it now
              </a>
            </div>
          </div>

          {/* Right - Features */}
          <div className="space-y-6">
            {whyAstrosureFeatures.map((feature) => {
              const Icon = iconMap[feature.icon];
              return (
                <div
                  key={feature.id}
                  className="bg-white rounded-2xl p-6 shadow-md hover:shadow-lg transition-shadow duration-300"
                >
                  <div className="flex items-start gap-4">
                    <div className="bg-amber-100 rounded-xl p-3">
                      <Icon className="w-6 h-6 text-amber-600" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-900 mb-2">{feature.title}</h3>
                      <p className="text-gray-600 text-sm leading-relaxed">{feature.description}</p>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </section>
  );
};

export default WhyAstrosureSection;
