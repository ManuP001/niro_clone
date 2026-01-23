/**
 * NIRO V5 Checkout Screen
 * Step 7 in the 8-step onboarding flow
 * 
 * ⚠️ CRITICAL: This preserves the existing Razorpay payment logic!
 * Only the UI has been restyled to match V5 theme.
 */

import React, { useState, useCallback, useMemo, useEffect } from 'react';
import { colors, shadows } from '../theme';
import { getLandingPageContent, formatPriceInr } from '../v5Data/landingPageContent';

// Load Razorpay script
const loadRazorpayScript = () => {
  return new Promise((resolve) => {
    if (document.getElementById('razorpay-script')) {
      resolve(true);
      return;
    }
    const script = document.createElement('script');
    script.id = 'razorpay-script';
    script.src = 'https://checkout.razorpay.com/v1/checkout.js';
    script.onload = () => resolve(true);
    script.onerror = () => resolve(false);
    document.body.appendChild(script);
  });
};

// Order summary item
const OrderItem = ({ label, value, isTotal = false }) => (
  <div className={`flex items-center justify-between ${isTotal ? 'pt-3 border-t' : ''}`}
    style={{ borderColor: colors.ui.borderDark }}
  >
    <span 
      className={`${isTotal ? 'font-semibold' : ''}`}
      style={{ color: isTotal ? colors.text.dark : colors.text.secondary }}
    >
      {label}
    </span>
    <span 
      className={`${isTotal ? 'text-lg font-bold' : 'font-medium'}`}
      style={{ color: isTotal ? colors.teal.dark : colors.text.dark }}
    >
      {value}
    </span>
  </div>
);

