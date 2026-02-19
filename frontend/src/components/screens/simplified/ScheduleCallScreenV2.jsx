import React, { useState, useEffect } from 'react';
import { colors, shadows } from './theme';
import { apiSimplified, trackEvent } from './utils';

/**
 * ScheduleCallScreen V2 - Embedded scheduling experience
 * 
 * Features:
 * - In-app date/time selection
 * - Available slots from backend
 * - Booking confirmation stored in database
 * - View scheduled calls in My Pack
 */

// Generate time slots for a given date
const generateTimeSlots = (date) => {
  const slots = [];
  const today = new Date();
  const isToday = date.toDateString() === today.toDateString();
  const currentHour = today.getHours();
  
  // Slots from 9 AM to 8 PM
  for (let hour = 9; hour <= 20; hour++) {
    // Skip past times for today
    if (isToday && hour <= currentHour) continue;
    
    const time = `${hour.toString().padStart(2, '0')}:00`;
    const displayTime = hour > 12 
      ? `${hour - 12}:00 PM` 
      : hour === 12 
        ? '12:00 PM' 
        : `${hour}:00 AM`;
    
    slots.push({
      time,
      displayTime,
      available: Math.random() > 0.3, // 70% chance of availability (to be replaced with real data)
    });
  }
  
  return slots;
};

// Generate next 14 days
const generateDates = () => {
  const dates = [];
  const today = new Date();
  
  for (let i = 0; i < 14; i++) {
    const date = new Date(today);
    date.setDate(today.getDate() + i);
    dates.push(date);
  }
  
  return dates;
};

const formatDate = (date) => {
  const options = { weekday: 'short', day: 'numeric', month: 'short' };
  return date.toLocaleDateString('en-US', options);
};

const isToday = (date) => {
  const today = new Date();
  return date.toDateString() === today.toDateString();
};

const isTomorrow = (date) => {
  const tomorrow = new Date();
  tomorrow.setDate(tomorrow.getDate() + 1);
  return date.toDateString() === tomorrow.toDateString();
};

