import React from 'react';
import { Heart, Users, Briefcase } from 'lucide-react';

const CompatibilitySection = () => {
  return (
    <section className="bg-white py-20">
      <div className="max-w-6xl mx-auto px-4">
        <div className="grid md:grid-cols-2 gap-12 items-center">
          {/* Left - Visual */}
          <div className="relative">
            <div className="aspect-square max-w-md mx-auto relative">
              {/* Central cosmic circle */}
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="w-48 h-48 bg-gradient-to-br from-amber-100 to-amber-200 rounded-full opacity-60"></div>
              </div>
              
              {/* Floating elements */}
              <div className="absolute top-10 left-10 bg-white rounded-2xl shadow-lg p-4 animate-float">
                <Heart className="w-8 h-8 text-pink-500" />
                <p className="text-xs mt-2 text-gray-600">Love</p>
              </div>
              
              <div className="absolute top-10 right-10 bg-white rounded-2xl shadow-lg p-4 animate-float-delayed">
                <Users className="w-8 h-8 text-blue-500" />
                <p className="text-xs mt-2 text-gray-600">Friends</p>
              </div>
              
              <div className="absolute bottom-10 left-1/2 -translate-x-1/2 bg-white rounded-2xl shadow-lg p-4 animate-float">
                <Briefcase className="w-8 h-8 text-amber-500" />
                <p className="text-xs mt-2 text-gray-600">Business</p>
              </div>

              {/* Connection lines */}
              <svg className="absolute inset-0 w-full h-full" viewBox="0 0 400 400">
                <path d="M80 100 Q200 200 320 100" fill="none" stroke="#fcd34d" strokeWidth="1" strokeDasharray="5,5" opacity="0.5"/>
                <path d="M80 100 Q200 250 200 300" fill="none" stroke="#fcd34d" strokeWidth="1" strokeDasharray="5,5" opacity="0.5"/>
                <path d="M320 100 Q200 250 200 300" fill="none" stroke="#fcd34d" strokeWidth="1" strokeDasharray="5,5" opacity="0.5"/>
              </svg>
            </div>
          </div>

          {/* Right Content */}
          <div>
            <p className="text-amber-600 font-medium mb-2">Compatibility</p>
            <h2 className="text-4xl md:text-5xl font-serif text-gray-900 mb-6">
              Discover your cosmic <span className="italic">connections</span>
            </h2>
            <p className="text-gray-600 text-lg leading-relaxed">
              Find out how well your stars align with anyone—whether it&apos;s a partner, friend, 
              or even a whole group! Dive into detailed insights on love, friendship, or 
              business relationships, and explore compatibility like never before. From 
              one-on-one comparisons to group dynamics, let Vedic astrology help you make 
              a better decision.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
};

export default CompatibilitySection;
