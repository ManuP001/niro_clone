import React, { useState, useEffect, useRef } from 'react';
import { colors, shadows } from './theme';

/**
 * BannerCarousel - Scrollable promotional banners
 * 
 * Features:
 * - Auto-scroll every 5 seconds
 * - Manual swipe/scroll on mobile
 * - Dot indicators
 * - Optimized for both mobile and desktop
 */

const DEFAULT_BANNERS = [
  {
    id: 'free_call',
    title: 'Get Your Free 10-Min Call',
    subtitle: 'Talk to a Vedic astrologer today',
    cta: 'Book Now',
    ctaAction: 'schedule',
    bgGradient: `linear-gradient(135deg, ${colors.teal.primary} 0%, ${colors.teal.soft} 100%)`,
    textColor: '#FFFFFF',
  },
  {
    id: 'experts',
    title: 'Meet Our Expert Astrologers',
    subtitle: 'Only 4.5+ rated professionals',
    cta: 'Browse Experts',
    ctaAction: 'experts',
    bgGradient: `linear-gradient(135deg, ${colors.peach.primary} 0%, ${colors.peach.soft} 100%)`,
    textColor: colors.text.dark,
  },
  {
    id: 'remedies',
    title: 'Remedies That Work',
    subtitle: 'Curated solutions for your concerns',
    cta: 'Explore Remedies',
    ctaAction: 'remedies',
    bgGradient: `linear-gradient(135deg, #7C9A92 0%, ${colors.teal.soft} 100%)`,
    textColor: '#FFFFFF',
  },
];

export default function BannerCarousel({ 
  banners = DEFAULT_BANNERS, 
  onBannerClick,
  autoScrollInterval = 5000,
}) {
  const [activeIndex, setActiveIndex] = useState(0);
  const scrollContainerRef = useRef(null);
  const autoScrollRef = useRef(null);

  // Auto-scroll effect
  useEffect(() => {
    if (banners.length <= 1) return;

    autoScrollRef.current = setInterval(() => {
      setActiveIndex((prev) => (prev + 1) % banners.length);
    }, autoScrollInterval);

    return () => {
      if (autoScrollRef.current) {
        clearInterval(autoScrollRef.current);
      }
    };
  }, [banners.length, autoScrollInterval]);

  // Scroll to active banner when activeIndex changes
  useEffect(() => {
    if (scrollContainerRef.current) {
      const container = scrollContainerRef.current;
      const bannerWidth = container.offsetWidth;
      container.scrollTo({
        left: activeIndex * bannerWidth,
        behavior: 'smooth',
      });
    }
  }, [activeIndex]);

  // Handle manual scroll
  const handleScroll = () => {
    if (scrollContainerRef.current) {
      const container = scrollContainerRef.current;
      const scrollLeft = container.scrollLeft;
      const bannerWidth = container.offsetWidth;
      const newIndex = Math.round(scrollLeft / bannerWidth);
      
      if (newIndex !== activeIndex && newIndex >= 0 && newIndex < banners.length) {
        setActiveIndex(newIndex);
        
        // Reset auto-scroll timer on manual interaction
        if (autoScrollRef.current) {
          clearInterval(autoScrollRef.current);
          autoScrollRef.current = setInterval(() => {
            setActiveIndex((prev) => (prev + 1) % banners.length);
          }, autoScrollInterval);
        }
      }
    }
  };

  const handleBannerClick = (banner) => {
    if (onBannerClick) {
      onBannerClick(banner.ctaAction, banner);
    }
  };

  return (
    <div className="w-full" data-testid="banner-carousel">
      {/* Banner Container */}
      <div
        ref={scrollContainerRef}
        className="flex overflow-x-auto snap-x snap-mandatory scrollbar-hide"
        style={{ 
          scrollSnapType: 'x mandatory',
          WebkitOverflowScrolling: 'touch',
        }}
        onScroll={handleScroll}
      >
        {banners.map((banner, index) => (
          <div
            key={banner.id}
            className="flex-shrink-0 w-full snap-center px-4 py-3"
            style={{ scrollSnapAlign: 'center' }}
          >
            <div
              className="relative rounded-2xl p-5 md:p-6 cursor-pointer transition-all hover:shadow-lg active:scale-[0.99]"
              style={{ 
                background: banner.bgGradient,
                minHeight: '140px',
              }}
              onClick={() => handleBannerClick(banner)}
              data-testid={`banner-${banner.id}`}
            >
              {/* Content */}
              <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                <div className="flex-1">
                  <h3 
                    className="text-lg md:text-xl font-bold mb-1"
                    style={{ color: banner.textColor }}
                  >
                    {banner.title}
                  </h3>
                  <p 
                    className="text-sm md:text-base opacity-90"
                    style={{ color: banner.textColor }}
                  >
                    {banner.subtitle}
                  </p>
                </div>
                
                {/* CTA Button */}
                <button
                  className="self-start md:self-center px-5 py-2.5 rounded-full font-semibold text-sm transition-all hover:shadow-md active:scale-95"
                  style={{ 
                    backgroundColor: banner.textColor === '#FFFFFF' ? 'rgba(255,255,255,0.95)' : colors.teal.primary,
                    color: banner.textColor === '#FFFFFF' ? colors.text.dark : '#FFFFFF',
                  }}
                  onClick={(e) => {
                    e.stopPropagation();
                    handleBannerClick(banner);
                  }}
                >
                  {banner.cta}
                </button>
              </div>

              {/* Decorative element */}
              <div 
                className="absolute top-3 right-3 w-16 h-16 rounded-full opacity-20"
                style={{ 
                  background: banner.textColor === '#FFFFFF' 
                    ? 'rgba(255,255,255,0.3)' 
                    : 'rgba(0,0,0,0.1)',
                }}
              />
            </div>
          </div>
        ))}
      </div>

      {/* Dot Indicators */}
      {banners.length > 1 && (
        <div className="flex justify-center gap-2 mt-2 pb-2">
          {banners.map((_, index) => (
            <button
              key={index}
              className="w-2 h-2 rounded-full transition-all"
              style={{ 
                backgroundColor: index === activeIndex 
                  ? colors.teal.primary 
                  : 'rgba(0,0,0,0.15)',
                transform: index === activeIndex ? 'scale(1.2)' : 'scale(1)',
              }}
              onClick={() => setActiveIndex(index)}
              aria-label={`Go to banner ${index + 1}`}
            />
          ))}
        </div>
      )}

      {/* Hide scrollbar styles */}
      <style>{`
        .scrollbar-hide {
          -ms-overflow-style: none;
          scrollbar-width: none;
        }
        .scrollbar-hide::-webkit-scrollbar {
          display: none;
        }
      `}</style>
    </div>
  );
}
