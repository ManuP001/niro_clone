import React from 'react';
import { sampleQuestions } from '../data/mockData';
import { ExternalLink } from 'lucide-react';

const AgastyaaSection = () => {
  return (
    <section className="bg-gradient-to-b from-white to-amber-50 py-20 relative overflow-hidden">
      <div className="max-w-6xl mx-auto px-4">
        {/* Header */}
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-serif text-gray-900 mb-6">
            Ask anything, let{' '}
            <span className="text-amber-500 italic">Agastyaa</span> answer
          </h2>
          <p className="text-gray-600 max-w-2xl mx-auto text-lg leading-relaxed">
            Agastyaa leverages the power of AI to personalise the astrology experience for you.
          </p>
          <p className="text-gray-600 max-w-2xl mx-auto text-lg leading-relaxed mt-4">
            Agastyaa can answer all questions related to your life such as relationships, career, education, health and so on.
          </p>
        </div>

        {/* Questions Grid with Sun */}
        <div className="relative">
          {/* Central Sun Illustration */}
          <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-64 h-64 md:w-80 md:h-80">
            <div className="relative w-full h-full">
              {/* Dashed circle */}
              <div className="absolute inset-0 border-2 border-dashed border-amber-300 rounded-full"></div>
              {/* Sun glow */}
              <div className="absolute inset-8 bg-gradient-to-br from-amber-200 via-yellow-100 to-amber-100 rounded-full opacity-80 blur-sm"></div>
              <div className="absolute inset-12 bg-gradient-to-br from-amber-100 to-yellow-50 rounded-full"></div>
              {/* Inner decorative lines */}
              <svg className="absolute inset-0 w-full h-full" viewBox="0 0 200 200">
                <path d="M100 60 Q110 100 100 140" fill="none" stroke="#fcd34d" strokeWidth="1" opacity="0.5"/>
                <path d="M80 80 Q100 100 120 120" fill="none" stroke="#fcd34d" strokeWidth="1" opacity="0.5"/>
              </svg>
            </div>
          </div>

          {/* Question Bubbles */}
          <div className="grid grid-cols-2 gap-8 md:gap-16 relative z-10">
            {/* Top Left */}
            <div className="flex items-start gap-3 justify-end">
              <div className="bg-white rounded-2xl shadow-lg p-4 max-w-xs">
                <p className="text-gray-700 text-sm">{sampleQuestions[0].question}</p>
              </div>
              <img
                src={sampleQuestions[0].avatar}
                alt="User"
                className="w-10 h-10 rounded-full object-cover border-2 border-white shadow"
              />
            </div>

            {/* Top Right */}
            <div className="flex items-start gap-3">
              <img
                src={sampleQuestions[1].avatar}
                alt="User"
                className="w-10 h-10 rounded-full object-cover border-2 border-white shadow"
              />
              <div className="bg-white rounded-2xl shadow-lg p-4 max-w-xs">
                <p className="text-gray-700 text-sm">{sampleQuestions[1].question}</p>
              </div>
            </div>

            {/* Spacer for sun */}
            <div className="col-span-2 h-32 md:h-48"></div>

            {/* Bottom Left */}
            <div className="flex items-end gap-3 justify-end">
              <div className="bg-white rounded-2xl shadow-lg p-4 max-w-xs">
                <p className="text-gray-700 text-sm">{sampleQuestions[2].question}</p>
              </div>
              <img
                src={sampleQuestions[2].avatar}
                alt="User"
                className="w-10 h-10 rounded-full object-cover border-2 border-white shadow"
              />
            </div>

            {/* Bottom Right */}
            <div className="flex items-end gap-3">
              <img
                src={sampleQuestions[3].avatar}
                alt="User"
                className="w-10 h-10 rounded-full object-cover border-2 border-white shadow"
              />
              <div className="bg-white rounded-2xl shadow-lg p-4 max-w-xs">
                <p className="text-gray-700 text-sm">{sampleQuestions[3].question}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Link */}
        <div className="text-center mt-16">
          <a
            href="#"
            className="inline-flex items-center gap-2 text-gray-700 hover:text-gray-900 underline underline-offset-4 transition-colors"
          >
            The making of Agastyaa
            <ExternalLink className="w-4 h-4" />
          </a>
        </div>
      </div>
    </section>
  );
};

export default AgastyaaSection;
