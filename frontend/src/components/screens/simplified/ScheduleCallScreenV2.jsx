import React, { useState, useEffect } from 'react';
import { colors, shadows } from './theme';
import { trackEvent } from './utils';
import { BACKEND_URL } from '../../../config';
import PreBookingQuestionsScreen from './PreBookingQuestionsScreen';

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

// Format a Date as YYYY-MM-DD using local timezone (avoids UTC date shifting for IST users)
const toLocalDateStr = (date) => {
  const y = date.getFullYear();
  const m = String(date.getMonth() + 1).padStart(2, '0');
  const d = String(date.getDate()).padStart(2, '0');
  return `${y}-${m}-${d}`;
};

// Generate next 14 days starting from today
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

const TZ_LABELS = {
  'Asia/Kolkata': 'IST',
  'Asia/Dubai': 'GST',
  'Asia/Singapore': 'SGT',
  'UTC': 'UTC',
  'America/New_York': 'ET',
  'America/Los_Angeles': 'PT',
  'Europe/London': 'GMT',
};

const FEATURED_REMEDIES = [
  { id: 'chakra_balance', emoji: '🧘', title: 'Chakra Balance Program', price: '₹3,500' },
  { id: 'navgraha_shanti', emoji: '🙏', title: 'Navgraha Shanti Pooja', price: '₹5,000' },
  { id: 'yellow_sapphire', emoji: '💎', title: 'Yellow Sapphire (Pukhraj)', price: '₹4,200' },
];

