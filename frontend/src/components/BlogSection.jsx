import React from 'react';
import { blogArticles } from '../data/mockData';
import { ArrowRight } from 'lucide-react';

const BlogSection = () => {
  return (
    <section className="bg-gray-50 py-20" id="insights">
      <div className="max-w-6xl mx-auto px-4">
        <div className="text-center mb-12">
          <h2 className="text-4xl md:text-5xl font-serif text-gray-900 mb-4">
            Agastyaa <span className="italic">speaks</span>
          </h2>
          <p className="text-gray-600">
            Expand your astrological knowledge with our latest articles
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-8">
          {blogArticles.map((article) => (
            <article
              key={article.id}
              className="bg-white rounded-2xl overflow-hidden shadow-md hover:shadow-xl transition-shadow duration-300 group cursor-pointer"
            >
              <div className="relative overflow-hidden">
                <img
                  src={article.image}
                  alt={article.title}
                  className="w-full h-48 object-cover group-hover:scale-105 transition-transform duration-500"
                />
              </div>
              <div className="p-6">
                <h3 className="font-semibold text-gray-900 mb-3 line-clamp-2 group-hover:text-amber-600 transition-colors">
                  {article.title}
                </h3>
                <div className="flex items-center gap-2 text-sm text-gray-500">
                  <span>{article.date}</span>
                  <span>•</span>
                  <span>{article.readTime}</span>
                </div>
              </div>
            </article>
          ))}
        </div>

        <div className="text-center mt-12">
          <a
            href="#"
            className="inline-flex items-center gap-2 text-amber-600 hover:text-amber-700 font-medium transition-colors"
          >
            View all
            <ArrowRight className="w-4 h-4" />
          </a>
        </div>
      </div>
    </section>
  );
};

export default BlogSection;