export default function ScheduleCallScreen({ token, user, onBack, onComplete }) {
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [selectedSlot, setSelectedSlot] = useState(null);
  const [timeSlots, setTimeSlots] = useState([]);
  const [isBooking, setIsBooking] = useState(false);
  const [bookingComplete, setBookingComplete] = useState(false);
  const [bookingDetails, setBookingDetails] = useState(null);
  const [error, setError] = useState(null);
  
  const dates = generateDates();
  
  // Load time slots when date changes
  useEffect(() => {
    setTimeSlots(generateTimeSlots(selectedDate));
    setSelectedSlot(null);
  }, [selectedDate]);
  
  const handleBooking = async () => {
    if (!selectedSlot) return;
    
    setIsBooking(true);
    setError(null);
    
    try {
      // Format the booking date/time
      const bookingDate = new Date(selectedDate);
      const [hours] = selectedSlot.time.split(':');
      bookingDate.setHours(parseInt(hours), 0, 0, 0);
      
      const bookingData = {
        scheduled_date: bookingDate.toISOString(),
        duration_minutes: 10,
        call_type: 'free_consultation',
        user_name: user?.name || 'User',
        user_email: user?.email || '',
        notes: 'Free 10-minute consultation call',
      };
      
      // Save booking to backend
      const response = await apiSimplified.post('/bookings/schedule', bookingData, token);
      
      if (response.ok) {
        setBookingDetails({
          id: response.booking_id,
          date: bookingDate,
          time: selectedSlot.displayTime,
        });
        setBookingComplete(true);
        trackEvent('call_scheduled', { 
          date: bookingDate.toISOString(),
          type: 'free_consultation' 
        });
      } else {
        throw new Error(response.message || 'Failed to schedule call');
      }
    } catch (err) {
      console.error('Booking error:', err);
      setError(err.message || 'Failed to schedule call. Please try again.');
    } finally {
      setIsBooking(false);
    }
  };
  
  // Show booking confirmation
  if (bookingComplete && bookingDetails) {
    return (
      <div 
        className="min-h-screen flex flex-col"
        style={{ backgroundColor: colors.background.primary }}
      >
        {/* Header */}
        <header className="sticky top-0 z-40 px-4 py-4 flex items-center gap-4" style={{ backgroundColor: colors.background.primary }}>
          <h1 className="text-lg font-semibold" style={{ color: colors.text.dark }}>
            Booking Confirmed
          </h1>
        </header>

        {/* Content */}
        <div className="flex-1 px-4 py-8">
          <div className="max-w-lg mx-auto text-center">
            {/* Success Icon */}
            <div 
              className="w-24 h-24 rounded-full mx-auto mb-6 flex items-center justify-center"
              style={{ backgroundColor: `${colors.teal.primary}15` }}
            >
              <svg className="w-12 h-12" style={{ color: colors.teal.primary }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
            
            <h2 className="text-2xl font-bold mb-2" style={{ color: colors.text.dark }}>
              You're all set!
            </h2>
            <p className="text-base mb-8" style={{ color: colors.text.secondary }}>
              Your free consultation call has been scheduled.
            </p>
            
            {/* Booking Details Card */}
            <div 
              className="rounded-2xl p-6 mb-8 text-left"
              style={{ backgroundColor: '#FFFFFF', boxShadow: shadows.card }}
            >
              <h3 className="font-semibold mb-4" style={{ color: colors.text.dark }}>
                Call Details
              </h3>
              
              <div className="space-y-4">
                <div className="flex items-center gap-3">
                  <div 
                    className="w-10 h-10 rounded-full flex items-center justify-center"
                    style={{ backgroundColor: `${colors.teal.primary}15` }}
                  >
                    <svg className="w-5 h-5" style={{ color: colors.teal.primary }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                  </div>
                  <div>
                    <p className="text-sm" style={{ color: colors.text.muted }}>Date</p>
                    <p className="font-medium" style={{ color: colors.text.dark }}>
                      {bookingDetails.date.toLocaleDateString('en-US', { 
                        weekday: 'long', 
                        day: 'numeric', 
                        month: 'long', 
                        year: 'numeric' 
                      })}
                    </p>
                  </div>
                </div>
                
                <div className="flex items-center gap-3">
                  <div 
                    className="w-10 h-10 rounded-full flex items-center justify-center"
                    style={{ backgroundColor: `${colors.teal.primary}15` }}
                  >
                    <svg className="w-5 h-5" style={{ color: colors.teal.primary }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <div>
                    <p className="text-sm" style={{ color: colors.text.muted }}>Time</p>
                    <p className="font-medium" style={{ color: colors.text.dark }}>
                      {bookingDetails.time} (10 minutes)
                    </p>
                  </div>
                </div>
                
                <div className="flex items-center gap-3">
                  <div 
                    className="w-10 h-10 rounded-full flex items-center justify-center"
                    style={{ backgroundColor: `${colors.teal.primary}15` }}
                  >
                    <svg className="w-5 h-5" style={{ color: colors.teal.primary }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                    </svg>
                  </div>
                  <div>
                    <p className="text-sm" style={{ color: colors.text.muted }}>Call Type</p>
                    <p className="font-medium" style={{ color: colors.text.dark }}>
                      Free Consultation Call
                    </p>
                  </div>
                </div>
              </div>
              
              <div 
                className="mt-6 p-4 rounded-xl"
                style={{ backgroundColor: colors.cream.warm }}
              >
                <p className="text-sm" style={{ color: colors.text.secondary }}>
                  You'll receive a call from our Niro Expert Team at the scheduled time. 
                  Make sure your phone is nearby!
                </p>
              </div>
            </div>
            
            {/* Actions */}
            <button
              onClick={() => onComplete?.() || window.location.href = '/app/mypack'}
              className="w-full py-4 rounded-full font-semibold text-base transition-all hover:shadow-lg"
              style={{
                backgroundColor: colors.teal.primary,
                color: '#FFFFFF',
              }}
            >
              View My Scheduled Calls
            </button>
          </div>
        </div>
      </div>
    );
  }
  
  return (
    <div 
      className="min-h-screen flex flex-col"
      style={{ backgroundColor: colors.background.primary }}
    >
      {/* Header */}
      <header className="sticky top-0 z-40 px-4 py-4 flex items-center gap-4" style={{ backgroundColor: colors.background.primary }}>
        <button
          onClick={onBack || (() => window.history.back())}
          className="w-10 h-10 rounded-full flex items-center justify-center transition-all hover:bg-gray-100"
          style={{ backgroundColor: '#FFFFFF', boxShadow: shadows.card }}
          data-testid="schedule-back-btn"
        >
          <svg className="w-5 h-5" style={{ color: colors.text.dark }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
        </button>
        <h1 className="text-lg font-semibold" style={{ color: colors.text.dark }}>
          Schedule Your Free Call
        </h1>
      </header>

      {/* Content */}
      <div className="flex-1 px-4 py-4">
        <div className="max-w-lg mx-auto">
          {/* Info Card */}
          <div 
            className="rounded-2xl p-4 mb-6"
            style={{ backgroundColor: colors.cream.warm }}
          >
            <div className="flex items-center gap-3">
              <div 
                className="w-12 h-12 rounded-full flex items-center justify-center flex-shrink-0"
                style={{ backgroundColor: colors.teal.primary }}
              >
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                </svg>
              </div>
              <div>
                <p className="font-semibold" style={{ color: colors.text.dark }}>
                  Free 10-Minute Consultation
                </p>
                <p className="text-sm" style={{ color: colors.text.muted }}>
                  Select a convenient time for your call
                </p>
              </div>
            </div>
          </div>
          
          {/* Date Selection */}
          <div className="mb-6">
            <h3 className="text-sm font-medium mb-3" style={{ color: colors.text.dark }}>
              Select Date
            </h3>
            <div 
              className="flex gap-2 overflow-x-auto pb-2 scrollbar-hide"
              style={{ 
                WebkitOverflowScrolling: 'touch',
                scrollbarWidth: 'none',
                msOverflowStyle: 'none',
              }}
            >
              {dates.map((date) => {
                const isSelected = date.toDateString() === selectedDate.toDateString();
                return (
                  <button
                    key={date.toISOString()}
                    onClick={() => setSelectedDate(date)}
                    className="flex-shrink-0 px-4 py-3 rounded-xl text-center transition-all"
                    style={{
                      backgroundColor: isSelected ? colors.teal.primary : '#FFFFFF',
                      color: isSelected ? '#FFFFFF' : colors.text.dark,
                      boxShadow: isSelected ? shadows.teal : shadows.card,
                      minWidth: '80px',
                    }}
                  >
                    <p className="text-xs font-medium opacity-80">
                      {isToday(date) ? 'Today' : isTomorrow(date) ? 'Tomorrow' : date.toLocaleDateString('en-US', { weekday: 'short' })}
                    </p>
                    <p className="text-lg font-bold">
                      {date.getDate()}
                    </p>
                    <p className="text-xs">
                      {date.toLocaleDateString('en-US', { month: 'short' })}
                    </p>
                  </button>
                );
              })}
            </div>
          </div>
          
          {/* Time Selection */}
          <div className="mb-6">
            <h3 className="text-sm font-medium mb-3" style={{ color: colors.text.dark }}>
              Select Time
            </h3>
            <div className="grid grid-cols-3 gap-2">
              {timeSlots.map((slot) => {
                const isSelected = selectedSlot?.time === slot.time;
                return (
                  <button
                    key={slot.time}
                    onClick={() => slot.available && setSelectedSlot(slot)}
                    disabled={!slot.available}
                    className={`py-3 rounded-xl text-sm font-medium transition-all ${
                      !slot.available ? 'opacity-40 cursor-not-allowed' : 'hover:shadow-md'
                    }`}
                    style={{
                      backgroundColor: isSelected ? colors.teal.primary : '#FFFFFF',
                      color: isSelected ? '#FFFFFF' : slot.available ? colors.text.dark : colors.text.muted,
                      boxShadow: isSelected ? shadows.teal : shadows.card,
                    }}
                  >
                    {slot.displayTime}
                  </button>
                );
              })}
            </div>
            
            {timeSlots.length === 0 && (
              <p className="text-center text-sm py-8" style={{ color: colors.text.muted }}>
                No available slots for this date. Please select another date.
              </p>
            )}
          </div>
          
          {/* Error Message */}
          {error && (
            <div 
              className="rounded-xl p-4 mb-4"
              style={{ backgroundColor: `${colors.ui.error}15` }}
            >
              <p className="text-sm" style={{ color: colors.ui.error }}>{error}</p>
            </div>
          )}
          
          {/* CTA Button */}
          <button
            onClick={handleBooking}
            disabled={!selectedSlot || isBooking}
            className={`w-full py-4 rounded-full font-semibold text-base transition-all ${
              selectedSlot && !isBooking ? 'hover:shadow-lg hover:-translate-y-0.5' : 'opacity-50 cursor-not-allowed'
            }`}
            style={{
              backgroundColor: colors.peach.primary,
              color: colors.text.dark,
              boxShadow: selectedSlot ? shadows.peach : 'none',
            }}
            data-testid="confirm-booking-btn"
          >
            {isBooking ? (
              <span className="flex items-center justify-center gap-2">
                <svg className="animate-spin w-5 h-5" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Booking...
              </span>
            ) : (
              'Confirm Booking'
            )}
          </button>
          
          {selectedSlot && (
            <p className="text-center text-sm mt-3" style={{ color: colors.text.muted }}>
              {formatDate(selectedDate)} at {selectedSlot.displayTime}
            </p>
          )}
        </div>
      </div>
      
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
