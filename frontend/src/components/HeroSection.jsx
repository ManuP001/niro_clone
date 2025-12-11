import React from 'react';
import { Play } from 'lucide-react';

const HeroSection = () => {
  return (
    <section className="relative min-h-[85vh] flex items-center justify-center overflow-hidden">
      {/* Background Image */}
      <div className="absolute inset-0">
        <img
          src="https://images.unsplash.com/photo-1611095564350-2cbe940a8d99?w=1920&h=1080&fit=crop"
          alt="Person using phone"
          className="w-full h-full object-cover"
        />
        <div className="absolute inset-0 bg-black/30"></div>
      </div>

      {/* Content */}
      <div className="relative z-10 text-center px-4 max-w-4xl mx-auto">
        <h1 className="text-4xl md:text-5xl lg:text-6xl font-serif text-white mb-8 leading-tight">
          Your constant companion<br />for Vedic insights
        </h1>

        {/* Video Button */}
        <button className="group flex items-center gap-3 mx-auto bg-black/40 backdrop-blur-sm rounded-full px-6 py-3 hover:bg-black/60 transition-all duration-300">
          <div className="w-10 h-10 rounded-full overflow-hidden">
            <img
              src="https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=100&h=100&fit=crop"
              alt="Video thumbnail"
              className="w-full h-full object-cover"
            />
          </div>
          <span className="text-white font-medium">AstroSure story</span>
          <Play className="w-4 h-4 text-white fill-white" />
        </button>
      </div>
    </section>
  );
};

export default HeroSection;
