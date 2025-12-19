import React from 'react';

const MobileFrame = ({ children }) => {
  return (
    <div className="relative">
      {/* Phone frame */}
      <div className="w-[375px] h-[812px] bg-white rounded-[3rem] shadow-2xl overflow-hidden border-[14px] border-gray-900 relative">
        {/* Notch */}
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[150px] h-[30px] bg-gray-900 rounded-b-3xl z-50 flex items-center justify-center">
          <div className="w-[60px] h-[4px] bg-gray-700 rounded-full"></div>
        </div>
        
        {/* Status bar */}
        <div className="h-[44px] bg-white flex items-end justify-between px-6 pb-1 text-xs font-medium">
          <span>9:41</span>
          <div className="flex items-center gap-1">
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12.33 4.67L18 10.33V20H6V10.33L12.33 4.67M12.33 2L4 10.33V22H20V10.33L12.33 2Z"/>
            </svg>
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
              <path d="M1 9l2 2c4.97-4.97 13.03-4.97 18 0l2-2C16.93 2.93 7.08 2.93 1 9zm8 8l3 3 3-3c-1.65-1.66-4.34-1.66-6 0zm-4-4l2 2c2.76-2.76 7.24-2.76 10 0l2-2C15.14 9.14 8.87 9.14 5 13z"/>
            </svg>
            <div className="flex items-center">
              <div className="w-6 h-3 border border-current rounded-sm relative">
                <div className="absolute inset-0.5 bg-current rounded-sm" style={{width: '80%'}}></div>
              </div>
            </div>
          </div>
        </div>
        
        {/* Content */}
        <div className="h-[calc(100%-44px)] overflow-hidden">
          {children}
        </div>
      </div>
    </div>
  );
};

export default MobileFrame;
