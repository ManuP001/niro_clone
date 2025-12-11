import React from 'react';
import { FileText, BarChart3 } from 'lucide-react';

const OtherFeaturesSection = () => {
  return (
    <section className="bg-white py-20">
      <div className="max-w-6xl mx-auto px-4">
        <h2 className="text-4xl md:text-5xl font-serif text-gray-900 mb-12 text-center">
          Other features on <span className="text-amber-500">AstroSure.ai</span>
        </h2>

        <div className="grid md:grid-cols-2 gap-8">
          {/* Generate Reports */}
          <div className="bg-gradient-to-br from-amber-50 to-orange-50 rounded-3xl p-8 hover:shadow-xl transition-shadow duration-300">
            <div className="flex items-start gap-4">
              <div className="bg-white rounded-2xl p-3 shadow-md">
                <FileText className="w-8 h-8 text-amber-600" />
              </div>
              <div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">Generate Reports</h3>
                <p className="text-gray-600 leading-relaxed">
                  Get personalized astrological insights, forecasts, compatibility analysis, 
                  and Vedic guidance in one detailed report.
                </p>
              </div>
            </div>
            <div className="mt-6">
              <img
                src="https://images.unsplash.com/photo-1554224155-6726b3ff858f?w=600&h=400&fit=crop"
                alt="Reports"
                className="w-full h-48 object-cover rounded-2xl"
              />
            </div>
          </div>

          {/* Generate Life Charts */}
          <div className="bg-gradient-to-br from-indigo-50 to-purple-50 rounded-3xl p-8 hover:shadow-xl transition-shadow duration-300">
            <div className="flex items-start gap-4">
              <div className="bg-white rounded-2xl p-3 shadow-md">
                <BarChart3 className="w-8 h-8 text-indigo-600" />
              </div>
              <div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">Generate your life charts</h3>
                <p className="text-gray-600 leading-relaxed">
                  Create in-depth, personalized birth charts with insights into life events, 
                  relationships, and Vedic timelines.
                </p>
              </div>
            </div>
            <div className="mt-6">
              <img
                src="https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=600&h=400&fit=crop"
                alt="Life Charts"
                className="w-full h-48 object-cover rounded-2xl"
              />
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default OtherFeaturesSection;
