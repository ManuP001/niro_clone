import React from 'react';
import { Button } from './ui/button';

const HoroscopeSection = () => {
  return (
    <section className="bg-gray-950 py-20 relative overflow-hidden">
      {/* Subtle gradient overlay */}
      <div className="absolute inset-0 bg-gradient-to-b from-gray-900 to-gray-950"></div>
      
      <div className="relative z-10 max-w-4xl mx-auto px-4 text-center">
        <p className="text-gray-400 mb-4">Daily predictions to keep you informed</p>
        
        <h2 className="text-4xl md:text-5xl lg:text-6xl font-serif text-white mb-6">
          Detailed <span className="text-amber-400 italic">horoscopes</span>
        </h2>
        
        <p className="text-gray-300 text-lg max-w-3xl mx-auto mb-10 leading-relaxed">
          Daily horoscope delivered straight to you with a dash of insight and a sprinkle of cosmic wisdom. 
          Get a clear picture of what the stars have planned for you, from love to career moves, 
          more than just vibes—it&apos;s the universe explained, made easy and fun!
        </p>

        {/* CTA Banner */}
        <div className="mt-12">
          <Button 
            className="bg-gradient-to-r from-amber-400 to-amber-500 hover:from-amber-500 hover:to-amber-600 text-gray-900 font-semibold px-8 py-6 rounded-full text-lg transition-all duration-300 shadow-lg hover:shadow-amber-400/25"
          >
            Try Agastyaa
          </Button>
        </div>
      </div>
    </section>
  );
};

export default HoroscopeSection;
