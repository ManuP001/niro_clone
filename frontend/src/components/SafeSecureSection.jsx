import React from 'react';
import { Shield, Lock } from 'lucide-react';
import { Button } from './ui/button';

const SafeSecureSection = () => {
  return (
    <section className="bg-gradient-to-b from-gray-50 to-white py-20">
      <div className="max-w-4xl mx-auto px-4 text-center">
        {/* Badge */}
        <div className="inline-flex items-center gap-2 bg-green-50 border border-green-200 rounded-full px-4 py-2 mb-8">
          <Shield className="w-4 h-4 text-green-600" />
          <span className="text-sm text-green-700 font-medium">SAFE & SECURE</span>
        </div>

        <h2 className="text-4xl md:text-5xl font-serif text-gray-900 mb-6">
          Your private AI companion for your <span className="italic">private</span> questions
        </h2>

        <p className="text-gray-600 text-lg max-w-2xl mx-auto mb-10 leading-relaxed">
          Let&apos;s be real—asking about your love life or career path can be a little awkward. 
          Agastyaa, your AI companion, lets you explore the stars with total privacy and confidence.
        </p>

        {/* Lock illustration */}
        <div className="flex justify-center mb-10">
          <div className="relative">
            <div className="w-24 h-24 bg-amber-100 rounded-full flex items-center justify-center">
              <Lock className="w-10 h-10 text-amber-600" />
            </div>
            <div className="absolute -inset-4 border-2 border-dashed border-amber-300 rounded-full animate-spin-slow"></div>
          </div>
        </div>

        {/* CTA */}
        <Button 
          className="bg-gradient-to-r from-amber-400 to-amber-500 hover:from-amber-500 hover:to-amber-600 text-gray-900 font-semibold px-8 py-6 rounded-full text-lg transition-all duration-300 shadow-lg hover:shadow-amber-400/25"
        >
          Try Agastyaa
        </Button>
      </div>
    </section>
  );
};

export default SafeSecureSection;