export default function ScheduleCallScreen({ token, user, onBack, onComplete, onNavigate, expertId, topicId, expertName }) {
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [selectedSlot, setSelectedSlot] = useState(null);
  const [timeSlots, setTimeSlots] = useState([]);
  const [slotsLoading, setSlotsLoading] = useState(false);
  const [isBooking, setIsBooking] = useState(false);
  const [bookingComplete, setBookingComplete] = useState(false);
  const [bookingDetails, setBookingDetails] = useState(null);
  const [error, setError] = useState(null);
  const [slotTimezone, setSlotTimezone] = useState('Asia/Kolkata');
  // subStep: 'questions' → 'slots' → confirmation
  const [subStep, setSubStep] = useState('questions');
  const [bookingQuestions, setBookingQuestions] = useState([]);
  const [phoneNumber, setPhoneNumber] = useState(user?.phone || '');

  const dates = generateDates();

  // Load time slots when date changes; auto-advance past today if no slots remain
  useEffect(() => {
    const fetchSlots = async () => {
      setSlotsLoading(true);
      try {
        // Use local date string (not UTC) so IST users get the correct date
        const dateStr = toLocalDateStr(selectedDate);
        const url = `${BACKEND_URL}/api/bookings/available-slots?date=${dateStr}`;
        const res = await fetch(url);
        const data = await res.json();
        const slots = data.ok ? data.slots : [];
        if (data.timezone) setSlotTimezone(data.timezone);

        if (slots.length === 0) {
          // If no slots for today (past business hours), advance to the next day
          const today = new Date();
          const isCurrentOrPast = selectedDate <= today;
          if (isCurrentOrPast) {
            const next = new Date(selectedDate);
            next.setDate(next.getDate() + 1);
            setSelectedDate(next);
            return; // useEffect will re-run with new date
          }
        }
        setTimeSlots(slots);
      } catch {
        setTimeSlots([]);
      } finally {
        setSlotsLoading(false);
        setSelectedSlot(null);
      }
    };
    fetchSlots();
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
        expert_id: expertId || null,
        topic_id: topicId || null,
        questions: bookingQuestions,
        user_phone: phoneNumber || user?.phone || '',
      };
      
      // Save booking to backend (use direct API call, not apiSimplified)
      const res = await fetch(`${BACKEND_URL}/api/bookings/schedule`, {
        method: 'POST',
        headers: {
          'Authorization': token ? `Bearer ${token}` : '',
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(bookingData),
      });
      const response = await res.json();

      if (!res.ok) {
        throw new Error(response.detail || response.message || 'Failed to schedule call');
      }

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
  
  // Show questions sub-step
  if (subStep === 'questions') {
    return (
      <PreBookingQuestionsScreen
        expertName={expertName}
        onBack={onBack || (() => window.history.back())}
        onSubmit={(qs) => {
          setBookingQuestions(qs);
          setSubStep('slots');
        }}
      />
    );
  }

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
            
            {/* Remedies Upsell */}
            <div
              className="rounded-2xl p-5 mb-6 text-left"
              style={{ backgroundColor: '#FFFFFF', boxShadow: shadows.card }}
            >
              <h3 className="font-semibold mb-1" style={{ color: colors.text.dark }}>
                Enhance your journey with Niro
              </h3>
              <p className="text-xs mb-4" style={{ color: colors.text.muted }}>
                Deepen your transformation with these popular remedies
              </p>
              <div className="space-y-3">
                {FEATURED_REMEDIES.map((r) => (
                  <div
                    key={r.id}
                    className="flex items-center gap-3 p-3 rounded-xl"
                    style={{ backgroundColor: colors.cream.warm }}
                  >
                    <span className="text-2xl">{r.emoji}</span>
                    <div className="flex-1">
                      <p className="text-sm font-medium" style={{ color: colors.text.dark }}>{r.title}</p>
                    </div>
                    <span className="text-sm font-semibold" style={{ color: colors.teal.primary }}>{r.price}</span>
                  </div>
                ))}
              </div>
              <button
                onClick={() => onNavigate ? onNavigate('remedies') : (window.location.href = '/app/remedies')}
                className="mt-4 w-full py-3 rounded-full text-sm font-semibold border transition-all hover:shadow-md"
                style={{ borderColor: colors.teal.primary, color: colors.teal.primary, backgroundColor: 'transparent' }}
              >
                Explore all remedies →
              </button>
            </div>

            {/* Actions */}
            <button
              onClick={() => {
                if (onComplete) {
                  onComplete();
                } else {
                  window.location.href = '/app/mypack';
                }
              }}
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
        <div>
          <h1 className="text-lg font-semibold" style={{ color: colors.text.dark }}>
            Schedule Your Free Call
          </h1>
          {expertName && (
            <p className="text-sm mt-0.5" style={{ color: colors.teal.primary }}>
              with {expertName}
            </p>
          )}
        </div>
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
            <div className="flex items-baseline gap-2 mb-3">
              <h3 className="text-sm font-medium" style={{ color: colors.text.dark }}>
                Select Time
              </h3>
              <span className="text-xs" style={{ color: colors.text.muted }}>
                All times in {TZ_LABELS[slotTimezone] || slotTimezone}
              </span>
            </div>
            {slotsLoading ? (
              <div className="flex items-center justify-center py-8">
                <div
                  className="w-8 h-8 border-4 rounded-full animate-spin"
                  style={{ borderColor: `${colors.teal.primary}30`, borderTopColor: colors.teal.primary }}
                />
              </div>
            ) : (
              <>
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
              </>
            )}
          </div>
          
          {/* Phone Number */}
          <div className="mb-5">
            <label className="block text-sm font-medium mb-2" style={{ color: colors.text.dark }}>
              WhatsApp number <span style={{ color: '#dc2626', fontWeight: 400 }}>*</span> <span style={{ color: colors.text.muted, fontWeight: 400 }}>(required for call confirmation)</span>
            </label>
            <input
              type="tel"
              value={phoneNumber}
              onChange={(e) => setPhoneNumber(e.target.value)}
              placeholder="+91 98765 43210"
              className="w-full rounded-xl px-4 py-3 text-sm outline-none"
              style={{
                backgroundColor: '#FFFFFF',
                border: `1.5px solid ${phoneNumber.replace(/\D/g, '').length >= 10 ? colors.teal.primary : colors.ui.borderDark}`,
                color: colors.text.dark,
              }}
            />
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
            disabled={!selectedSlot || phoneNumber.replace(/\D/g, '').length < 10 || isBooking}
            className={`w-full py-4 rounded-full font-semibold text-base transition-all ${
              selectedSlot && phoneNumber.replace(/\D/g, '').length >= 10 && !isBooking ? 'hover:shadow-lg hover:-translate-y-0.5' : 'opacity-50 cursor-not-allowed'
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
