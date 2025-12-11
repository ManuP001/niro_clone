import React, { useState } from 'react';
import { Sun, Menu, X } from 'lucide-react';
import { Button } from './ui/button';

const Header = () => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <header className="fixed top-0 left-0 right-0 z-50 bg-white">
      {/* Main header */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <a href="/" className="flex items-center gap-1">
            <span className="text-xl font-semibold text-gray-900">Astro</span>
            <Sun className="w-6 h-6 text-amber-500" strokeWidth={2.5} />
            <span className="text-xl font-semibold text-gray-900">Sure</span>
            <span className="text-xl text-gray-500">.ai</span>
          </a>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center gap-6">
            <a href="#insights" className="text-gray-700 hover:text-gray-900 transition-colors font-medium">
              Insights
            </a>
            <Button 
              className="bg-amber-400 hover:bg-amber-500 text-gray-900 font-semibold px-6 rounded-full border-0"
            >
              Login / Sign-up
            </Button>
            <div className="flex items-center gap-2 text-gray-600">
              <span className="text-sm">Download for:</span>
              <a href="#" className="p-2 rounded-full border border-gray-200 hover:bg-gray-50 transition-colors">
                <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M17.523 15.3414C17.523 15.3414 15.3089 16.7148 12.0005 16.7148C8.69214 16.7148 6.47803 15.3414 6.47803 15.3414C4.29459 13.7227 3 10.8125 3 7.5C3 4.1875 4.29459 1.27734 6.47803 -0.341406C6.47803 -0.341406 8.69214 1.03203 12.0005 1.03203C15.3089 1.03203 17.523 -0.341406 17.523 -0.341406C19.7065 1.27734 21.001 4.1875 21.001 7.5C21.001 10.8125 19.7065 13.7227 17.523 15.3414Z" transform="translate(0, 4.5)"/>
                </svg>
              </a>
              <a href="#" className="p-2 rounded-full border border-gray-200 hover:bg-gray-50 transition-colors">
                <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M18.71 19.5C17.88 20.74 17 21.95 15.66 21.97C14.32 22 13.89 21.18 12.37 21.18C10.84 21.18 10.37 21.95 9.1 22C7.79 22.05 6.8 20.68 5.96 19.47C4.25 17 2.94 12.45 4.7 9.39C5.57 7.87 7.13 6.91 8.82 6.88C10.1 6.86 11.32 7.75 12.11 7.75C12.89 7.75 14.37 6.68 15.92 6.84C16.57 6.87 18.39 7.1 19.56 8.82C19.47 8.88 17.39 10.1 17.41 12.63C17.44 15.65 20.06 16.66 20.09 16.67C20.06 16.74 19.67 18.11 18.71 19.5ZM13 3.5C13.73 2.67 14.94 2.04 15.94 2C16.07 3.17 15.6 4.35 14.9 5.19C14.21 6.04 13.07 6.7 11.95 6.61C11.8 5.46 12.36 4.26 13 3.5Z"/>
                </svg>
              </a>
            </div>
          </nav>

          {/* Mobile menu button */}
          <button 
            className="md:hidden p-2"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          >
            {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>
      </div>

      {/* Yellow accent bar */}
      <div className="h-1 bg-amber-400"></div>

      {/* Mobile menu */}
      {mobileMenuOpen && (
        <div className="md:hidden bg-white border-b border-gray-200 px-4 py-4">
          <nav className="flex flex-col gap-4">
            <a href="#insights" className="text-gray-700 hover:text-gray-900 font-medium">
              Insights
            </a>
            <Button className="bg-amber-400 hover:bg-amber-500 text-gray-900 font-semibold rounded-full w-full">
              Login / Sign-up
            </Button>
            <div className="flex items-center gap-2 text-gray-600">
              <span className="text-sm">Download for:</span>
              <a href="#" className="p-2 rounded-full border border-gray-200">
                <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M3,20.5V3.5C3,2.91 3.34,2.39 3.84,2.15L13.69,12L3.84,21.85C3.34,21.6 3,21.09 3,20.5M16.81,15.12L6.05,21.34L14.54,12.85L16.81,15.12M20.16,10.81C20.5,11.08 20.75,11.5 20.75,12C20.75,12.5 20.53,12.9 20.18,13.18L17.89,14.5L15.39,12L17.89,9.5L20.16,10.81M6.05,2.66L16.81,8.88L14.54,11.15L6.05,2.66Z"/>
                </svg>
              </a>
              <a href="#" className="p-2 rounded-full border border-gray-200">
                <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M18.71 19.5C17.88 20.74 17 21.95 15.66 21.97C14.32 22 13.89 21.18 12.37 21.18C10.84 21.18 10.37 21.95 9.1 22C7.79 22.05 6.8 20.68 5.96 19.47C4.25 17 2.94 12.45 4.7 9.39C5.57 7.87 7.13 6.91 8.82 6.88C10.1 6.86 11.32 7.75 12.11 7.75C12.89 7.75 14.37 6.68 15.92 6.84C16.57 6.87 18.39 7.1 19.56 8.82C19.47 8.88 17.39 10.1 17.41 12.63C17.44 15.65 20.06 16.66 20.09 16.67C20.06 16.74 19.67 18.11 18.71 19.5ZM13 3.5C13.73 2.67 14.94 2.04 15.94 2C16.07 3.17 15.6 4.35 14.9 5.19C14.21 6.04 13.07 6.7 11.95 6.61C11.8 5.46 12.36 4.26 13 3.5Z"/>
                </svg>
              </a>
            </div>
          </nav>
        </div>
      )}
    </header>
  );
};

export default Header;