export default function CheckoutScreenV5({
  subtopicSlug,
  tierName,
  birthDetails = {},
  onPaymentSuccess,
  onBack
}) {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [paymentStatus, setPaymentStatus] = useState('idle'); // idle, processing, success, error

  // Get content for this subtopic
  const content = useMemo(() => {
    return getLandingPageContent(subtopicSlug);
  }, [subtopicSlug]);

  const price = content?.tierCards?.[tierName]?.priceInr || 0;
  const duration = content?.tierCards?.[tierName]?.durationWeeks || 8;

  // Get API URL
  const apiUrl = process.env.REACT_APP_BACKEND_URL || '';

  // Load Razorpay script on mount
  useEffect(() => {
    loadRazorpayScript();
  }, []);

  // ⚠️ PRESERVED RAZORPAY PAYMENT LOGIC - DO NOT MODIFY ⚠️
  const handlePayment = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    setPaymentStatus('processing');

    try {
      // Create Razorpay order
      const tierId = `${subtopicSlug}_${tierName.toLowerCase()}`;
      const response = await fetch(`${apiUrl}/api/simplified/checkout/create-order`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          tier_id: tierId,
          amount: price,
          currency: 'INR'
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to create order');
      }

      const orderData = await response.json();

      // Open Razorpay checkout
      const razorpayLoaded = await loadRazorpayScript();
      if (!razorpayLoaded) {
        throw new Error('Failed to load payment gateway');
      }

      const options = {
        key: orderData.razorpay_key_id,
        amount: orderData.amount,
        currency: orderData.currency,
        name: 'NIRO',
        description: `${content?.subTopic || 'Astrology'} - ${tierName}`,
        order_id: orderData.order_id,
        handler: async function (response) {
          try {
            // Verify payment on backend
            const verifyResponse = await fetch(`${apiUrl}/api/simplified/checkout/verify-payment`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                razorpay_order_id: response.razorpay_order_id,
                razorpay_payment_id: response.razorpay_payment_id,
                razorpay_signature: response.razorpay_signature
              })
            });

            if (!verifyResponse.ok) {
              throw new Error('Payment verification failed');
            }

            const result = await verifyResponse.json();
            setPaymentStatus('success');
            
            if (onPaymentSuccess) {
              onPaymentSuccess({
                orderId: response.razorpay_order_id,
                paymentId: response.razorpay_payment_id,
                subtopicSlug,
                tierName,
                ...result
              });
            }
          } catch (err) {
            console.error('Payment verification error:', err);
            setPaymentStatus('error');
            setError('Payment verification failed. Please contact support.');
          }
        },
        prefill: {
          name: birthDetails.name || '',
          email: '',
          contact: ''
        },
        theme: {
          color: colors.teal.primary
        },
        modal: {
          ondismiss: function() {
            setIsLoading(false);
            setPaymentStatus('idle');
          }
        }
      };

      const rzp = new window.Razorpay(options);
      rzp.on('payment.failed', function(response) {
        console.error('Payment failed:', response.error);
        setPaymentStatus('error');
        setError(response.error.description || 'Payment failed. Please try again.');
        setIsLoading(false);
      });
      rzp.open();
    } catch (err) {
      console.error('Checkout error:', err);
      setPaymentStatus('error');
      setError(err.message || 'Something went wrong. Please try again.');
      setIsLoading(false);
    }
  }, [subtopicSlug, tierName, price, content, apiUrl, birthDetails, onPaymentSuccess]);

  return (
    <div 
      className="min-h-screen flex flex-col"
      style={{ background: colors.background.gradient }}
    >
      {/* Header */}
      <div className="px-5 pt-12 pb-6">
        <button 
          onClick={onBack}
          className="flex items-center gap-2 text-sm font-medium mb-6 transition-opacity hover:opacity-70"
          style={{ color: colors.gold.primary }}
          data-testid="checkout-back-btn"
        >
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          Back
        </button>
        
        <h1 
          className="text-2xl font-bold mb-2"
          style={{ color: colors.text.primary }}
        >
          Complete Your Purchase
        </h1>
        <p 
          className="text-sm"
          style={{ color: colors.text.muted }}
        >
          You&apos;re one step away from your personalized guidance
        </p>
      </div>

      {/* Order Summary Card */}
      <div 
        className="flex-1 px-5 pb-safe"
        style={{ paddingBottom: 'calc(env(safe-area-inset-bottom) + 120px)' }}
      >
        <div 
          className="rounded-2xl p-5"
          style={{ 
            background: colors.background.card,
            boxShadow: shadows.lg
          }}
        >
          {/* Package info */}
          <div className="flex items-start gap-4 mb-6">
            <div 
              className="w-14 h-14 rounded-xl flex items-center justify-center flex-shrink-0"
              style={{ 
                background: `linear-gradient(135deg, ${colors.gold.primary} 0%, ${colors.gold.light} 100%)` 
              }}
            >
              <svg className="w-7 h-7" fill="none" viewBox="0 0 24 24" stroke={colors.teal.dark}>
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
              </svg>
            </div>
            <div className="flex-1">
              <h3 
                className="text-lg font-bold mb-1"
                style={{ color: colors.text.dark }}
              >
                {content?.subTopic || 'Guidance Package'}
              </h3>
              <div className="flex items-center gap-2">
                <span 
                  className="px-2 py-0.5 rounded-full text-xs font-medium"
                  style={{ 
                    background: tierName === 'Supported' 
                      ? `linear-gradient(135deg, ${colors.gold.primary} 0%, ${colors.gold.light} 100%)`
                      : `${colors.teal.primary}15`,
                    color: tierName === 'Supported' ? colors.teal.dark : colors.teal.primary
                  }}
                >
                  {tierName}
                  {tierName === 'Supported' && ' • Recommended'}
                </span>
              </div>
            </div>
          </div>

          {/* Divider */}
          <div className="h-px mb-4" style={{ background: colors.ui.borderDark }} />

          {/* Order details */}
          <div className="space-y-3">
            <OrderItem label="Package" value={tierName} />
            <OrderItem label="Duration" value={`${duration} weeks`} />
            <OrderItem label="Category" value={content?.category || 'Guidance'} />
            <OrderItem label="Subtotal" value={formatPriceInr(price)} />
            <OrderItem label="Total" value={formatPriceInr(price)} isTotal />
          </div>

          {/* Refund guarantee */}
          <div 
            className="flex items-center gap-2 mt-6 p-3 rounded-xl"
            style={{ background: `${colors.ui.success}10` }}
          >
            <svg className="w-5 h-5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke={colors.ui.success}>
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
            </svg>
            <span 
              className="text-sm"
              style={{ color: colors.ui.success }}
            >
              100% satisfaction guaranteed
            </span>
          </div>

          {/* What's included */}
          <div className="mt-6">
            <h4 
              className="text-sm font-semibold mb-3"
              style={{ color: colors.text.dark }}
            >
              What&apos;s included
            </h4>
            <div className="space-y-2">
              {content?.featuresByTier?.[tierName]?.outcomes?.slice(0, 3).map((outcome, idx) => (
                <div key={idx} className="flex items-start gap-2">
                  <svg className="w-4 h-4 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke={colors.ui.success}>
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span 
                    className="text-xs"
                    style={{ color: colors.text.secondary }}
                  >
                    {outcome}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Error message */}
        {error && (
          <div 
            className="mt-4 p-4 rounded-xl flex items-start gap-3"
            style={{ 
              background: `${colors.ui.error}10`,
              border: `1px solid ${colors.ui.error}30`
            }}
          >
            <svg className="w-5 h-5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke={colors.ui.error}>
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div>
              <p 
                className="text-sm font-medium"
                style={{ color: colors.ui.error }}
              >
                Payment Error
              </p>
              <p 
                className="text-xs mt-1"
                style={{ color: colors.text.secondary }}
              >
                {error}
              </p>
            </div>
          </div>
        )}

        {/* Secure payment note */}
        <div className="flex items-center justify-center gap-2 mt-4">
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke={colors.text.muted}>
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
          </svg>
          <span 
            className="text-xs"
            style={{ color: colors.text.muted }}
          >
            Secure payment via Razorpay
          </span>
        </div>
      </div>

      {/* Fixed CTA */}
      <div 
        className="fixed bottom-0 left-0 right-0 p-5 border-t"
        style={{ 
          background: `linear-gradient(to top, ${colors.teal.dark} 0%, ${colors.teal.primary} 100%)`,
          borderColor: colors.ui.border,
          paddingBottom: 'calc(env(safe-area-inset-bottom) + 20px)'
        }}
      >
        <div className="flex items-center justify-between mb-3">
          <div>
            <p 
              className="text-xs"
              style={{ color: colors.text.muted }}
            >
              Total Amount
            </p>
            <p 
              className="text-xl font-bold"
              style={{ color: colors.text.primary }}
            >
              {formatPriceInr(price)}
            </p>
          </div>
          <button
            onClick={handlePayment}
            disabled={isLoading || paymentStatus === 'success'}
            className="px-8 py-3 rounded-xl font-semibold transition-all active:scale-[0.98] disabled:opacity-60"
            style={{
              background: colors.gold.primary,
              color: colors.text.dark,
              boxShadow: shadows.md
            }}
            data-testid="checkout-pay-btn"
          >
            {isLoading ? (
              <span className="flex items-center gap-2">
                <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
                Processing...
              </span>
            ) : paymentStatus === 'success' ? (
              '✓ Payment Complete'
            ) : (
              'Pay Now'
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
