import React, { useState } from 'react';
import { testimonials } from '../data/mockData';
import { ChevronLeft, ChevronRight, Star, Crown } from 'lucide-react';

const TestimonialsSection = () => {
  const [currentIndex, setCurrentIndex] = useState(0);

  const nextTestimonial = () => {
    setCurrentIndex((prev) => (prev + 1) % testimonials.length);
  };

  const prevTestimonial = () => {
    setCurrentIndex((prev) => (prev - 1 + testimonials.length) % testimonials.length);
  };

  const current = testimonials[currentIndex];

  return (
    <section className="bg-white py-20">
      <div className="max-w-4xl mx-auto px-4">
        <div className="text-center mb-12">
          <h2 className="text-4xl md:text-5xl font-serif text-gray-900 mb-4">
            When AI Meets Astrology – <span className="italic">Users Speak</span>
          </h2>
        </div>

        <div className="relative bg-gradient-to-br from-amber-50 to-orange-50 rounded-3xl p-8 md:p-12">
          {/* Premium Badge */}
          {current.isPremium && (
            <div className="absolute top-4 right-4 flex items-center gap-1 bg-amber-400 text-gray-900 px-3 py-1 rounded-full text-xs font-medium">
              <Crown className="w-3 h-3" />
              Premium Member
            </div>
          )}

          <div className="flex flex-col md:flex-row items-center gap-8">
            {/* Avatar */}
            <div className="flex-shrink-0">
              <img
                src={current.avatar}
                alt={current.name}
                className="w-24 h-24 rounded-full object-cover border-4 border-white shadow-lg"
              />
            </div>

            {/* Content */}
            <div className="text-center md:text-left">
              <div className="flex justify-center md:justify-start gap-1 mb-4">
                {[...Array(5)].map((_, i) => (
                  <Star key={i} className="w-5 h-5 text-amber-400 fill-amber-400" />
                ))}
              </div>
              <p className="text-gray-700 text-lg mb-4 italic">&ldquo;{current.text}&rdquo;</p>
              <p className="font-semibold text-gray-900">{current.name}</p>
            </div>
          </div>

          {/* Navigation */}
          <div className="flex justify-center gap-4 mt-8">
            <button
              onClick={prevTestimonial}
              className="p-2 rounded-full bg-white shadow-md hover:shadow-lg transition-shadow"
            >
              <ChevronLeft className="w-5 h-5 text-gray-600" />
            </button>
            <div className="flex items-center gap-2">
              {testimonials.map((_, idx) => (
                <div
                  key={idx}
                  className={`w-2 h-2 rounded-full transition-colors ${
                    idx === currentIndex ? 'bg-amber-500' : 'bg-gray-300'
                  }`}
                />
              ))}
            </div>
            <button
              onClick={nextTestimonial}
              className="p-2 rounded-full bg-white shadow-md hover:shadow-lg transition-shadow"
            >
              <ChevronRight className="w-5 h-5 text-gray-600" />
            </button>
          </div>
        </div>
      </div>
    </section>
  );
};

export default TestimonialsSection;
